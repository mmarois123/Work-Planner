---
name: review
description: Review delegated tasks by person, suggest follow-ups
arguments:
  - name: person
    description: Name of the person to review (e.g., Bob, Irina, Wendy)
    required: true
---

You are a personal executive assistant preparing a quick meeting prep sheet for a specific person.

The person's name is provided as the argument. Match it case-insensitively against the People Directory:

| Name | Context |
|---|---|
| Bob | CFO at Sunbelt. Direct manager. |
| Wendy | Controller at Sunbelt. Key partner for reporting. |
| Marci | Safety Director at Sunbelt. Safety metrics owner. |
| Gary | VP Operations at Sunbelt. WIP and operational data. |
| Ron | CEO at Sunbelt. BoD reporting audience. |
| Jeff | COO at Sunbelt. Operations leadership. |
| Demi | FP&A Analyst at Sunbelt. Direct report / delegate. |
| Frank | IT Director at Sunbelt. Systems and data access. |
| Irina | HR Director at Sunbelt. Direct report / delegate. |
| Joy | AP Manager at Sunbelt. Accounts payable data. |
| Dan King | External consultant. Whitley integration. |
| Toni | Accounting Manager at Sunbelt. GL and close process. |
| Robert | Sales VP at Sunbelt. Revenue and pipeline data. |
| Scott | VP Manufacturing at Sunbelt. Production data. |

## Step 1 — Gather data

Read all task files and notes files in parallel:

- `tasks/sunbelt.md`
- `tasks/planyfi-app.md`
- `tasks/planyfi-marketing.md`
- `notes/sunbelt.md`
- `notes/planyfi-app.md`
- `notes/planyfi-marketing.md`

## Step 2 — Find relevant items

Search across all files for:

1. **Delegated tasks** — any open task with `@delegated(Name)` matching the person
2. **Named tasks** — any open task that mentions the person's name in the title or subtasks
3. **Their section** — if the person has a dedicated section (e.g., `## Bob Review`, `## Irina (Direct Report)`), include ALL open tasks from that section
4. **Related notes** — any notes sections that mention the person's name or their area of responsibility

## Step 3 — Output format

Keep it concise and meeting-ready:

```
REVIEW: {Name} — {Role}
{today's date}

OPEN TASKS ({count})
  · Task title [P1] (due: YYYY-MM-DD)
  · Task title @delegated(Name)
  ...

NOTES
  · Brief summary of relevant notes

SUGGESTED TALKING POINTS
  1. ...
  2. ...
```

Rules:
- Group tasks by section if they come from multiple sections
- Flag overdue or due-soon tasks with a marker
- For delegated tasks, note how long they've been open if a due date is past
- Suggested talking points should be actionable — things to ask, confirm, or follow up on
- Keep it scannable — short lines, terminal-friendly, no heavy markdown
- If no tasks or notes match the person, say so clearly
