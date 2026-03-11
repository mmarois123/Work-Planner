#!/usr/bin/env python3
"""Inbox CLI — Interactive terminal preview/confirm flow.

Usage:
    cat notes.md | python3 web/inbox_cli.py
    python3 web/inbox_cli.py < notes.md
"""

import os
import sys

import yaml

# Add parent so we can import inbox
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inbox import (
    check_claude_available,
    process_inbox,
)
from db import get_db, init_db, bulk_create_tasks

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.yaml")
TASKS_DIR = os.path.join(PROJECT_ROOT, "tasks")

DISPLAY_NAMES = {
    "sunbelt": "Sunbelt FP&A",
    "app": "Planyfi — App",
    "marketing": "Planyfi — Marketing",
    "personal": "Personal",
}

CONFIDENCE_MARKERS = {"high": "+", "medium": "~", "low": "?"}


def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def print_preview(tasks, display_names):
    """Print a formatted preview table of parsed tasks."""
    if not tasks:
        print("\n  No actionable tasks found.")
        return

    print(f"\n  Found {len(tasks)} task(s):\n")
    print(f"  {'#':<4} {'Conf':<5} {'Area':<20} {'Section':<18} {'Task'}")
    print(f"  {'─'*4} {'─'*5} {'─'*20} {'─'*18} {'─'*40}")

    for i, task in enumerate(tasks, 1):
        conf = task.get("confidence", "medium")
        marker = CONFIDENCE_MARKERS.get(conf, "?")
        area_name = display_names.get(task["area_key"], task["area_key"])
        print(f"  {i:<4} [{marker}]   {area_name:<20} {task['section']:<18} {task['text']}")

    print()
    print("  Confidence: [+] high  [~] medium  [?] low")
    print()


def prompt_confirm(tasks):
    """Prompt user for confirmation. Returns list of tasks to apply.

    Options:
        Y/y/enter - add all tasks
        n/N       - cancel
        select    - pick specific tasks by number
    """
    while True:
        try:
            choice = input("  Add these tasks? [Y/n/select] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return []

        if choice in ("", "y", "yes"):
            return tasks

        if choice in ("n", "no"):
            print("  Cancelled.")
            return []

        if choice in ("s", "select"):
            try:
                nums = input("  Enter task numbers (comma-separated): ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return []
            selected = []
            for part in nums.split(","):
                part = part.strip()
                if part.isdigit():
                    idx = int(part) - 1
                    if 0 <= idx < len(tasks):
                        selected.append(tasks[idx])
            if selected:
                return selected
            print("  No valid tasks selected. Try again.")

        # Invalid input — loop again


def main():
    # Check claude is available
    if not check_claude_available():
        print("Error: 'claude' CLI not found on PATH.", file=sys.stderr)
        print("Install it or check your PATH.", file=sys.stderr)
        sys.exit(1)

    # Read input from stdin
    if sys.stdin.isatty():
        print("Error: No input. Pipe text or a file via stdin.", file=sys.stderr)
        print("  Usage: cat notes.md | ./task.sh inbox -", file=sys.stderr)
        print("         ./task.sh inbox notes.md", file=sys.stderr)
        sys.exit(1)

    content = sys.stdin.read().strip()
    if not content:
        print("Error: Empty input.", file=sys.stderr)
        sys.exit(1)

    # Load config
    config = load_config()
    areas = config["areas"]

    # Process with AI
    print("  Processing with Claude...")
    try:
        result = process_inbox(content, areas, DISPLAY_NAMES)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error parsing AI response: {e}", file=sys.stderr)
        sys.exit(1)

    tasks = result.get("tasks", [])
    unparsed = result.get("unparsed", [])

    # Show preview
    print_preview(tasks, DISPLAY_NAMES)

    if unparsed:
        print("  Could not parse:")
        for line in unparsed:
            print(f"    - {line}")
        print()

    if not tasks:
        sys.exit(0)

    # Confirm
    confirmed = prompt_confirm(tasks)
    if not confirmed:
        sys.exit(0)

    # Write tasks to SQLite database
    init_db()
    conn = get_db()
    added = bulk_create_tasks(conn, confirmed)
    conn.close()
    print(f"  Added {added} task(s).")


if __name__ == "__main__":
    main()
