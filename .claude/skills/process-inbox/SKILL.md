---
name: process-inbox
description: Parse files from the Incoming/ folder into structured tasks
---

You are a chief of staff processing the inbox.

First, check what's in the Incoming/ folder:

```bash
ls -la Incoming/
```

Then read each file in the folder using the Read tool.

Area/section mapping:
- **sunbelt** → `tasks/sunbelt.md` — Sections: BoD, 13 Week Cash Flow, Reporting, Analysis, General
- **app** → `tasks/planyfi-app.md` — Sections: Engineering, Product, Bugs / Issues
- **marketing** → `tasks/planyfi-marketing.md` — Sections: Campaigns, Content, Analytics

For each file in Incoming/, parse the content into actionable tasks. For each task determine:
- **area** — Which area (sunbelt, app, marketing)
- **section** — Which section within that area
- **title** — Clean, concise task title
- **priority** — `[P1]`/`[P2]`/`[P3]` if determinable
- **due_date** — `(due: YYYY-MM-DD)` if a deadline is mentioned
- **delegated_to** — `@delegated(Name)` if a person is mentioned as owner

Before creating tasks, read all three existing task files in parallel to check for duplicates.

Present the parsed tasks in a table:
- # | Source File | Area | Section | Task Title | Priority | Duplicate?

Mark potential duplicates (similar title to existing task in same area/section).

Ask the user to confirm which tasks to create. After confirmation, use the Edit tool to append each new task line (`- [ ] Task title [priority] (due: date) @delegated(Name)`) under the correct `## Section` in the correct area file.

After creating tasks, ask if the user wants to:
- Delete the processed files from Incoming/
- Keep the files for reference

Notes:
- BACKLOG.md contains Planyfi tasks (app + marketing)
- Sunbelt Tasks.md contains Sunbelt FP&A tasks
- Skip items in "Shipped" or "Ideas" sections unless explicitly requested
- Be conservative with duplicates — flag them but don't skip automatically
