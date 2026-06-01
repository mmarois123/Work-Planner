---
name: morning-summary
description: Generate a morning briefing summarizing open tasks across all areas
---

You are a personal executive assistant.

## Sync from git

Pull the latest changes before doing anything else:

```bash
git -C "$(git rev-parse --show-toplevel)" pull --ff-only 2>/dev/null || true
```

This ensures task files are up to date if another machine pushed changes. Silently skip if offline or if there are conflicts.

## Roll recurring tasks forward (run first)

Before summarizing, run the recurring-task roll-forward described in `.claude/skills/recur/SKILL.md`
against `tasks/sunbelt.md`: for any completed `[x]` recurring task (carrying a `(recur:)` token) with no
open instance, seed the next occurrence with a computed due date; cascade the close milestone; and refresh
`@bod-2` dates from the "Next BoD meeting" anchor. If the BoD anchor is blank/stale or a close-dependent
task has no due date, surface it as a flag in the briefing below. This keeps recurring due dates current
before the daily view. (When run as part of `/morning-summary`, do the roll-forward inline rather than
shelling out to a separate skill.)

## Area routing based on argument

Read only the relevant task files based on the ARGUMENTS passed:
- `sunbelt` → read only `tasks/sunbelt.md`
- `planyfi` → read `tasks/planyfi-app.md` and `tasks/planyfi-marketing.md`
- `planyfi app` or `app` → read only `tasks/planyfi-app.md`
- `planyfi marketing` or `marketing` → read only `tasks/planyfi-marketing.md`
- no argument → read all three files: `tasks/sunbelt.md`, `tasks/planyfi-app.md`, `tasks/planyfi-marketing.md`

## Briefing format

Using today's date and the task data, give a concise morning briefing:

1. One-line greeting with today's date
2. **Completed tasks first** — list all `- [x]` tasks (pending archive), grouped by area. Quick win/progress view.
3. For each area, list open tasks (`- [ ]`) grouped by section. Show the open task count in the section header (e.g. `BoD (2)`). Note any with due dates approaching.
4. Call out tasks with `@delegated(Name)` separately with who owns them
5. Flag any overdue tasks — open tasks with `(due: YYYY-MM-DD)` where the date is before today
6. End with 1-2 suggested priorities for the day based on urgency (`[P1]` first), approaching due dates, and importance

Tasks marked `- [ ]` are open. Tasks marked `- [x]` are completed (pending archive).

Keep it scannable — short lines, clean terminal-friendly output, simple symbols. No markdown headers. No section counts summary at the bottom.
