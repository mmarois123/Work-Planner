#!/usr/bin/env python3
"""Inbox — AI-powered task parsing and routing.

Accepts raw text (notes, markdown, freeform ideas), uses Claude CLI
to parse tasks and route them to the correct area/section files.
"""

import json
import os
import shutil
import subprocess

# Paths (same as server.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
TASKS_DIR = os.path.join(PROJECT_ROOT, "tasks")

# ---------------------------------------------------------------------------
# Claude CLI helpers
# ---------------------------------------------------------------------------

def check_claude_available():
    """Return True if the `claude` CLI is on PATH."""
    return shutil.which("claude") is not None


def build_inbox_prompt(content, areas, display_names):
    """Build the prompt sent to Claude for task extraction.

    Args:
        content: Raw text from the user.
        areas: dict from config.yaml (key -> {file, sections}).
        display_names: dict (key -> human-readable title).

    Returns:
        str: The full prompt.
    """
    area_lines = []
    for key, area in areas.items():
        name = display_names.get(key, key)
        sections = ", ".join(area["sections"])
        area_lines.append(f'  - area_key: "{key}" ({name})  sections: [{sections}]')

    areas_block = "\n".join(area_lines)

    return f"""You are a task-extraction assistant for a personal work planner.

Given the raw text below, extract individual actionable tasks and assign each
to exactly one area and section from the valid list.

VALID AREAS AND SECTIONS:
{areas_block}

RULES:
1. Each task must be a short, actionable line (imperative mood preferred).
2. Assign the best-matching area_key and section.
3. If unsure, use area_key "personal" and section "Other".
4. Set confidence to "high", "medium", or "low".
5. Include the original snippet that led to the task.
6. If text contains no actionable tasks, return an empty tasks array.

Return ONLY a JSON object (no markdown fences, no explanation) in this format:
{{
  "tasks": [
    {{
      "text": "Task description",
      "area_key": "valid_area_key",
      "section": "Valid Section Name",
      "confidence": "high",
      "original_snippet": "source text fragment"
    }}
  ],
  "unparsed": ["any lines that could not be turned into tasks"]
}}

RAW TEXT:
{content}"""


def call_claude(prompt):
    """Call `claude --print` with the given prompt.

    Returns:
        str: Raw stdout from Claude.

    Raises:
        RuntimeError: If claude is not available or the call fails.
    """
    claude_path = shutil.which("claude")
    if not claude_path:
        raise RuntimeError("claude CLI not found on PATH")

    env = os.environ.copy()
    env.pop("CLAUDECODE", None)

    result = subprocess.run(
        [claude_path, "--print", prompt],
        capture_output=True,
        text=True,
        timeout=120,
        shell=(os.name == "nt"),
        env=env,
    )

    if result.returncode != 0:
        raise RuntimeError(f"claude exited with code {result.returncode}: {result.stderr.strip()}")

    return result.stdout.strip()


def parse_ai_response(raw):
    """Parse the JSON response from Claude.

    Strips markdown fences if present, then JSON-decodes.

    Returns:
        dict: {"tasks": [...], "unparsed": [...]}

    Raises:
        ValueError: If parsing fails.
    """
    text = raw.strip()

    # Strip markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json or ```) and last line (```)
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse AI response as JSON: {e}\nRaw output:\n{text}")

    if "tasks" not in data:
        raise ValueError("AI response missing 'tasks' key")

    return data


def validate_routing(tasks, areas):
    """Validate and fix routing for parsed tasks.

    If a task's area_key or section is invalid, fall back to personal/Other.

    Args:
        tasks: list of task dicts from AI.
        areas: dict from config.

    Returns:
        list: Validated task dicts (modified in place).
    """
    for task in tasks:
        area_key = task.get("area_key", "")
        section = task.get("section", "")

        if area_key not in areas:
            task["area_key"] = "personal"
            task["section"] = "Other"
            task["confidence"] = "low"
            continue

        valid_sections = [s.lower() for s in areas[area_key]["sections"]]
        if section.lower() not in valid_sections:
            # Try to find a case-insensitive match
            matched = False
            for s in areas[area_key]["sections"]:
                if s.lower() == section.lower():
                    task["section"] = s
                    matched = True
                    break
            if not matched:
                task["area_key"] = "sunbelt"
                task["section"] = "Tasks"
                task["confidence"] = "low"

    return tasks


def process_inbox(content, areas, display_names):
    """Full pipeline: prompt -> Claude -> parse -> validate.

    Args:
        content: Raw text to process.
        areas: Config areas dict.
        display_names: Config display names dict.

    Returns:
        dict: {"tasks": [...], "unparsed": [...]}
    """
    prompt = build_inbox_prompt(content, areas, display_names)
    raw = call_claude(prompt)
    data = parse_ai_response(raw)
    data["tasks"] = validate_routing(data.get("tasks", []), areas)
    return data


def apply_tasks(tasks, areas, tasks_dir=None, file_lock=None):
    """Write parsed tasks to their respective markdown files.

    Uses the same insertion logic as server.py: append after section header.

    Args:
        tasks: list of {"text", "area_key", "section"} dicts.
        areas: Config areas dict.
        tasks_dir: Path to tasks directory (defaults to TASKS_DIR).
        file_lock: threading.Lock for file safety (optional).

    Returns:
        int: Number of tasks successfully added.
    """
    if tasks_dir is None:
        tasks_dir = TASKS_DIR

    added = 0

    # Group tasks by area to minimize file reads/writes
    by_area = {}
    for task in tasks:
        key = task["area_key"]
        if key not in by_area:
            by_area[key] = []
        by_area[key].append(task)

    def _do_write():
        nonlocal added
        for area_key, area_tasks in by_area.items():
            if area_key not in areas:
                continue

            filepath = os.path.join(tasks_dir, areas[area_key]["file"])
            if not os.path.exists(filepath):
                continue

            with open(filepath) as f:
                lines = f.readlines()

            # Build a map of section header positions (case-insensitive)
            section_inserts = {}  # line index -> list of task texts
            for i, line in enumerate(lines):
                stripped = line.rstrip("\n")
                if stripped.startswith("## "):
                    header = stripped[3:].strip().lower()
                    section_inserts[header] = i

            new_lines = []
            for i, line in enumerate(lines):
                new_lines.append(line)
                stripped = line.rstrip("\n")
                if stripped.startswith("## "):
                    header = stripped[3:].strip().lower()
                    for task in area_tasks:
                        if task["section"].lower() == header:
                            new_lines.append(f"- [ ] {task['text']}\n")
                            added += 1

            with open(filepath, "w") as f:
                f.writelines(new_lines)

    if file_lock:
        with file_lock:
            _do_write()
    else:
        _do_write()

    return added
