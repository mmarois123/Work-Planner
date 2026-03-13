---
name: process-email
description: Fetch forwarded emails from Gmail, parse into tasks
---

You are a chief of staff processing emails that were forwarded to a dedicated task inbox.

## Step 1 — Fetch emails

Run the fetch script:

```bash
python scripts/fetch_emails.py --dry-run
```

Use `--dry-run` first so the user can review before marking emails as read.

### Handle errors

If the output contains `"error"`:
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

If `"count": 0` → Tell the user no unread emails were found in the inbox.

## Step 2 — Parse each email into tasks

For each email in the response, extract:
- **Task title** from subject line (already cleaned of FW:/Re: prefixes)
- **Subtasks** from body — look for numbered lists, bullet points, or multiple action items. If found, create a parent task with nested `  - [ ]` subtasks
- **Area/section** using routing rules (same as /add-task):
  - Mentions of Bob, Wendy, Marci, Gary, Ron, Jeff, Demi, Frank, Irina, Joy, Dan King, Toni, Robert, Scott → sunbelt
  - Mentions of BoD, board, Whitley, cash flow, 13-week, safety, WIP, AR, AP, reporting → sunbelt (match to appropriate section)
  - Mentions of app, engineering, bug, feature, code, deploy, API → app
  - Mentions of campaign, content, SEO, marketing, launch, website, blog → marketing
  - Default: sunbelt/General if ambiguous
  - `original_sender_name` is a strong routing signal — match against People Directory
- **Priority** — infer from urgency language ("ASAP", "urgent", "EOD", "critical" → P1; deadlines this week → P1; deadlines next week → P2; no urgency → leave blank)
- **Due date** — extract explicit dates from the body, convert to `(due: YYYY-MM-DD)`
- **Delegation** — if someone is mentioned as the owner/assignee, use `@delegated(Name)`

Area/section mapping:
- **sunbelt** → `tasks/sunbelt.md` — Sections: BoD, 13 Week Cash Flow, Reporting, Analysis, General
- **app** → `tasks/planyfi-app.md` — Sections: Engineering, Product, Bugs / Issues
- **marketing** → `tasks/planyfi-marketing.md` — Sections: Campaigns, Content, Analytics

## Step 3 — Duplicate check

Read all three task files in parallel to check for existing tasks with similar titles or content.

## Step 4 — Preview

Show a table for user review:

```
# | Email Subject | Area | Section | Task | Pri | Due | Dup?
```

Flag potential duplicates with `~DUP` in the last column.

If subtasks were extracted, show them indented under the parent task row.

## Step 5 — Confirm

Ask the user:
- **Confirm all** — create all tasks as shown
- **Select specific** — user picks which tasks to create (by number)
- **Edit routing** — user can reassign area/section for specific tasks
- **Cancel** — abort without creating anything

## Step 6 — Write tasks

After confirmation, use the Edit tool to append each task line under the correct `## Section` in the correct area file. Format:

```
- [ ] Task title [P1] (due: 2026-03-20) @delegated(Name)
```

Only include metadata tags that were actually extracted. Subtasks go as nested `  - [ ]` lines under the parent.

## Step 7 — Mark emails as read

After tasks are written, run the fetch script again without `--dry-run` to mark the processed emails as read:

```bash
python scripts/fetch_emails.py --limit N
```

Where N matches the number of emails that were just processed.

## Step 8 — Summary

Print a concise summary:
- How many emails processed
- How many tasks created (and in which areas)
- Any duplicates that were skipped
