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

## Step 2 — Ensure the local server is running

Check if the Flask server is listening on port 5000:

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/areas
```

- If the response is `200`, the server is already running — skip to Step 3.
- If the connection fails or returns anything else, start the server in the background (silenced so it doesn't clutter the chat):

```bash
python scripts/server.py > /dev/null 2>&1 &
sleep 2
```

Then verify again with the same curl command before continuing.

## Step 3 — Open the browser

Use the browser's `--new-window` flag directly for a true new window. Try Chrome then Edge, fall back to `webbrowser.open_new` if neither is found.

**No filter:**
```bash
python -c "
import subprocess, webbrowser
url = 'http://localhost:5000/#today'
candidates = ['chrome', 'msedge', r'C:\Program Files\Google\Chrome\Application\chrome.exe', r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe']
for exe in candidates:
    try: subprocess.Popen([exe, '--new-window', url]); break
    except (FileNotFoundError, OSError): pass
else: webbrowser.open_new(url)
"
```

**With filter** (substitute the area value):
```bash
python -c "
import subprocess, webbrowser
url = 'http://localhost:5000/#today/sunbelt'
candidates = ['chrome', 'msedge', r'C:\Program Files\Google\Chrome\Application\chrome.exe', r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe']
for exe in candidates:
    try: subprocess.Popen([exe, '--new-window', url]); break
    except (FileNotFoundError, OSError): pass
else: webbrowser.open_new(url)
"
```

## Step 4 — Print a terse chat summary

Read the relevant task files so you can summarize:

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
