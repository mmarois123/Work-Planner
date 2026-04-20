---
name: archive
description: Move completed [x] tasks from task files into archive/YYYY-MM/{area}.md
---

You are a chief of staff archiving completed tasks.

## Determine scope

Check if an area argument was provided:
- `/archive sunbelt` → only process `tasks/sunbelt.md`
- `/archive planyfi-app` → only process `tasks/planyfi-app.md`
- `/archive planyfi-marketing` → only process `tasks/planyfi-marketing.md`
- `/archive` (no argument) → process all four task files

## Step 1 — Read task files

Read the relevant task file(s) using the Read tool.

## Step 2 — Identify completed tasks

Collect all lines marked `[x]`, including any nested subtasks (`  - [x]`) directly under a completed parent. A subtask under an incomplete parent should NOT be archived.

Count them per area and show a preview:

```
Area           Completed tasks to archive
-----------    ---------------------------
sunbelt        12
planyfi-app     4
```

List the tasks (truncated titles are fine). Ask the user to confirm before proceeding.

## Step 3 — Write to archive

Archive destination: `archive/YYYY-MM/{area}.md` where YYYY-MM is the current month.

- If the archive file doesn't exist, create it with a heading: `# {Area Name} — Archive (YYYY-MM)`
- If it already exists, append to the end
- Append each completed task line exactly as it appears in the task file (preserve indentation, metadata, emoji)
- Keep subtasks grouped under their parent

Use the Edit tool to append to archive files.

## Step 4 — Remove from task files

Use the Edit tool to remove the archived `[x]` lines from each task file. Remove the exact lines — do not leave blank lines where tasks were (one blank line between sections is fine, but don't leave a gap for every removed task).

## Step 5 — Summary

Print a concise summary:
- How many tasks archived per area
- Archive file(s) written to

Then git commit and push silently.
