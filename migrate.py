#!/usr/bin/env python3
"""Migrate markdown task files to SQLite database.

Reads all 4 markdown files, parses tasks using the existing regex patterns,
and populates the SQLite database created by web/db.py.

Usage:
    python migrate.py              # Run migration
    python migrate.py --dry-run    # Preview without writing
"""

import os
import re
import sys

import yaml

# Add web/ so we can import db
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "web"))
from db import get_db, init_db, DB_PATH

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_DIR = os.path.join(SCRIPT_DIR, "tasks")
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.yaml")

# Same patterns used by server.py
TASK_RE = re.compile(r"^- \[([ x])\] (.+)$")
DELEGATED_RE = re.compile(r"@delegated\(([^)]+)\)")

DISPLAY_NAMES = {
    "sunbelt": "Sunbelt FP&A",
    "app": "Planyfi — App",
    "marketing": "Planyfi — Marketing",
    "personal": "Personal",
}


def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


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


def migrate(dry_run=False):
    config = load_config()
    areas_config = config["areas"]

    total_tasks = 0
    total_sections = 0
    total_areas = 0

    if not dry_run:
        # Remove existing db to start fresh
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()
        conn = get_db()

    print("Migrating markdown tasks to SQLite...\n")

    for area_pos, (area_key, area_info) in enumerate(areas_config.items()):
        title = DISPLAY_NAMES.get(area_key, area_key)
        filepath = os.path.join(TASKS_DIR, area_info["file"])

        print(f"  Area: {title} ({area_key})")

        if not dry_run:
            conn.execute(
                "INSERT INTO areas (key, title, position) VALUES (?, ?, ?)",
                (area_key, title, area_pos)
            )
            area_id = conn.execute(
                "SELECT id FROM areas WHERE key = ?", (area_key,)
            ).fetchone()["id"]
        total_areas += 1

        # Parse the markdown file
        parsed_sections = parse_markdown_file(filepath)

        # Build map of parsed section names (lowercased) to their tasks
        parsed_map = {}
        for s in parsed_sections:
            parsed_map[s["name"].lower()] = s

        # Use config sections order as canonical, but also pick up any
        # sections from the file that aren't in config
        config_sections = area_info.get("sections", [])
        seen = set()
        ordered_sections = []
        for name in config_sections:
            ordered_sections.append(name)
            seen.add(name.lower())
        for s in parsed_sections:
            if s["name"].lower() not in seen:
                ordered_sections.append(s["name"])

        for sec_pos, section_name in enumerate(ordered_sections):
            parsed = parsed_map.get(section_name.lower(), {"tasks": []})
            task_count = len(parsed["tasks"])

            print(f"    Section: {section_name} ({task_count} tasks)")

            if not dry_run:
                conn.execute(
                    "INSERT INTO sections (area_id, name, position) VALUES (?, ?, ?)",
                    (area_id, section_name, sec_pos)
                )
                section_id = conn.execute(
                    "SELECT last_insert_rowid() AS id"
                ).fetchone()["id"]

            total_sections += 1

            for task_pos, task in enumerate(parsed["tasks"]):
                if not dry_run:
                    conn.execute("""
                        INSERT INTO tasks (section_id, title, done, delegated_to, position)
                        VALUES (?, ?, ?, ?, ?)
                    """, (section_id, task["text"], 1 if task["done"] else 0,
                          task["delegated_to"], task_pos))
                total_tasks += 1

    if not dry_run:
        conn.commit()
        conn.close()

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Summary:")
    print(f"  {total_tasks} tasks, {total_sections} sections, {total_areas} areas")
    if not dry_run:
        print(f"  Database: {DB_PATH}")
    print("\nMarkdown files left intact as backup.")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    migrate(dry_run=dry_run)
