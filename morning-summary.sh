#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Gather all tasks from SQLite via db.py
TASKS=$(python3 "$SCRIPT_DIR/web/db.py" --summary-text)
TODAY=$(date +"%A, %B %-d, %Y")

PROMPT="You are a personal executive assistant. Today is $TODAY.

Below are my current task files across 3 areas of my life: Personal, Sunbelt FP&A (professional), and Planyfi (startup).

Tasks marked - [ ] are open. Tasks marked - [x] are completed (pending archive). Tasks tagged @delegated(Name) have been handed off.

Please give me a concise morning briefing:

1. Start with a one-line greeting with today's date
2. For each area, list open tasks grouped by sub-area. Mention how old tasks are if there's a date tag.
3. Call out any delegated items separately with who owns them.
4. End with 1-2 suggested priorities for the day based on what seems most urgent/important.

Keep it scannable — use short lines and clear formatting. No markdown headers, just clean terminal-friendly output with simple symbols.

Here are my tasks:

$TASKS"

# Check which AI CLI is available
if command -v claude &>/dev/null; then
  echo "$PROMPT" | claude --print
elif command -v openai &>/dev/null; then
  echo "$PROMPT" | openai api chat.completions.create -m gpt-4o -
else
  # Fallback: simple non-AI summary from DB
  echo ""
  echo "Good morning — $TODAY"
  echo "==========================================="
  echo ""
  echo "OPEN TASKS:"
  echo ""
  echo "$TASKS"
  echo ""

  # Show delegated tasks
  delegated=$(python3 -c "
import sys, os
sys.path.insert(0, os.path.join('$SCRIPT_DIR', 'web'))
from db import get_db, init_db
init_db()
conn = get_db()
rows = conn.execute('''
    SELECT a.title AS area_title, t.id, t.title, t.delegated_to
    FROM tasks t
    JOIN sections s ON s.id = t.section_id
    JOIN areas a ON a.id = s.area_id
    WHERE t.delegated_to IS NOT NULL AND t.delegated_to != ''
          AND t.archived = 0 AND t.done = 0
    ORDER BY a.position, t.position
''').fetchall()
for r in rows:
    print(f'  #{r[\"id\"]} [{r[\"area_title\"]}] {r[\"title\"]} -> {r[\"delegated_to\"]}')
conn.close()
" 2>/dev/null || true)

  if [[ -n "$delegated" ]]; then
    echo "DELEGATED:"
    echo "$delegated"
    echo ""
  fi

  echo "==========================================="
  echo "Tip: Install 'claude' CLI for AI-powered summaries"
  echo ""
fi
