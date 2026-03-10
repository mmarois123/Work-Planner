#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TASKS_DIR="$SCRIPT_DIR/tasks"

# Gather all task files into a single context
gather_tasks() {
  local all=""
  for f in "$TASKS_DIR"/*.md; do
    all+="$(cat "$f")"
    all+=$'\n\n'
  done
  echo "$all"
}

TASKS=$(gather_tasks)
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
  # Fallback: simple non-AI summary
  echo ""
  echo "Good morning — $TODAY"
  echo "==========================================="
  echo ""
  echo "OPEN TASKS:"
  echo ""
  for f in "$TASKS_DIR"/*.md; do
    basename "$f" .md | tr '-' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2))}1'
    grep -n '\- \[ \]' "$f" 2>/dev/null | sed 's/^/  /' || echo "  (none)"
    echo ""
  done

  delegated=$(grep -n '@delegated' "$TASKS_DIR"/*.md 2>/dev/null | grep -v '<!--' || true)
  if [[ -n "$delegated" ]]; then
    echo "DELEGATED:"
    echo "$delegated" | sed 's/^/  /'
    echo ""
  fi

  echo "==========================================="
  echo "Tip: Install 'claude' CLI for AI-powered summaries"
  echo ""
fi
