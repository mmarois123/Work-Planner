#!/usr/bin/env python3
"""Work Planner — Flask API server.

All data stored in SQLite via db.py. Start with: python3 web/server.py
"""

import os
import sys

# Load .env for Turso creds (needed for sync_from_turso on local startup).
# On Vercel, env vars are injected directly so dotenv is a no-op.
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))
except ImportError:
    pass

from flask import Flask, jsonify, request, send_from_directory

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import (
    get_db, init_db,
    get_all_areas, get_all_tasks, get_task,
    toggle_task, delete_task, archive_completed,
    toggle_subtask, delete_subtask,
    get_all_tags,
    get_tasks_due_today, get_tasks_overdue, get_tasks_upcoming,
    get_tasks_calendar, get_tasks_no_due_date,
    complete_recurring_task,
    sync_tasks,
    get_tasks_completed_between, get_tasks_stale, get_delegation_summary,
    get_task_counts_by_section, get_velocity_metrics, get_unprioritized_tasks,
)

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

app = Flask(__name__)

from flask_cors import CORS
CORS(app, origins=[
    "https://mmarois123.github.io",
    "http://localhost:5151",
    "http://127.0.0.1:5151",
], supports_credentials=True)

DISPLAY_NAMES = {
    "sunbelt": "Sunbelt FP&A",
    "app": "Planyfi — App",
    "marketing": "Planyfi — Marketing",
    "personal": "Personal",
}

# Cloud / auth configuration
WP_AUTH_PIN = os.environ.get("WP_AUTH_PIN")
SKIP_INIT_DB = os.environ.get("SKIP_INIT_DB")
IS_VERCEL = bool(os.environ.get("VERCEL"))
HAS_TURSO = bool(os.environ.get("TURSO_DATABASE_URL"))

if IS_VERCEL:
    # On Vercel: use Turso directly, schema already exists
    if not SKIP_INIT_DB:
        init_db()
else:
    # Local: pull cloud data into local SQLite, then run on local SQLite
    if HAS_TURSO:
        try:
            from db import sync_from_turso
            sync_from_turso()
        except Exception as e:
            print(f"Turso sync failed (using local data): {e}")
    # Force db.py to use local SQLite even though TURSO env vars exist
    import db as _db
    _db.USE_TURSO = False
    _db._turso_conn = None
    # Init local DB schema
    init_db()
    # Sync markdown <-> DB
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
# Background Turso sync (local -> cloud after writes)
# ---------------------------------------------------------------------------

_turso_push_pending = False
_turso_push_timer = None

def schedule_turso_push():
    """Debounce: push to Turso 2s after the last write, in a background thread."""
    global _turso_push_pending, _turso_push_timer
    if IS_VERCEL or not HAS_TURSO:
        return
    import threading
    if _turso_push_timer:
        _turso_push_timer.cancel()
    def _do_push():
        global _turso_push_pending
        try:
            from db import push_to_turso
            push_to_turso()
        except Exception as e:
            print(f"Background Turso push failed: {e}")
        _turso_push_pending = False
    _turso_push_pending = True
    _turso_push_timer = threading.Timer(2.0, _do_push)
    _turso_push_timer.daemon = True
    _turso_push_timer.start()


# ---------------------------------------------------------------------------
# Auth middleware & sync hooks
# ---------------------------------------------------------------------------

@app.after_request
def after_write(response):
    """Push local changes to Turso after any mutating API request."""
    if request.method in ('POST', 'PATCH', 'PUT', 'DELETE') and request.path.startswith('/api/'):
        schedule_turso_push()
    return response

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
    return jsonify({"ok": True, "mode": "cloud" if IS_VERCEL else "local"})

# ---------------------------------------------------------------------------
# Routes — static
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(SCRIPT_DIR, "index.html")


# ---------------------------------------------------------------------------
# Routes — Combined init (single request for page load)
# ---------------------------------------------------------------------------

@app.route("/api/init")
def api_init():
    """Return tasks + tags + config in a single response to minimize cold-start latency."""
    conn = get_db()
    areas = get_all_tasks(conn)
    tags = get_all_tags(conn)
    config = {}
    for area in get_all_areas(conn):
        config[area["key"]] = {
            "title": area["title"],
            "sections": [s["name"] for s in area["sections"]],
        }
    conn.close()
    return jsonify({"areas": areas, "tags": tags, "config": config})


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
    """Toggle a task's done status (read-only web app — no field edits)."""
    data = request.get_json() or {}
    action = data.get("action")
    if action != "toggle":
        return jsonify({"error": "Only toggle action is allowed"}), 400

    conn = get_db()
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


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def api_delete_task(task_id):
    conn = get_db()
    delete_task(conn, task_id)
    conn.close()
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Routes — Subtasks
# ---------------------------------------------------------------------------

@app.route("/api/subtasks/<int:subtask_id>", methods=["PATCH"])
def api_patch_subtask(subtask_id):
    """Toggle a subtask's done status (read-only web app — no field edits)."""
    data = request.get_json() or {}
    action = data.get("action")
    if action != "toggle":
        return jsonify({"error": "Only toggle action is allowed"}), 400

    conn = get_db()
    new_done = toggle_subtask(conn, subtask_id)
    conn.close()
    if new_done is None:
        return jsonify({"error": "Subtask not found"}), 404
    return jsonify({"ok": True, "done": bool(new_done)})


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
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Work Planner running at http://0.0.0.0:5151")
    app.run(host="0.0.0.0", port=5151, debug=True)
