#!/usr/bin/env python3
"""Work Planner — SQLite data access layer.

All database operations for areas, sections, tasks, subtasks, tags,
and recurrence rules. Uses WAL mode for concurrency.
"""

import os
import sqlite3
from datetime import date, datetime, timedelta

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "data", "workplanner.db")

# ---------------------------------------------------------------------------
# Connection management
# ---------------------------------------------------------------------------

def get_db(path=None):
    """Return a SQLite connection with WAL mode and foreign keys enabled."""
    db_path = path or DB_PATH
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(path=None):
    """Create all tables if they don't exist."""
    conn = get_db(path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS areas (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    key         TEXT    NOT NULL UNIQUE,
    title       TEXT    NOT NULL,
    position    INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS sections (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    area_id     INTEGER NOT NULL REFERENCES areas(id),
    name        TEXT    NOT NULL,
    position    INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tasks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id      INTEGER NOT NULL REFERENCES sections(id),
    title           TEXT    NOT NULL,
    description     TEXT    DEFAULT '',
    done            INTEGER NOT NULL DEFAULT 0,
    priority        INTEGER DEFAULT NULL,
    due_date        TEXT    DEFAULT NULL,
    delegated_to    TEXT    DEFAULT NULL,
    position        INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    completed_at    TEXT    DEFAULT NULL,
    archived        INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS subtasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id     INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    title       TEXT    NOT NULL,
    done        INTEGER NOT NULL DEFAULT 0,
    position    INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tags (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT    NOT NULL UNIQUE,
    color   TEXT    NOT NULL DEFAULT '#6b7280'
);

CREATE TABLE IF NOT EXISTS task_tags (
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id  INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);

CREATE TABLE IF NOT EXISTS recurrence_rules (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id         INTEGER NOT NULL UNIQUE REFERENCES tasks(id) ON DELETE CASCADE,
    pattern         TEXT    NOT NULL,
    interval        INTEGER NOT NULL DEFAULT 1,
    days_of_week    TEXT    DEFAULT NULL,
    next_due        TEXT    DEFAULT NULL
);
"""

# ---------------------------------------------------------------------------
# Areas & Sections
# ---------------------------------------------------------------------------

def get_all_areas(conn):
    """Return all areas with their sections."""
    areas = conn.execute("SELECT * FROM areas ORDER BY position").fetchall()
    result = []
    for area in areas:
        sections = conn.execute(
            "SELECT * FROM sections WHERE area_id = ? ORDER BY position",
            (area["id"],)
        ).fetchall()
        result.append({
            "id": area["id"],
            "key": area["key"],
            "title": area["title"],
            "position": area["position"],
            "sections": [dict(s) for s in sections],
        })
    return result


def get_section_id(conn, area_key, section_name):
    """Look up section ID by area key and section name (case-insensitive)."""
    row = conn.execute("""
        SELECT s.id FROM sections s
        JOIN areas a ON a.id = s.area_id
        WHERE a.key = ? AND LOWER(s.name) = LOWER(?)
    """, (area_key, section_name)).fetchone()
    return row["id"] if row else None


# ---------------------------------------------------------------------------
# Tasks CRUD
# ---------------------------------------------------------------------------

def _task_row_to_dict(row):
    """Convert a task Row to a dict."""
    return dict(row)


def _enrich_tasks(conn, tasks):
    """Add subtasks, tags, and recurrence to a list of task dicts."""
    for task in tasks:
        tid = task["id"]
        # Subtasks
        task["subtasks"] = [dict(s) for s in conn.execute(
            "SELECT * FROM subtasks WHERE task_id = ? ORDER BY position", (tid,)
        ).fetchall()]
        # Tags
        task["tags"] = [dict(t) for t in conn.execute("""
            SELECT t.id, t.name, t.color FROM tags t
            JOIN task_tags tt ON tt.tag_id = t.id
            WHERE tt.task_id = ?
        """, (tid,)).fetchall()]
        # Recurrence
        rec = conn.execute(
            "SELECT * FROM recurrence_rules WHERE task_id = ?", (tid,)
        ).fetchone()
        task["recurrence"] = dict(rec) if rec else None
    return tasks


def get_all_tasks(conn, include_archived=False):
    """Return all tasks grouped by area > section, like the old API shape."""
    areas = get_all_areas(conn)
    for area in areas:
        for section in area["sections"]:
            where = "WHERE t.section_id = ?"
            if not include_archived:
                where += " AND t.archived = 0"
            rows = conn.execute(f"""
                SELECT t.* FROM tasks t
                {where}
                ORDER BY t.done ASC, t.position ASC, t.id ASC
            """, (section["id"],)).fetchall()
            tasks = [dict(r) for r in rows]
            _enrich_tasks(conn, tasks)
            section["tasks"] = tasks
    return areas


def get_task(conn, task_id):
    """Return a single task with subtasks, tags, recurrence."""
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not row:
        return None
    task = dict(row)
    _enrich_tasks(conn, [task])
    # Also include area/section info
    section = conn.execute("SELECT * FROM sections WHERE id = ?", (task["section_id"],)).fetchone()
    if section:
        area = conn.execute("SELECT * FROM areas WHERE id = ?", (section["area_id"],)).fetchone()
        task["section_name"] = section["name"]
        task["area_key"] = area["key"] if area else None
        task["area_title"] = area["title"] if area else None
    return task


def create_task(conn, section_id, title, description="", priority=None,
                due_date=None, delegated_to=None):
    """Insert a new task, return its id."""
    # Get next position
    row = conn.execute(
        "SELECT COALESCE(MAX(position), -1) + 1 AS pos FROM tasks WHERE section_id = ?",
        (section_id,)
    ).fetchone()
    pos = row["pos"]

    cur = conn.execute("""
        INSERT INTO tasks (section_id, title, description, priority, due_date,
                           delegated_to, position)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (section_id, title, description, priority, due_date, delegated_to, pos))
    conn.commit()
    return cur.lastrowid


def update_task(conn, task_id, **fields):
    """Update arbitrary fields on a task. Returns True if found."""
    allowed = {"title", "description", "done", "priority", "due_date",
               "delegated_to", "position", "archived", "section_id"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return False

    # Handle done transition
    if "done" in updates:
        current = conn.execute("SELECT done FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if current and current["done"] == 0 and updates["done"] == 1:
            updates["completed_at"] = datetime.now().isoformat()
        elif current and current["done"] == 1 and updates["done"] == 0:
            updates["completed_at"] = None

    sets = ", ".join(f"{k} = ?" for k in updates)
    vals = list(updates.values()) + [task_id]
    conn.execute(f"UPDATE tasks SET {sets} WHERE id = ?", vals)
    conn.commit()
    return True


def toggle_task(conn, task_id):
    """Toggle done status. Returns the new done state, or None if not found."""
    row = conn.execute("SELECT done FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not row:
        return None
    new_done = 0 if row["done"] else 1
    completed_at = datetime.now().isoformat() if new_done else None
    conn.execute(
        "UPDATE tasks SET done = ?, completed_at = ? WHERE id = ?",
        (new_done, completed_at, task_id)
    )
    conn.commit()
    return new_done


def delete_task(conn, task_id):
    """Hard delete a task (cascades to subtasks, tags, recurrence)."""
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()


def archive_completed(conn):
    """Set archived=1 on all done, non-archived tasks. Returns count."""
    cur = conn.execute(
        "UPDATE tasks SET archived = 1 WHERE done = 1 AND archived = 0"
    )
    conn.commit()
    return cur.rowcount


# ---------------------------------------------------------------------------
# Subtasks
# ---------------------------------------------------------------------------

def create_subtask(conn, task_id, title):
    """Add a subtask. Returns its id."""
    row = conn.execute(
        "SELECT COALESCE(MAX(position), -1) + 1 AS pos FROM subtasks WHERE task_id = ?",
        (task_id,)
    ).fetchone()
    cur = conn.execute(
        "INSERT INTO subtasks (task_id, title, position) VALUES (?, ?, ?)",
        (task_id, title, row["pos"])
    )
    conn.commit()
    return cur.lastrowid


def toggle_subtask(conn, subtask_id):
    """Toggle a subtask's done status. Returns new done state."""
    row = conn.execute("SELECT done FROM subtasks WHERE id = ?", (subtask_id,)).fetchone()
    if not row:
        return None
    new_done = 0 if row["done"] else 1
    conn.execute("UPDATE subtasks SET done = ?, id = id WHERE id = ?", (new_done, subtask_id))
    conn.commit()
    return new_done


def update_subtask(conn, subtask_id, **fields):
    """Update subtask fields (title, done, position)."""
    allowed = {"title", "done", "position"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return False
    sets = ", ".join(f"{k} = ?" for k in updates)
    vals = list(updates.values()) + [subtask_id]
    conn.execute(f"UPDATE subtasks SET {sets} WHERE id = ?", vals)
    conn.commit()
    return True


def delete_subtask(conn, subtask_id):
    """Delete a subtask."""
    conn.execute("DELETE FROM subtasks WHERE id = ?", (subtask_id,))
    conn.commit()


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------

def get_all_tags(conn):
    """Return all tags."""
    return [dict(r) for r in conn.execute("SELECT * FROM tags ORDER BY name").fetchall()]


def create_tag(conn, name, color="#6b7280"):
    """Create a tag. Returns its id."""
    cur = conn.execute("INSERT INTO tags (name, color) VALUES (?, ?)", (name, color))
    conn.commit()
    return cur.lastrowid


def update_tag(conn, tag_id, **fields):
    """Update tag name/color."""
    allowed = {"name", "color"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return False
    sets = ", ".join(f"{k} = ?" for k in updates)
    vals = list(updates.values()) + [tag_id]
    conn.execute(f"UPDATE tags SET {sets} WHERE id = ?", vals)
    conn.commit()
    return True


def delete_tag(conn, tag_id):
    """Delete a tag (cascades from task_tags)."""
    conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
    conn.commit()


def add_tag_to_task(conn, task_id, tag_id):
    """Assign a tag to a task."""
    conn.execute(
        "INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)",
        (task_id, tag_id)
    )
    conn.commit()


def remove_tag_from_task(conn, task_id, tag_id):
    """Remove a tag from a task."""
    conn.execute(
        "DELETE FROM task_tags WHERE task_id = ? AND tag_id = ?",
        (task_id, tag_id)
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Due dates
# ---------------------------------------------------------------------------

def get_tasks_due_today(conn):
    """Return non-archived tasks due today."""
    today = date.today().isoformat()
    rows = conn.execute("""
        SELECT t.*, s.name AS section_name, a.key AS area_key, a.title AS area_title
        FROM tasks t
        JOIN sections s ON s.id = t.section_id
        JOIN areas a ON a.id = s.area_id
        WHERE t.due_date = ? AND t.archived = 0
        ORDER BY t.priority ASC NULLS LAST, t.position
    """, (today,)).fetchall()
    tasks = [dict(r) for r in rows]
    return _enrich_tasks(conn, tasks)


def get_tasks_overdue(conn):
    """Return non-archived, undone tasks with due_date before today."""
    today = date.today().isoformat()
    rows = conn.execute("""
        SELECT t.*, s.name AS section_name, a.key AS area_key, a.title AS area_title
        FROM tasks t
        JOIN sections s ON s.id = t.section_id
        JOIN areas a ON a.id = s.area_id
        WHERE t.due_date < ? AND t.done = 0 AND t.archived = 0
        ORDER BY t.due_date ASC, t.priority ASC NULLS LAST
    """, (today,)).fetchall()
    tasks = [dict(r) for r in rows]
    return _enrich_tasks(conn, tasks)


def get_tasks_upcoming(conn, days=7):
    """Return non-archived tasks due within `days` from today."""
    today = date.today()
    end = (today + timedelta(days=days)).isoformat()
    rows = conn.execute("""
        SELECT t.*, s.name AS section_name, a.key AS area_key, a.title AS area_title
        FROM tasks t
        JOIN sections s ON s.id = t.section_id
        JOIN areas a ON a.id = s.area_id
        WHERE t.due_date >= ? AND t.due_date <= ? AND t.archived = 0
        ORDER BY t.due_date ASC, t.priority ASC NULLS LAST
    """, (today.isoformat(), end)).fetchall()
    tasks = [dict(r) for r in rows]
    return _enrich_tasks(conn, tasks)


def get_tasks_calendar(conn, start_date, end_date):
    """Return non-archived tasks in a date range for calendar view."""
    rows = conn.execute("""
        SELECT t.*, s.name AS section_name, a.key AS area_key, a.title AS area_title
        FROM tasks t
        JOIN sections s ON s.id = t.section_id
        JOIN areas a ON a.id = s.area_id
        WHERE t.due_date >= ? AND t.due_date <= ? AND t.archived = 0
        ORDER BY t.due_date ASC, t.priority ASC NULLS LAST
    """, (start_date, end_date)).fetchall()
    tasks = [dict(r) for r in rows]
    return _enrich_tasks(conn, tasks)


def get_tasks_no_due_date(conn):
    """Return non-archived, undone tasks with no due date."""
    rows = conn.execute("""
        SELECT t.*, s.name AS section_name, a.key AS area_key, a.title AS area_title
        FROM tasks t
        JOIN sections s ON s.id = t.section_id
        JOIN areas a ON a.id = s.area_id
        WHERE t.due_date IS NULL AND t.done = 0 AND t.archived = 0
        ORDER BY a.position, s.position, t.position
    """).fetchall()
    tasks = [dict(r) for r in rows]
    return _enrich_tasks(conn, tasks)


# ---------------------------------------------------------------------------
# Recurrence
# ---------------------------------------------------------------------------

def set_recurrence(conn, task_id, pattern, interval=1, days_of_week=None, next_due=None):
    """Set or update recurrence rule for a task."""
    existing = conn.execute(
        "SELECT id FROM recurrence_rules WHERE task_id = ?", (task_id,)
    ).fetchone()
    if existing:
        conn.execute("""
            UPDATE recurrence_rules
            SET pattern = ?, interval = ?, days_of_week = ?, next_due = ?
            WHERE task_id = ?
        """, (pattern, interval, days_of_week, next_due, task_id))
    else:
        conn.execute("""
            INSERT INTO recurrence_rules (task_id, pattern, interval, days_of_week, next_due)
            VALUES (?, ?, ?, ?, ?)
        """, (task_id, pattern, interval, days_of_week, next_due))
    conn.commit()


def remove_recurrence(conn, task_id):
    """Remove recurrence rule from a task."""
    conn.execute("DELETE FROM recurrence_rules WHERE task_id = ?", (task_id,))
    conn.commit()


def calculate_next_due(pattern, interval, days_of_week, from_date=None):
    """Calculate the next due date based on recurrence pattern.

    Args:
        pattern: 'daily', 'weekly', 'biweekly', 'monthly', 'quarterly', 'yearly'
        interval: multiplier (e.g. 2 = every 2 weeks)
        days_of_week: comma-separated day numbers (0=Mon..6=Sun) for weekly
        from_date: starting date (defaults to today)

    Returns:
        date object for next occurrence
    """
    if from_date is None:
        from_date = date.today()
    elif isinstance(from_date, str):
        from_date = date.fromisoformat(from_date)

    if pattern == "daily":
        return from_date + timedelta(days=interval)

    elif pattern == "weekly":
        if days_of_week:
            target_days = sorted(int(d) for d in days_of_week.split(","))
            current_dow = from_date.weekday()
            # Find next day in this week
            for d in target_days:
                if d > current_dow:
                    return from_date + timedelta(days=(d - current_dow))
            # Wrap to next week
            return from_date + timedelta(days=(7 - current_dow + target_days[0]))
        return from_date + timedelta(weeks=interval)

    elif pattern == "biweekly":
        return from_date + timedelta(weeks=2)

    elif pattern == "monthly":
        try:
            from dateutil.relativedelta import relativedelta
            return from_date + relativedelta(months=interval)
        except ImportError:
            # Fallback: approximate
            return from_date + timedelta(days=30 * interval)

    elif pattern == "quarterly":
        try:
            from dateutil.relativedelta import relativedelta
            return from_date + relativedelta(months=3)
        except ImportError:
            return from_date + timedelta(days=91)

    elif pattern == "yearly":
        try:
            from dateutil.relativedelta import relativedelta
            return from_date + relativedelta(years=interval)
        except ImportError:
            return from_date + timedelta(days=365 * interval)

    return from_date + timedelta(days=7)


def complete_recurring_task(conn, task_id):
    """Complete a recurring task: archive it and create a new instance.

    Returns the new task's id, or None if task has no recurrence.
    """
    task = get_task(conn, task_id)
    if not task or not task.get("recurrence"):
        return None

    rec = task["recurrence"]

    # Archive the current task
    conn.execute(
        "UPDATE tasks SET done = 1, archived = 1, completed_at = ? WHERE id = ?",
        (datetime.now().isoformat(), task_id)
    )

    # Calculate next due
    next_due = calculate_next_due(
        rec["pattern"], rec["interval"], rec["days_of_week"],
        task.get("due_date")
    )

    # Create new task instance
    row = conn.execute(
        "SELECT COALESCE(MAX(position), -1) + 1 AS pos FROM tasks WHERE section_id = ?",
        (task["section_id"],)
    ).fetchone()

    cur = conn.execute("""
        INSERT INTO tasks (section_id, title, description, priority, due_date,
                           delegated_to, position)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (task["section_id"], task["title"], task["description"],
          task["priority"], next_due.isoformat(), task["delegated_to"], row["pos"]))
    new_id = cur.lastrowid

    # Copy recurrence rule to new task
    conn.execute("""
        INSERT INTO recurrence_rules (task_id, pattern, interval, days_of_week, next_due)
        VALUES (?, ?, ?, ?, ?)
    """, (new_id, rec["pattern"], rec["interval"], rec["days_of_week"],
          next_due.isoformat()))

    # Copy tags
    for tag in task.get("tags", []):
        conn.execute(
            "INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)",
            (new_id, tag["id"])
        )

    conn.commit()
    return new_id


# ---------------------------------------------------------------------------
# Bulk / Summary
# ---------------------------------------------------------------------------

def bulk_create_tasks(conn, tasks_list):
    """Bulk create tasks from a list of dicts.

    Each dict must have: area_key, section, text
    Optional: priority, due_date, delegated_to, description

    Returns count of tasks created.
    """
    count = 0
    for t in tasks_list:
        section_id = get_section_id(conn, t["area_key"], t["section"])
        if not section_id:
            continue
        create_task(
            conn, section_id, t["text"],
            description=t.get("description", ""),
            priority=t.get("priority"),
            due_date=t.get("due_date"),
            delegated_to=t.get("delegated_to"),
        )
        count += 1
    return count


def get_tasks_for_summary(conn):
    """Return formatted text of all open tasks for AI summary."""
    areas = get_all_tasks(conn)
    lines = []
    for area in areas:
        lines.append(f"# {area['title']}")
        lines.append("")
        for section in area["sections"]:
            lines.append(f"## {section['name']}")
            for task in section["tasks"]:
                mark = "x" if task["done"] else " "
                text = task["title"]
                if task.get("delegated_to"):
                    text += f" @delegated({task['delegated_to']})"
                if task.get("due_date"):
                    text += f" [due: {task['due_date']}]"
                if task.get("priority"):
                    text += f" [P{task['priority']}]"
                lines.append(f"- [{mark}] {text}")
            lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--summary-text":
        init_db()
        conn = get_db()
        print(get_tasks_for_summary(conn))
        conn.close()
    elif len(sys.argv) > 1 and sys.argv[1] == "--init":
        init_db()
        print(f"Database initialized at {DB_PATH}")
    else:
        print("Usage: python web/db.py [--init | --summary-text]")
