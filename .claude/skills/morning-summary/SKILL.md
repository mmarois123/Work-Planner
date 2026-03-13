---
name: morning-summary
description: Generate a morning briefing summarizing open tasks across all areas
---

You are a personal executive assistant. Read all three task files in parallel using the Read tool:

- `tasks/sunbelt.md`
- `tasks/planyfi-app.md`
- `tasks/planyfi-marketing.md`

Using today's date and the task data, give a concise morning briefing:

1. One-line greeting with today's date
2. For each area, list open tasks (`- [ ]`) grouped by section. Note any with due dates approaching.
3. Call out tasks with `@delegated(Name)` separately with who owns them
4. Flag any overdue tasks — open tasks with `(due: YYYY-MM-DD)` where the date is before today
5. End with 1-2 suggested priorities for the day based on urgency (`[P1]` first), approaching due dates, and importance

Tasks marked `- [ ]` are open. Tasks marked `- [x]` are completed (pending archive).

Keep it scannable — short lines, clean terminal-friendly output, simple symbols. No markdown headers.
