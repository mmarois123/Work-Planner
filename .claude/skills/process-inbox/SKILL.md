---
name: process-inbox
description: Process incoming tasks from Incoming/ folder files or forwarded Gmail emails
---

You are a chief of staff processing the inbox. Handle both file-based and email-based input.

## Determine source

Check if the user specified "email" or just ran `/process-inbox`:
- If **email** → go to Email Flow
- If **no argument** or **files** → go to File Flow

---

## File Flow — Incoming/ folder

Check what's in the Incoming/ folder:

```bash
ls -la Incoming/
```

Read each file using the Read tool. Then parse into tasks (see Parsing Rules below).

Notes:
- BACKLOG.md contains Planyfi tasks (app + marketing)
- Sunbelt Tasks.md contains Sunbelt FP&A tasks
- Skip items in "Shipped" or "Ideas" sections unless explicitly requested

After creating tasks, ask if the user wants to delete the processed files from Incoming/ or keep them for reference.

---

## Email Flow — Gmail

Run the fetch script:

```bash
python scripts/fetch_emails.py --dry-run
```

Use `--dry-run` first so the user can review before marking emails as read.

### Handle errors

- **missing_config** → Print setup instructions:
  1. Copy `.email-config.example` to `.email-config`
  2. Create a Gmail account or use an existing one
  3. Enable 2-Step Verification in Google Account security
  4. Generate an App Password at https://myaccount.google.com/apppasswords
  5. Enable IMAP in Gmail Settings → Forwarding and POP/IMAP
  6. Fill in `.email-config` with your credentials
  7. Test with `python scripts/fetch_emails.py --dry-run`
- **auth_failed** → Tell user to check their app password and that IMAP is enabled
- **connection_failed** → Tell user to check network and IMAP server settings
- **count: 0** → Tell the user no unread emails were found

After tasks are written, mark emails as read:

```bash
python scripts/fetch_emails.py --limit N
```

Where N matches the number of emails processed.

---

## Parsing Rules

For each item, determine:
- **area** — sunbelt / app / marketing
- **section** — within that area
- **title** — clean, concise task title
- **priority** — `[P1]`/`[P2]`/`[P3]` if determinable (ASAP/urgent/EOD → P1; this week deadline → P1; next week → P2; no urgency → leave blank)
- **due_date** — `(due: YYYY-MM-DD)` if mentioned
- **delegated_to** — `@delegated(Name)` if a person is mentioned as owner

Routing signals:
- Bob, Wendy, Marci, Gary, Ron, Jeff, Demi, Frank, Irina, Joy, Dan King, Toni, Robert, Scott → sunbelt
- BoD, board, Whitley, cash flow, 13-week, safety, WIP, AR, AP, reporting → sunbelt
- app, engineering, bug, feature, code, deploy, API → app
- campaign, content, SEO, marketing, launch, website, blog → marketing
- Default: sunbelt/General if ambiguous

Area/section mapping:
- **sunbelt** → `tasks/sunbelt.md` — Sections: BoD, 13 Week Cash Flow, Reporting, Analysis, General
- **app** → `tasks/planyfi-app.md` — Sections: Engineering, Product, Bugs / Issues
- **marketing** → `tasks/planyfi-marketing.md` — Sections: Campaigns, Content, Analytics

---

## Duplicate Check

Before creating tasks, read all three task files in parallel to check for existing tasks with similar titles.

---

## Preview Table

Show for user review:

```
# | Source | Area | Section | Task | Pri | Due | Dup?
```

Flag potential duplicates with `~DUP`. If subtasks were extracted, show them indented under the parent row.

---

## Confirm & Write

Ask the user:
- **Confirm all** — create all tasks as shown
- **Select specific** — pick by number
- **Edit routing** — reassign area/section for specific tasks
- **Cancel** — abort

After confirmation, append each task using the Edit tool:

```
- [ ] Task title [P1] (due: 2026-03-20) @delegated(Name)
```

Only include metadata tags that were actually extracted. Subtasks go as nested `  - [ ]` lines under the parent.

---

## Summary

Print a concise summary: how many items processed, how many tasks created (by area), duplicates skipped.
