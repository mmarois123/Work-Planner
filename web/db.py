#!/usr/bin/env python3
"""Work Planner — SQLite data access layer.

All database operations for areas, sections, tasks, subtasks, tags,
and recurrence rules. Uses WAL mode for concurrency.
"""

import json
import os
import re
import sqlite3
from datetime import date, datetime, timedelta

import yaml

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "data", "workplanner.db")

# Turso (cloud SQLite) configuration
TURSO_URL = os.environ.get("TURSO_DATABASE_URL")
TURSO_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")
USE_TURSO = bool(TURSO_URL and TURSO_TOKEN)

if USE_TURSO:
    import libsql_client

# ---------------------------------------------------------------------------
# Turso wrapper — makes libsql_client look like sqlite3
# ---------------------------------------------------------------------------

class _TursoCursor:
    """Wraps a libsql_client.ResultSet to behave like a sqlite3 Cursor."""

    def __init__(self, result):
        self._result = result
        self._rows = [r.asdict() for r in result.rows] if result.rows else []
        self.lastrowid = result.last_insert_rowid
        self.rowcount = result.rows_affected

    def fetchall(self):
        return list(self._rows)

    def fetchone(self):
        return self._rows[0] if self._rows else None


class _TursoConnection:
    """Wraps libsql_client.ClientSync to behave like a sqlite3 Connection.

    Rows are returned as plain dicts, so ``dict(row)`` and ``row["col"]``
    both work — identical to how the rest of db.py uses sqlite3.Row.
    """

    def __init__(self, url, auth_token):
        # Convert libsql:// to https:// for HTTP transport
        http_url = url.replace("libsql://", "https://")
        self._client = libsql_client.create_client_sync(
            url=http_url, auth_token=auth_token,
        )

    def execute(self, sql, params=None):
        args = list(params) if params else []
        rs = self._client.execute(sql, args)
        return _TursoCursor(rs)

    def batch(self, stmts):
        """Execute multiple SQL statements in a single HTTP round-trip.

        *stmts* is a list of (sql, params) tuples.  Returns a list of
        _TursoCursor objects, one per statement.
        """
        from libsql_client import InStatement
        batch = [InStatement(sql, list(params) if params else []) for sql, params in stmts]
        results = self._client.batch(batch)
        return [_TursoCursor(rs) for rs in results]

    def commit(self):
        pass  # libsql HTTP client auto-commits each statement

    def close(self):
        pass  # Keep client alive for reuse across requests


# Cached Turso client — reused across get_db() calls within the same process
_turso_conn = None

TABLES_ORDERED = ["areas", "sections", "tasks", "subtasks", "tags", "task_tags", "recurrence_rules"]

def sync_from_turso():
    """Pull all data from Turso cloud DB into local SQLite. One-time on startup."""
    if not TURSO_URL or not TURSO_TOKEN:
        return
    import libsql_client
    http_url = TURSO_URL.replace("libsql://", "https://")
    remote = libsql_client.create_client_sync(url=http_url, auth_token=TURSO_TOKEN)
    # Init local DB
    local = sqlite3.connect(DB_PATH)
    local.row_factory = sqlite3.Row
    local.execute("PRAGMA journal_mode=WAL")
    local.execute("PRAGMA foreign_keys=OFF")
    local.executescript(SCHEMA_SQL)
    # Clear and repopulate each table
    for table in TABLES_ORDERED:
        local.execute(f"DELETE FROM {table}")
    for table in TABLES_ORDERED:
        result = remote.execute(f"SELECT * FROM {table}")
        if not result.rows:
            continue
        cols = list(result.columns)
        placeholders = ",".join(["?"] * len(cols))
        col_names = ",".join(cols)
        local.executemany(f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})",
                          [tuple(r) for r in result.rows])
    local.execute("PRAGMA foreign_keys=ON")
    local.commit()
    local.close()
    remote.close()
    print(f"Synced from Turso -> local SQLite")

def push_to_turso():
    """Push local SQLite data to Turso cloud DB. Called on demand."""
    if not TURSO_URL or not TURSO_TOKEN:
        return
    import libsql_client
    remote = _TursoConnection(TURSO_URL, TURSO_TOKEN)
    local = sqlite3.connect(DB_PATH)
    local.row_factory = sqlite3.Row

    # Build all statements, then send in a single batch HTTP call
    stmts = []
    # Clear remote tables in reverse order (FK deps)
    for table in reversed(TABLES_ORDERED):
        stmts.append((f"DELETE FROM {table}", []))
    # Insert all rows
    for table in TABLES_ORDERED:
        rows = local.execute(f"SELECT * FROM {table}").fetchall()
        if not rows:
            continue
        cols = list(rows[0].keys())
        placeholders = ",".join(["?"] * len(cols))
        col_names = ",".join(cols)
        for row in rows:
            stmts.append((f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})",
                          [row[c] for c in cols]))
    remote.batch(stmts)
    local.close()
    remote.close()
    print(f"Pushed local SQLite -> Turso")


# ---------------------------------------------------------------------------
# Connection management
# ---------------------------------------------------------------------------

def get_db(path=None):
    """Return a database connection.

    If TURSO_DATABASE_URL and TURSO_AUTH_TOKEN env vars are set, connects
    to Turso cloud SQLite over HTTP. The Turso client is cached at module
    level so subsequent calls reuse the same HTTP connection.
    """
    global _turso_conn
    if USE_TURSO and path is None:
        if _turso_conn is None:
            _turso_conn = _TursoConnection(TURSO_URL, TURSO_TOKEN)
        return _turso_conn

    # Local SQLite fallback
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
    if USE_TURSO and path is None:
        # HTTP client doesn't support executescript; run statements individually
        for stmt in SCHEMA_SQL.split(';'):
            stmt = stmt.strip()
            if stmt:
                conn.execute(stmt)
    else:
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

CREATE INDEX IF NOT EXISTS idx_subtasks_task_id ON subtasks(task_id);
CREATE INDEX IF NOT EXISTS idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX IF NOT EXISTS idx_task_tags_tag_id ON task_tags(tag_id);
CREATE INDEX IF NOT EXISTS idx_recurrence_task_id ON recurrence_rules(task_id);
CREATE INDEX IF NOT EXISTS idx_tasks_section_id ON tasks(section_id);
CREATE INDEX IF NOT EXISTS idx_tasks_done_archived ON tasks(done, archived);
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
    if not tasks:
        return tasks

    task_ids = [t["id"] for t in tasks]
    placeholders = ",".join("?" * len(task_ids))

    # Use batch() on Turso to combine 3 queries into 1 HTTP round-trip
    if hasattr(conn, "batch"):
        cursors = conn.batch([
            (f"SELECT * FROM subtasks WHERE task_id IN ({placeholders}) ORDER BY position", task_ids),
            (f"""SELECT tt.task_id, t.id, t.name, t.color FROM tags t
                 JOIN task_tags tt ON tt.tag_id = t.id
                 WHERE tt.task_id IN ({placeholders})""", task_ids),
            (f"SELECT * FROM recurrence_rules WHERE task_id IN ({placeholders})", task_ids),
        ])
        all_subtasks = cursors[0].fetchall()
        all_tags = cursors[1].fetchall()
        all_recurrences = cursors[2].fetchall()
    else:
        all_subtasks = conn.execute(
            f"SELECT * FROM subtasks WHERE task_id IN ({placeholders}) ORDER BY position", task_ids
        ).fetchall()
        all_tags = conn.execute(
            f"""SELECT tt.task_id, t.id, t.name, t.color FROM tags t
                JOIN task_tags tt ON tt.tag_id = t.id
                WHERE tt.task_id IN ({placeholders})""", task_ids
        ).fetchall()
        all_recurrences = conn.execute(
            f"SELECT * FROM recurrence_rules WHERE task_id IN ({placeholders})", task_ids
        ).fetchall()

    # Group by task_id
    subtasks_by_tid = {}
    for s in all_subtasks:
        sd = dict(s)
        subtasks_by_tid.setdefault(sd["task_id"], []).append(sd)

    tags_by_tid = {}
    for t in all_tags:
        td = dict(t)
        tid = td.pop("task_id")
        tags_by_tid.setdefault(tid, []).append(td)

    rec_by_tid = {}
    for r in all_recurrences:
        rd = dict(r)
        rec_by_tid[rd["task_id"]] = rd

    for task in tasks:
        tid = task["id"]
        task["subtasks"] = subtasks_by_tid.get(tid, [])
        task["tags"] = tags_by_tid.get(tid, [])
        task["recurrence"] = rec_by_tid.get(tid, None)

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
# Analytics / Reporting
# ---------------------------------------------------------------------------

def get_tasks_completed_between(conn, start, end):
    """Return tasks completed in a date range (by completed_at)."""
    rows = conn.execute("""
        SELECT t.*, s.name AS section_name, a.key AS area_key, a.title AS area_title
        FROM tasks t
        JOIN sections s ON s.id = t.section_id
        JOIN areas a ON a.id = s.area_id
        WHERE t.done = 1 AND t.completed_at >= ? AND t.completed_at < ?
        ORDER BY t.completed_at DESC
    """, (start, end)).fetchall()
    return [dict(r) for r in rows]


def get_tasks_stale(conn, days=14):
    """Return open, non-archived tasks with no priority and no due date,
    older than `days` days."""
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    rows = conn.execute("""
        SELECT t.*, s.name AS section_name, a.key AS area_key, a.title AS area_title
        FROM tasks t
        JOIN sections s ON s.id = t.section_id
        JOIN areas a ON a.id = s.area_id
        WHERE t.done = 0 AND t.archived = 0
          AND t.priority IS NULL AND t.due_date IS NULL
          AND t.created_at < ?
        ORDER BY t.created_at ASC
    """, (cutoff,)).fetchall()
    return [dict(r) for r in rows]


def get_delegation_summary(conn):
    """Return delegated tasks grouped by person with counts."""
    rows = conn.execute("""
        SELECT t.delegated_to, COUNT(*) AS total,
               SUM(CASE WHEN t.done = 0 THEN 1 ELSE 0 END) AS open,
               SUM(CASE WHEN t.done = 1 THEN 1 ELSE 0 END) AS done
        FROM tasks t
        WHERE t.delegated_to IS NOT NULL AND t.archived = 0
        GROUP BY t.delegated_to
        ORDER BY open DESC
    """).fetchall()
    summary = []
    for r in rows:
        # Get individual open tasks for this person
        tasks = conn.execute("""
            SELECT t.id, t.title, t.due_date, t.priority, t.created_at,
                   s.name AS section_name, a.key AS area_key, a.title AS area_title
            FROM tasks t
            JOIN sections s ON s.id = t.section_id
            JOIN areas a ON a.id = s.area_id
            WHERE t.delegated_to = ? AND t.done = 0 AND t.archived = 0
            ORDER BY t.created_at ASC
        """, (r["delegated_to"],)).fetchall()
        summary.append({
            "person": r["delegated_to"],
            "total": r["total"],
            "open": r["open"],
            "done": r["done"],
            "tasks": [dict(t) for t in tasks],
        })
    return summary


def get_task_counts_by_section(conn, area_key=None):
    """Return open/done/priority counts per section, optionally filtered by area."""
    where = "WHERE t.archived = 0"
    params = []
    if area_key:
        where += " AND a.key = ?"
        params.append(area_key)

    rows = conn.execute(f"""
        SELECT a.key AS area_key, a.title AS area_title,
               s.name AS section_name,
               COUNT(*) AS total,
               SUM(CASE WHEN t.done = 0 THEN 1 ELSE 0 END) AS open,
               SUM(CASE WHEN t.done = 1 THEN 1 ELSE 0 END) AS done,
               SUM(CASE WHEN t.priority IS NOT NULL AND t.done = 0 THEN 1 ELSE 0 END) AS prioritized,
               SUM(CASE WHEN t.due_date IS NOT NULL AND t.done = 0 THEN 1 ELSE 0 END) AS has_due_date,
               SUM(CASE WHEN t.due_date < date('now') AND t.done = 0 THEN 1 ELSE 0 END) AS overdue
        FROM tasks t
        JOIN sections s ON s.id = t.section_id
        JOIN areas a ON a.id = s.area_id
        {where}
        GROUP BY a.key, s.name
        ORDER BY a.position, s.position
    """, params).fetchall()
    return [dict(r) for r in rows]


def get_velocity_metrics(conn, weeks=4):
    """Return tasks completed per week for the last N weeks."""
    results = []
    today = date.today()
    for i in range(weeks):
        week_end = today - timedelta(days=today.weekday()) - timedelta(weeks=i)
        week_start = week_end - timedelta(days=7)
        row = conn.execute("""
            SELECT COUNT(*) AS completed
            FROM tasks
            WHERE done = 1 AND completed_at >= ? AND completed_at < ?
        """, (week_start.isoformat(), week_end.isoformat())).fetchone()
        results.append({
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "completed": row["completed"],
        })
    results.reverse()
    return results


def get_unprioritized_tasks(conn, area_key=None):
    """Return open, non-archived tasks with no priority set."""
    where = "WHERE t.done = 0 AND t.archived = 0 AND t.priority IS NULL"
    params = []
    if area_key:
        where += " AND a.key = ?"
        params.append(area_key)

    rows = conn.execute(f"""
        SELECT t.*, s.name AS section_name, a.key AS area_key, a.title AS area_title
        FROM tasks t
        JOIN sections s ON s.id = t.section_id
        JOIN areas a ON a.id = s.area_id
        {where}
        ORDER BY a.position, s.position, t.position
    """, params).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Markdown parsing (shared with migrate.py)
# ---------------------------------------------------------------------------

TASK_RE = re.compile(r"^- \[([ x])\] (.+)$")
DELEGATED_RE = re.compile(r"@delegated\(([^)]+)\)")


def parse_markdown_file(filepath):
    """Parse a markdown task file into sections with tasks.

    Returns list of {"name": str, "tasks": [{"text": str, "done": bool, "delegated_to": str|None}]}
    """
    if not os.path.exists(filepath):
        return []

    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    sections = []
    current_section = None

    for raw_line in lines:
        line = raw_line.rstrip("\n")

        # H2 section header
        if line.startswith("## "):
            current_section = {"name": line[3:].strip(), "tasks": []}
            sections.append(current_section)
            continue

        # Task line
        m = TASK_RE.match(line)
        if m and current_section is not None:
            done = m.group(1) == "x"
            text = m.group(2).strip()
            delegated_to = None
            dm = DELEGATED_RE.search(text)
            if dm:
                delegated_to = dm.group(1)
                text = DELEGATED_RE.sub("", text).strip()
            current_section["tasks"].append({
                "text": text,
                "done": done,
                "delegated_to": delegated_to,
            })

    return sections


# ---------------------------------------------------------------------------
# Bidirectional sync: Markdown <-> SQLite
# ---------------------------------------------------------------------------

def sync_tasks(conn):
    """Bidirectional sync between markdown files and SQLite database.

    Reconciliation rules (per area+section, matched by title):
    - [x] in md but done=0 in DB -> mark done in DB
    - [ ] in md but done=1 in DB -> DB wins (md will be rewritten)
    - Task in md but not in DB -> create in DB
    - Task in DB but not in md -> added during md rewrite

    After reconciliation, rewrites each md file from DB state.

    Returns dict with counts of changes made.
    """
    config_path = os.path.join(PROJECT_ROOT, "config.yaml")
    tasks_dir = os.path.join(PROJECT_ROOT, "tasks")

    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    areas_config = config["areas"]
    changes = {"md_to_db": 0, "db_to_md": 0, "created_in_db": 0, "created_in_md": 0}

    for area_key, area_info in areas_config.items():
        filepath = os.path.join(tasks_dir, area_info["file"])

        # Get area from DB
        area_row = conn.execute(
            "SELECT id FROM areas WHERE key = ?", (area_key,)
        ).fetchone()
        if not area_row:
            continue
        area_id = area_row["id"]

        # Parse markdown file
        md_sections = parse_markdown_file(filepath)
        md_map = {}
        for s in md_sections:
            md_map[s["name"].lower()] = s

        # Get all DB sections for this area
        db_sections = conn.execute(
            "SELECT * FROM sections WHERE area_id = ? ORDER BY position",
            (area_id,)
        ).fetchall()

        for db_section in db_sections:
            section_name = db_section["name"]
            section_id = db_section["id"]

            # Get DB tasks for this section (non-archived)
            db_tasks = conn.execute(
                "SELECT * FROM tasks WHERE section_id = ? AND archived = 0 ORDER BY position",
                (section_id,)
            ).fetchall()

            # Build DB task index by title
            db_by_title = {}
            for t in db_tasks:
                db_by_title[t["title"]] = t

            # Get md tasks for this section
            md_section = md_map.get(section_name.lower(), {"tasks": []})
            md_tasks = md_section.get("tasks", [])

            # Build md task set by text
            md_by_title = {}
            for t in md_tasks:
                md_by_title[t["text"]] = t

            # Compare md tasks against DB
            for md_task in md_tasks:
                title = md_task["text"]
                if title in db_by_title:
                    db_task = db_by_title[title]
                    md_done = md_task["done"]
                    db_done = bool(db_task["done"])

                    if md_done and not db_done:
                        # MD says done, DB says not -> update DB
                        conn.execute(
                            "UPDATE tasks SET done = 1, completed_at = ? WHERE id = ?",
                            (datetime.now().isoformat(), db_task["id"])
                        )
                        changes["md_to_db"] += 1
                    elif not md_done and db_done:
                        # DB says done, MD says not -> DB wins, reflected in rewrite
                        changes["db_to_md"] += 1

                    # Sync delegated_to from md if changed
                    if md_task["delegated_to"] != db_task["delegated_to"]:
                        conn.execute(
                            "UPDATE tasks SET delegated_to = ? WHERE id = ?",
                            (md_task["delegated_to"], db_task["id"])
                        )
                else:
                    # Task in md but not in DB -> create in DB
                    row = conn.execute(
                        "SELECT COALESCE(MAX(position), -1) + 1 AS pos FROM tasks WHERE section_id = ?",
                        (section_id,)
                    ).fetchone()
                    conn.execute("""
                        INSERT INTO tasks (section_id, title, done, delegated_to, position, completed_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        section_id,
                        title,
                        1 if md_task["done"] else 0,
                        md_task["delegated_to"],
                        row["pos"],
                        datetime.now().isoformat() if md_task["done"] else None,
                    ))
                    changes["created_in_db"] += 1

            # Count tasks in DB but not in md
            for title in db_by_title:
                if title not in md_by_title:
                    changes["created_in_md"] += 1

        conn.commit()

        # Rewrite markdown file from DB state
        _rewrite_markdown_file(conn, area_id, filepath)

    return changes


def _rewrite_markdown_file(conn, area_id, filepath):
    """Rewrite a markdown file from current DB state."""
    area_row = conn.execute(
        "SELECT title FROM areas WHERE id = ?", (area_id,)
    ).fetchone()
    area_title = area_row["title"] if area_row else "Unknown"

    db_sections = conn.execute(
        "SELECT * FROM sections WHERE area_id = ? ORDER BY position",
        (area_id,)
    ).fetchall()

    lines = [f"# {area_title}", ""]

    for section in db_sections:
        lines.append(f"## {section['name']}")

        tasks = conn.execute(
            "SELECT * FROM tasks WHERE section_id = ? AND archived = 0 "
            "ORDER BY done ASC, position ASC, id ASC",
            (section["id"],)
        ).fetchall()

        for task in tasks:
            mark = "x" if task["done"] else " "
            text = task["title"]
            if task["delegated_to"]:
                text += f" @delegated({task['delegated_to']})"
            lines.append(f"- [{mark}] {text}")

        lines.append("")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


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
    elif len(sys.argv) > 1 and sys.argv[1] == "--summary-json":
        init_db()
        conn = get_db()
        # Build a structured JSON summary with stats
        total_open = conn.execute(
            "SELECT COUNT(*) AS c FROM tasks WHERE done=0 AND archived=0"
        ).fetchone()["c"]
        total_done = conn.execute(
            "SELECT COUNT(*) AS c FROM tasks WHERE done=1 AND archived=0"
        ).fetchone()["c"]
        total_prioritized = conn.execute(
            "SELECT COUNT(*) AS c FROM tasks WHERE done=0 AND archived=0 AND priority IS NOT NULL"
        ).fetchone()["c"]
        total_with_due = conn.execute(
            "SELECT COUNT(*) AS c FROM tasks WHERE done=0 AND archived=0 AND due_date IS NOT NULL"
        ).fetchone()["c"]
        total_delegated = conn.execute(
            "SELECT COUNT(*) AS c FROM tasks WHERE delegated_to IS NOT NULL AND archived=0 AND done=0"
        ).fetchone()["c"]
        overdue = get_tasks_overdue(conn)
        sections = get_task_counts_by_section(conn)
        summary = {
            "stats": {
                "open": total_open,
                "done_unarchived": total_done,
                "prioritized": total_prioritized,
                "with_due_date": total_with_due,
                "delegated": total_delegated,
                "overdue": len(overdue),
            },
            "sections": sections,
            "overdue": [{"id": t["id"], "title": t["title"], "due_date": t["due_date"],
                         "area_key": t["area_key"], "section_name": t["section_name"]}
                        for t in overdue],
        }
        print(json.dumps(summary, indent=2))
        conn.close()
    elif len(sys.argv) > 1 and sys.argv[1] == "--init":
        init_db()
        print(f"Database initialized at {DB_PATH}")
    else:
        print("Usage: python web/db.py [--init | --summary-text | --summary-json]")
