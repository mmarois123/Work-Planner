#!/usr/bin/env python3
"""Work Planner — Flask API server.

All data stored in SQLite via db.py. Start with: python3 web/server.py
"""

import os
import shutil
import subprocess
from datetime import datetime

from flask import Flask, jsonify, request, send_from_directory

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import (
    get_db, init_db,
    get_all_areas, get_all_tasks, get_task, get_section_id,
    create_task, update_task, toggle_task, delete_task, archive_completed,
    create_subtask, toggle_subtask, update_subtask, delete_subtask,
    get_all_tags, create_tag, update_tag, delete_tag,
    add_tag_to_task, remove_tag_from_task,
    get_tasks_due_today, get_tasks_overdue, get_tasks_upcoming,
    get_tasks_calendar, get_tasks_no_due_date,
    set_recurrence, remove_recurrence, complete_recurring_task,
    get_tasks_for_summary, bulk_create_tasks,
    sync_tasks,
    get_tasks_completed_between, get_tasks_stale, get_delegation_summary,
    get_task_counts_by_section, get_velocity_metrics, get_unprioritized_tasks,
)
from inbox import check_claude_available, process_inbox

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

app = Flask(__name__)

DISPLAY_NAMES = {
    "sunbelt": "Sunbelt FP&A",
    "app": "Planyfi — App",
    "marketing": "Planyfi — Marketing",
    "personal": "Personal",
}

# Cloud / auth configuration
WP_AUTH_PIN = os.environ.get("WP_AUTH_PIN")
SKIP_INIT_DB = os.environ.get("SKIP_INIT_DB")
IS_CLOUD = bool(os.environ.get("TURSO_DATABASE_URL"))

# Init DB (skip on Vercel where schema already exists in Turso)
if not SKIP_INIT_DB:
    init_db()

# Sync markdown <-> DB on startup (local only — no filesystem on Vercel)
if not IS_CLOUD:
    try:
        _conn = get_db()
        _sync_result = sync_tasks(_conn)
        _conn.close()
        _total = sum(_sync_result.values())
        if _total:
            print(f"Startup sync: {_sync_result}")
    except Exception as e:
        print(f"Startup sync failed: {e}")


# ---------------------------------------------------------------------------
# Auth middleware
# ---------------------------------------------------------------------------

@app.before_request
def check_auth():
    """Require PIN auth for API routes when WP_AUTH_PIN is set."""
    if not WP_AUTH_PIN:
        return  # No PIN configured, skip auth

    # Exempt paths
    if request.path in ('/api/login', '/api/health'):
        return

    # Only protect API routes
    if not request.path.startswith('/api/'):
        return

    # Check auth cookie
    if request.cookies.get('wp_auth') == WP_AUTH_PIN:
        return

    # Check header (localStorage backup)
    if request.headers.get('X-Auth-PIN') == WP_AUTH_PIN:
        return

    return jsonify({"error": "Unauthorized"}), 401


@app.route("/api/login", methods=["POST"])
def api_login():
    """Validate PIN and set auth cookie."""
    data = request.get_json() or {}
    pin = data.get("pin", "")
    if not WP_AUTH_PIN or pin == WP_AUTH_PIN:
        resp = jsonify({"ok": True})
        resp.set_cookie(
            'wp_auth', WP_AUTH_PIN or '',
            max_age=30 * 24 * 3600,
            httponly=True,
            samesite='Lax',
        )
        return resp
    return jsonify({"error": "Invalid PIN"}), 401


@app.route("/api/health")
def api_health():
    """Health check (exempt from auth)."""
    return jsonify({"ok": True, "mode": "cloud" if IS_CLOUD else "local"})

# ---------------------------------------------------------------------------
# Routes — static
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(SCRIPT_DIR, "index.html")


# ---------------------------------------------------------------------------
# Routes — Config
# ---------------------------------------------------------------------------

@app.route("/api/config")
def api_config():
    conn = get_db()
    areas = get_all_areas(conn)
    conn.close()
    result = {}
    for area in areas:
        result[area["key"]] = {
            "title": area["title"],
            "sections": [s["name"] for s in area["sections"]],
        }
    return jsonify(result)


# ---------------------------------------------------------------------------
# Routes — Tasks
# ---------------------------------------------------------------------------

@app.route("/api/tasks")
def api_tasks_all():
    conn = get_db()
    areas = get_all_tasks(conn)
    conn.close()
    return jsonify({"areas": areas})


@app.route("/api/tasks/bulk", methods=["POST"])
def api_bulk_tasks():
    """Bulk create tasks (for AI inbox)."""
    data = request.get_json()
    tasks = (data or {}).get("tasks", [])
    if not tasks:
        return jsonify({"error": "tasks array is required"}), 400
    conn = get_db()
    count = bulk_create_tasks(conn, tasks)
    conn.close()
    return jsonify({"ok": True, "added": count}), 201


@app.route("/api/tasks/due/today")
def api_tasks_due_today():
    conn = get_db()
    tasks = get_tasks_due_today(conn)
    conn.close()
    return jsonify({"tasks": tasks})


@app.route("/api/tasks/due/overdue")
def api_tasks_due_overdue():
    conn = get_db()
    tasks = get_tasks_overdue(conn)
    conn.close()
    return jsonify({"tasks": tasks})


@app.route("/api/tasks/due/upcoming")
def api_tasks_due_upcoming():
    days = request.args.get("days", 7, type=int)
    conn = get_db()
    tasks = get_tasks_upcoming(conn, days=days)
    conn.close()
    return jsonify({"tasks": tasks})


@app.route("/api/tasks/due/calendar")
def api_tasks_due_calendar():
    start = request.args.get("start")
    end = request.args.get("end")
    if not start or not end:
        return jsonify({"error": "start and end query params required"}), 400
    conn = get_db()
    tasks = get_tasks_calendar(conn, start, end)
    conn.close()
    return jsonify({"tasks": tasks})


@app.route("/api/tasks/due/no-date")
def api_tasks_no_due_date():
    conn = get_db()
    tasks = get_tasks_no_due_date(conn)
    conn.close()
    return jsonify({"tasks": tasks})


@app.route("/api/tasks/<area_key>", methods=["POST"])
def api_add_task(area_key):
    """Add a task to a section within an area."""
    data = request.get_json()
    section_name = (data or {}).get("section", "").strip()
    text = (data or {}).get("text", "").strip()
    if not section_name or not text:
        return jsonify({"error": "section and text are required"}), 400

    conn = get_db()
    section_id = get_section_id(conn, area_key, section_name)
    if not section_id:
        conn.close()
        return jsonify({"error": f"Section '{section_name}' not found in '{area_key}'"}), 404

    task_id = create_task(
        conn, section_id, text,
        description=data.get("description", ""),
        priority=data.get("priority"),
        due_date=data.get("due_date"),
        delegated_to=data.get("delegated_to"),
    )
    conn.close()
    return jsonify({"ok": True, "id": task_id, "text": text}), 201


@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def api_get_task(task_id):
    """Get full task detail with subtasks, tags, recurrence."""
    conn = get_db()
    task = get_task(conn, task_id)
    conn.close()
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)


@app.route("/api/tasks/<int:task_id>", methods=["PATCH"])
def api_patch_task(task_id):
    """Update any field(s) on a task."""
    data = request.get_json() or {}

    # Legacy support: action-based mutations
    action = data.get("action")
    conn = get_db()

    if action == "toggle":
        task = get_task(conn, task_id)
        if not task:
            conn.close()
            return jsonify({"error": "Task not found"}), 404
        # Check for recurrence
        if task.get("recurrence") and not task["done"]:
            new_id = complete_recurring_task(conn, task_id)
            conn.close()
            return jsonify({"ok": True, "new_task_id": new_id, "recurring": True})
        new_done = toggle_task(conn, task_id)
        conn.close()
        if new_done is None:
            return jsonify({"error": "Task not found"}), 404
        return jsonify({"ok": True, "done": bool(new_done)})

    elif action == "delegate":
        name = data.get("name", "").strip()
        if not name:
            conn.close()
            return jsonify({"error": "name is required for delegation"}), 400
        update_task(conn, task_id, delegated_to=name)
        conn.close()
        return jsonify({"ok": True})

    elif action == "undelegate":
        update_task(conn, task_id, delegated_to=None)
        conn.close()
        return jsonify({"ok": True})

    elif action == "rename":
        text = data.get("text", "").strip()
        if not text:
            conn.close()
            return jsonify({"error": "text is required"}), 400
        update_task(conn, task_id, title=text)
        conn.close()
        return jsonify({"ok": True})

    elif action == "delete":
        delete_task(conn, task_id)
        conn.close()
        return jsonify({"ok": True})

    elif action:
        conn.close()
        return jsonify({"error": f"Unknown action: {action}"}), 400

    # Field-based update (no action key)
    fields = {}
    for key in ("title", "description", "done", "priority", "due_date",
                "delegated_to", "position", "section_id"):
        if key in data:
            fields[key] = data[key]

    if not fields:
        conn.close()
        return jsonify({"error": "No fields to update"}), 400

    # Handle done transition with recurrence
    if "done" in fields and fields["done"]:
        task = get_task(conn, task_id)
        if task and task.get("recurrence"):
            new_id = complete_recurring_task(conn, task_id)
            conn.close()
            return jsonify({"ok": True, "new_task_id": new_id, "recurring": True})

    ok = update_task(conn, task_id, **fields)
    conn.close()
    if not ok:
        return jsonify({"error": "Task not found or no valid fields"}), 404
    return jsonify({"ok": True})


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def api_delete_task(task_id):
    conn = get_db()
    delete_task(conn, task_id)
    conn.close()
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Routes — Subtasks
# ---------------------------------------------------------------------------

@app.route("/api/tasks/<int:task_id>/subtasks", methods=["POST"])
def api_add_subtask(task_id):
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400
    conn = get_db()
    sub_id = create_subtask(conn, task_id, title)
    conn.close()
    return jsonify({"ok": True, "id": sub_id}), 201


@app.route("/api/subtasks/<int:subtask_id>", methods=["PATCH"])
def api_patch_subtask(subtask_id):
    data = request.get_json() or {}

    action = data.get("action")
    conn = get_db()

    if action == "toggle":
        new_done = toggle_subtask(conn, subtask_id)
        conn.close()
        if new_done is None:
            return jsonify({"error": "Subtask not found"}), 404
        return jsonify({"ok": True, "done": bool(new_done)})

    fields = {}
    for key in ("title", "done", "position"):
        if key in data:
            fields[key] = data[key]
    if not fields:
        conn.close()
        return jsonify({"error": "No fields to update"}), 400

    ok = update_subtask(conn, subtask_id, **fields)
    conn.close()
    return jsonify({"ok": ok})


@app.route("/api/subtasks/<int:subtask_id>", methods=["DELETE"])
def api_delete_subtask(subtask_id):
    conn = get_db()
    delete_subtask(conn, subtask_id)
    conn.close()
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Routes — Tags
# ---------------------------------------------------------------------------

@app.route("/api/tags")
def api_tags():
    conn = get_db()
    tags = get_all_tags(conn)
    conn.close()
    return jsonify({"tags": tags})


@app.route("/api/tags", methods=["POST"])
def api_create_tag():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400
    color = data.get("color", "#6b7280")
    conn = get_db()
    try:
        tag_id = create_tag(conn, name, color)
    except Exception:
        conn.close()
        return jsonify({"error": "Tag name already exists"}), 409
    conn.close()
    return jsonify({"ok": True, "id": tag_id}), 201


@app.route("/api/tags/<int:tag_id>", methods=["PATCH"])
def api_patch_tag(tag_id):
    data = request.get_json() or {}
    fields = {}
    if "name" in data:
        fields["name"] = data["name"]
    if "color" in data:
        fields["color"] = data["color"]
    conn = get_db()
    ok = update_tag(conn, tag_id, **fields)
    conn.close()
    return jsonify({"ok": ok})


@app.route("/api/tags/<int:tag_id>", methods=["DELETE"])
def api_delete_tag(tag_id):
    conn = get_db()
    delete_tag(conn, tag_id)
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/tasks/<int:task_id>/tags", methods=["POST"])
def api_add_tag_to_task(task_id):
    data = request.get_json() or {}
    tag_id = data.get("tag_id")
    if not tag_id:
        return jsonify({"error": "tag_id is required"}), 400
    conn = get_db()
    add_tag_to_task(conn, task_id, tag_id)
    conn.close()
    return jsonify({"ok": True}), 201


@app.route("/api/tasks/<int:task_id>/tags/<int:tag_id>", methods=["DELETE"])
def api_remove_tag_from_task(task_id, tag_id):
    conn = get_db()
    remove_tag_from_task(conn, task_id, tag_id)
    conn.close()
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Routes — Recurrence
# ---------------------------------------------------------------------------

@app.route("/api/tasks/<int:task_id>/recurrence", methods=["POST"])
def api_set_recurrence(task_id):
    data = request.get_json() or {}
    pattern = data.get("pattern", "").strip()
    if not pattern:
        return jsonify({"error": "pattern is required"}), 400
    conn = get_db()
    set_recurrence(
        conn, task_id, pattern,
        interval=data.get("interval", 1),
        days_of_week=data.get("days_of_week"),
        next_due=data.get("next_due"),
    )
    conn.close()
    return jsonify({"ok": True}), 201


@app.route("/api/tasks/<int:task_id>/recurrence", methods=["DELETE"])
def api_remove_recurrence(task_id):
    conn = get_db()
    remove_recurrence(conn, task_id)
    conn.close()
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Routes — Archive
# ---------------------------------------------------------------------------

@app.route("/api/archive", methods=["POST"])
def api_archive():
    conn = get_db()
    count = archive_completed(conn)
    conn.close()
    if count == 0:
        return jsonify({"ok": True, "archived": 0})
    return jsonify({"ok": True, "archived": count})


# ---------------------------------------------------------------------------
# Routes — Sync
# ---------------------------------------------------------------------------

@app.route("/api/sync", methods=["POST"])
def api_sync():
    """Bidirectional sync between markdown files and SQLite database."""
    if IS_CLOUD:
        return jsonify({"error": "Markdown sync not available in cloud mode"}), 503
    conn = get_db()
    try:
        changes = sync_tasks(conn)
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500
    conn.close()
    total = sum(changes.values())
    return jsonify({"ok": True, "total_changes": total, "details": changes})


# ---------------------------------------------------------------------------
# Routes — Delegated
# ---------------------------------------------------------------------------

@app.route("/api/delegated")
def api_delegated():
    conn = get_db()
    rows = conn.execute("""
        SELECT t.*, s.name AS section_name, a.key AS area_key, a.title AS area_title
        FROM tasks t
        JOIN sections s ON s.id = t.section_id
        JOIN areas a ON a.id = s.area_id
        WHERE t.delegated_to IS NOT NULL AND t.archived = 0
        ORDER BY t.delegated_to, a.position, s.position, t.position
    """).fetchall()
    conn.close()
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "text": r["title"],
            "done": bool(r["done"]),
            "delegated_to": r["delegated_to"],
            "area": r["area_title"],
            "area_key": r["area_key"],
            "section": r["section_name"],
            "due_date": r["due_date"],
            "priority": r["priority"],
        })
    return jsonify({"delegated": results})


# ---------------------------------------------------------------------------
# Routes — Analytics / Reporting
# ---------------------------------------------------------------------------

@app.route("/api/tasks/completed")
def api_tasks_completed():
    """Tasks completed in a date range."""
    start = request.args.get("start")
    end = request.args.get("end")
    if not start or not end:
        return jsonify({"error": "start and end query params required"}), 400
    conn = get_db()
    tasks = get_tasks_completed_between(conn, start, end)
    conn.close()
    return jsonify({"tasks": tasks, "count": len(tasks)})


@app.route("/api/tasks/stale")
def api_tasks_stale():
    """Open tasks with no priority or due date, older than N days."""
    days = request.args.get("days", 14, type=int)
    conn = get_db()
    tasks = get_tasks_stale(conn, days=days)
    conn.close()
    return jsonify({"tasks": tasks, "count": len(tasks)})


@app.route("/api/delegated/summary")
def api_delegation_summary():
    """Delegated tasks grouped by person with counts."""
    conn = get_db()
    summary = get_delegation_summary(conn)
    conn.close()
    return jsonify({"summary": summary})


@app.route("/api/stats/sections")
def api_stats_sections():
    """Open/done/priority counts per section."""
    area = request.args.get("area")
    conn = get_db()
    sections = get_task_counts_by_section(conn, area_key=area)
    conn.close()
    return jsonify({"sections": sections})


@app.route("/api/stats/velocity")
def api_stats_velocity():
    """Tasks completed per week for the last N weeks."""
    weeks = request.args.get("weeks", 4, type=int)
    conn = get_db()
    metrics = get_velocity_metrics(conn, weeks=weeks)
    conn.close()
    return jsonify({"velocity": metrics})


@app.route("/api/tasks/unprioritized")
def api_tasks_unprioritized():
    """Open tasks with no priority set."""
    area = request.args.get("area")
    conn = get_db()
    tasks = get_unprioritized_tasks(conn, area_key=area)
    conn.close()
    return jsonify({"tasks": tasks, "count": len(tasks)})


# ---------------------------------------------------------------------------
# Routes — Inbox
# ---------------------------------------------------------------------------

@app.route("/api/inbox/parse", methods=["POST"])
def api_inbox_parse():
    """Parse raw text into tasks using Claude CLI."""
    if IS_CLOUD:
        return jsonify({"error": "Not available in cloud mode"}), 503
    if not check_claude_available():
        return jsonify({"error": "claude CLI not found on server PATH"}), 503

    data = request.get_json()
    content = (data or {}).get("content", "").strip()
    if not content:
        return jsonify({"error": "content is required"}), 400

    # Build areas dict from DB for inbox routing
    conn = get_db()
    areas = get_all_areas(conn)
    conn.close()
    areas_dict = {}
    for area in areas:
        areas_dict[area["key"]] = {
            "sections": [s["name"] for s in area["sections"]],
        }

    try:
        result = process_inbox(content, areas_dict, DISPLAY_NAMES)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 502
    except ValueError as e:
        return jsonify({"error": str(e)}), 502

    return jsonify({"ok": True, **result})


@app.route("/api/inbox/confirm", methods=["POST"])
def api_inbox_confirm():
    """Write confirmed tasks to database."""
    data = request.get_json()
    tasks = (data or {}).get("tasks", [])
    if not tasks:
        return jsonify({"error": "tasks array is required"}), 400

    conn = get_db()
    # Validate area keys
    valid_areas = {r["key"] for r in conn.execute("SELECT key FROM areas").fetchall()}
    for t in tasks:
        if not t.get("text") or not t.get("area_key") or not t.get("section"):
            conn.close()
            return jsonify({"error": "Each task must have text, area_key, and section"}), 400
        if t["area_key"] not in valid_areas:
            conn.close()
            return jsonify({"error": f"Invalid area_key: {t['area_key']}"}), 400

    added = bulk_create_tasks(conn, tasks)
    conn.close()
    return jsonify({"ok": True, "added": added})


# ---------------------------------------------------------------------------
# Routes — Morning Summary
# ---------------------------------------------------------------------------

@app.route("/api/summary")
def api_summary():
    """Generate an AI-powered morning summary using Claude CLI."""
    if IS_CLOUD:
        return jsonify({"error": "Not available in cloud mode"}), 503
    if not shutil.which("claude"):
        return jsonify({"error": "claude CLI not found on server PATH"}), 503

    conn = get_db()
    tasks_text = get_tasks_for_summary(conn)
    conn.close()

    today = datetime.now().strftime("%A, %B %#d, %Y") if os.name == "nt" else datetime.now().strftime("%A, %B %-d, %Y")

    prompt = f"""You are a personal executive assistant. Today is {today}.

Below are my current task files across 4 areas of my life: Personal, Sunbelt FP&A (professional), and Planyfi (startup — App and Marketing).

Tasks marked - [ ] are open. Tasks marked - [x] are completed (pending archive). Tasks tagged @delegated(Name) have been handed off. Tasks with [due: DATE] have deadlines. Tasks with [P1/P2/P3] have priorities.

Please give me a concise morning briefing:

1. Start with a one-line greeting with today's date
2. For each area, list open tasks grouped by sub-area. Mention how old tasks are if there's a date tag.
3. Call out any delegated items separately with who owns them.
4. Highlight any overdue or due-today tasks.
5. End with 1-2 suggested priorities for the day based on what seems most urgent/important.

Keep it scannable — use short lines and clear formatting. Use simple markdown for structure (## headers, bullet points, **bold** for emphasis).

Here are my tasks:

{tasks_text}"""

    try:
        env = os.environ.copy()
        env.pop("CLAUDECODE", None)
        result = subprocess.run(
            ["claude", "--print", "-p", prompt],
            capture_output=True, text=True, timeout=120, env=env,
        )
        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip() or "Claude CLI failed"}), 502
        return jsonify({"ok": True, "summary": result.stdout.strip()})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Claude CLI timed out (120s)"}), 504
    except FileNotFoundError:
        return jsonify({"error": "claude CLI not found"}), 503


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Work Planner running at http://0.0.0.0:5151")
    app.run(host="0.0.0.0", port=5151, debug=True)
