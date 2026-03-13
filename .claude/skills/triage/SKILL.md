---
name: triage
description: Bulk-assign priorities and due dates to unprioritized tasks
---

You are a chief of staff running a triage session. Read all three task files in parallel using the Read tool:

- `tasks/sunbelt.md`
- `tasks/planyfi-app.md`
- `tasks/planyfi-marketing.md`

Identify all open tasks (`- [ ]`) that do NOT have a priority tag (`[P1]`, `[P2]`, or `[P3]`).

Present unprioritized tasks grouped by area. For each task, suggest:
- **Priority:** P1 (urgent/important), P2 (important), or P3 (low)
- **Due date:** Only if there's a natural deadline (otherwise leave blank)

Prioritization guidelines:
- Sunbelt BoD and reporting items near month/quarter end = P1
- Whitley integration tasks = P2 (ongoing project)
- Planyfi launch blockers = P1, feature work = P2, ideas = P3
- Delegated tasks waiting on others = P2

Present suggestions in a scannable table format. Process in batches of 10-15 if the list is long. Ask the user to confirm or adjust.

After confirmation, use the Edit tool to append the priority tag (and due date if applicable) to each task line in the markdown files. For example, change:
  `- [ ] Some task`
to:
  `- [ ] Some task [P2]`
or:
  `- [ ] Some task [P1] (due: 2026-03-20)`

Keep output terminal-friendly.
