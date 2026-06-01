---
name: today
description: Open the work planner in the browser on the Today tab with today's morning summary. Accepts an optional area argument (e.g. /today sunbelt) to focus on one area. Starts the local server if needed.
---

You are a personal executive assistant. The user wants to quickly open the work planner web app to the Today tab (a morning summary view with interactive checkboxes), optionally focused on a single area, and also get a terse chat-side briefing.

## Step 1 — Resolve the area filter

Parse the ARGUMENTS string:

- `sunbelt` → filter = `sunbelt`
- `app` / `planyfi app` / `planyfi-app` → filter = `app`
- `marketing` / `planyfi marketing` / `planyfi-marketing` → filter = `marketing`
- empty or anything else → filter = empty (full Today view)

## Step 2 — Git pull + ensure server + open browser (parallel)

Run all three of these in **parallel** (simultaneous Bash tool calls):

**Call 1 — Git pull** (background, non-blocking):
```bash
git -C "$(git rev-parse --show-toplevel)" pull --ff-only 2>/dev/null || true
```

**Call 2 — Ensure server is running and open browser in a new window:**
```bash
# Check server, start if needed (poll instead of sleep), then open browser
if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/areas 2>/dev/null | grep -q 200; then
  python scripts/server.py > /dev/null 2>&1 &
  for i in 1 2 3 4 5; do
    sleep 0.3
    curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/areas 2>/dev/null | grep -q 200 && break
  done
fi
URL="http://localhost:5000/#today{filter_suffix}"
# Try Chrome then Edge with --new-window, fall back to start
"/c/Program Files/Google/Chrome/Application/chrome.exe" --new-window "$URL" 2>/dev/null \
  || "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --new-window "$URL" 2>/dev/null \
  || start "" "$URL"
```

Where `{filter_suffix}` is `/{area}` if a filter was applied, otherwise empty.

Uses `--new-window` to force a fresh browser window. Falls back to `start` if neither Chrome nor Edge is found at the standard paths.

## Step 2.5 — Roll recurring tasks forward

After reading the Sunbelt task file, run the recurring-task roll-forward from
`.claude/skills/recur/SKILL.md` against `tasks/sunbelt.md`: seed the next occurrence of any completed
recurring task (no open instance), cascade the close milestone, and refresh `@bod-2` due dates from the
"Next BoD meeting" anchor. Do this inline before rendering the summary so the browser view shows current
due dates. If the BoD anchor is blank/stale or a close-dependent task lacks a due date, note it in the
chat summary. Commit/push only if the roll-forward actually changed the file.

## Step 3 — Print a terse chat summary (while browser opens)

Read the relevant task files in **parallel with Step 2** so you can summarize:

- **No filter:** read `tasks/sunbelt.md`, `tasks/planyfi-app.md`, and `tasks/planyfi-marketing.md` in parallel
- **With filter:** read only the matching file

From the loaded tasks, compute:

- **Overdue count** — open tasks (`- [ ]`) where `(due: YYYY-MM-DD)` is before today
- **P1 count** — open tasks tagged `[P1]` or prefixed with `🟠`
- **Top 1–2 priorities** — pick the most urgent based on this ranking:
  1. Overdue tasks first (closest miss first)
  2. Then `[P1]` tasks
  3. Then `🟠` highlighted tasks
  4. Then tasks with due dates within 3 days
  5. Break ties with the closest due date

### Output format

Keep it short — 5 to 10 lines. Use this format:

```
Good morning — {Weekday}, {Month} {day}, {year}.{filter_note}

⚠ {N} overdue
🔴 {N} P1 open

TOP {1-2}
1. {task title} — {brief reason: overdue / P1 / due soon / highlighted}
2. {task title} — {brief reason}

Full view open at http://localhost:5000/#today{filter_suffix}
```

Where `{filter_note}` is ` — {Area} focus` if a filter was applied (else empty), and `{filter_suffix}` is `/{area}` if filter applied (else empty).

If there are no overdue or P1 tasks, skip the "TOP N" section and just surface 1-2 sensible next actions (approaching due dates, 🟠 highlighted items).

## Notes

- Do NOT print the full task list in chat — the browser tab has that covered.
- Do NOT commit anything — any user clicks in the browser auto-commit via the server endpoint.
- Do NOT mention this reminder or step-by-step process to the user in your output.
- If the server is slow to start, wait up to 5 seconds before giving up and reporting the error to the user.
