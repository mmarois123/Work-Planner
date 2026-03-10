#!/usr/bin/env python3
"""Work Planner — Flask API server.

Reads/writes the same markdown task files used by task.sh.
Start with: python3 web/server.py
"""

import os
import re
import threading
from datetime import date, datetime

import yaml
from flask import Flask, jsonify, request, send_from_directory

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
TASKS_DIR = os.path.join(PROJECT_ROOT, "tasks")
ARCHIVE_DIR = os.path.join(PROJECT_ROOT, "archive")
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.yaml")

app = Flask(__name__)
file_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

CONFIG = load_config()
AREAS = CONFIG["areas"]  # dict: key -> {file, sections}

DISPLAY_NAMES = {
    "personal": "Personal",
    "sunbelt": "Sunbelt FP&A",
    "app": "Planyfi — App",
    "marketing": "Planyfi — Marketing",
}

# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

TASK_RE = re.compile(r"^- \[([ x])\] (.+)$")
DELEGATED_RE = re.compile(r"@delegated\(([^)]+)\)")


def parse_task_file(area_key):
    """Parse a markdown task file into structured data."""
    filepath = os.path.join(TASKS_DIR, AREAS[area_key]["file"])
    if not os.path.exists(filepath):
        return {"key": area_key, "title": DISPLAY_NAMES.get(area_key, area_key), "sections": []}

    with open(filepath) as f:
        lines = f.readlines()

    title = DISPLAY_NAMES.get(area_key, area_key)
    sections = []
    current_section = None

    for i, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip("\n")

        # H1 title
        if line.startswith("# "):
            title = line[2:].strip()
            continue

        # H2 section
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
                "line": i,
                "text": text,
                "done": done,
                "delegated_to": delegated_to,
            })

    return {"key": area_key, "title": title, "sections": sections}


# ---------------------------------------------------------------------------
# File mutation helpers
# ---------------------------------------------------------------------------

def read_lines(area_key):
    filepath = os.path.join(TASKS_DIR, AREAS[area_key]["file"])
    with open(filepath) as f:
        return f.readlines()


def write_lines(area_key, lines):
    filepath = os.path.join(TASKS_DIR, AREAS[area_key]["file"])
    with open(filepath, "w") as f:
        f.writelines(lines)


# ---------------------------------------------------------------------------
# Routes — static
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(SCRIPT_DIR, "index.html")


# ---------------------------------------------------------------------------
# Routes — API
# ---------------------------------------------------------------------------

@app.route("/api/config")
def api_config():
    result = {}
    for key, area in AREAS.items():
        result[key] = {
            "title": DISPLAY_NAMES.get(key, key),
            "sections": area["sections"],
        }
    return jsonify(result)


@app.route("/api/tasks")
def api_tasks_all():
    areas = [parse_task_file(k) for k in AREAS]
    return jsonify({"areas": areas})


@app.route("/api/tasks/<area_key>")
def api_tasks_area(area_key):
    if area_key not in AREAS:
        return jsonify({"error": f"Unknown area: {area_key}"}), 404
    return jsonify(parse_task_file(area_key))


@app.route("/api/tasks/<area_key>", methods=["POST"])
def api_add_task(area_key):
    if area_key not in AREAS:
        return jsonify({"error": f"Unknown area: {area_key}"}), 404

    data = request.get_json()
    section = data.get("section", "").strip()
    text = data.get("text", "").strip()
    if not section or not text:
        return jsonify({"error": "section and text are required"}), 400

    with file_lock:
        lines = read_lines(area_key)
        inserted = False
        new_lines = []
        for line in lines:
            new_lines.append(line)
            stripped = line.rstrip("\n")
            if stripped.startswith("## ") and stripped[3:].strip().lower() == section.lower():
                new_lines.append(f"- [ ] {text}\n")
                inserted = True

        if not inserted:
            return jsonify({"error": f"Section '{section}' not found"}), 404

        write_lines(area_key, new_lines)

    return jsonify({"ok": True, "text": text}), 201


@app.route("/api/tasks/<area_key>/<int:line_num>", methods=["PATCH"])
def api_patch_task(area_key, line_num):
    if area_key not in AREAS:
        return jsonify({"error": f"Unknown area: {area_key}"}), 404

    data = request.get_json()
    action = data.get("action")

    with file_lock:
        lines = read_lines(area_key)
        if line_num < 1 or line_num > len(lines):
            return jsonify({"error": "Invalid line number"}), 400

        line = lines[line_num - 1]
        if not TASK_RE.match(line.rstrip("\n")):
            return jsonify({"error": "Line is not a task"}), 400

        if action == "toggle":
            if "- [ ] " in line:
                lines[line_num - 1] = line.replace("- [ ] ", "- [x] ", 1)
            elif "- [x] " in line:
                lines[line_num - 1] = line.replace("- [x] ", "- [ ] ", 1)
            write_lines(area_key, lines)
            return jsonify({"ok": True})

        elif action == "delegate":
            name = data.get("name", "").strip()
            if not name:
                return jsonify({"error": "name is required for delegation"}), 400
            if "@delegated(" in line:
                return jsonify({"error": "Task already delegated"}), 400
            lines[line_num - 1] = line.rstrip("\n") + f" @delegated({name})\n"
            write_lines(area_key, lines)
            return jsonify({"ok": True})

        elif action == "undelegate":
            lines[line_num - 1] = DELEGATED_RE.sub("", line).rstrip() + "\n"
            write_lines(area_key, lines)
            return jsonify({"ok": True})

        else:
            return jsonify({"error": "Unknown action"}), 400


@app.route("/api/archive", methods=["POST"])
def api_archive():
    month_dir = os.path.join(ARCHIVE_DIR, date.today().strftime("%Y-%m"))
    os.makedirs(month_dir, exist_ok=True)
    date_stamp = date.today().isoformat()
    total = 0

    with file_lock:
        for key, area in AREAS.items():
            filepath = os.path.join(TASKS_DIR, area["file"])
            if not os.path.exists(filepath):
                continue

            with open(filepath) as f:
                lines = f.readlines()

            completed = [l for l in lines if l.strip().startswith("- [x]")]
            if not completed:
                continue

            archive_path = os.path.join(month_dir, area["file"])
            with open(archive_path, "a") as af:
                af.write(f"# Archived {date_stamp}\n")
                af.writelines(completed)
                af.write("\n")

            remaining = [l for l in lines if not l.strip().startswith("- [x]")]
            with open(filepath, "w") as f:
                f.writelines(remaining)

            total += len(completed)

    return jsonify({"ok": True, "archived": total, "month": month_dir})


@app.route("/api/delegated")
def api_delegated():
    results = []
    for key in AREAS:
        parsed = parse_task_file(key)
        for section in parsed["sections"]:
            for task in section["tasks"]:
                if task["delegated_to"]:
                    results.append({
                        "area": parsed["title"],
                        "area_key": key,
                        "section": section["name"],
                        **task,
                    })
    return jsonify({"delegated": results})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Work Planner running at http://0.0.0.0:5151")
    print(f"Tasks directory: {TASKS_DIR}")
    app.run(host="0.0.0.0", port=5151, debug=True)
