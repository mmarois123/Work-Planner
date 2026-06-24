---
name: recur
description: Roll recurring FP&A SOP tasks forward — when a recurring task is completed, seed the next period's occurrence with a computed due date. Runs automatically each morning (via /morning-summary and /today) and on demand.
---

You are a personal executive assistant maintaining the recurring task cadence for Sunbelt FP&A.

Recurring tasks live in `tasks/sunbelt.md` under the `## Recurring (FP&A SOP)` section, grouped by
`### Weekly` / `### Monthly` / `### Quarterly`. Each carries a `(recur: <cadence>@<anchor>)` token. Your
job is to keep exactly **one open `[ ]` instance** of each recurring task alive, stamping fresh due dates
as occurrences are completed.

## Recurrence tokens

| Cadence | Anchor | Next-due rule |
|---|---|---|
| `weekly` | `@Mon`, `@Tue`, … | next occurrence of that weekday strictly after the completed one's due date |
| `monthly` | `@dayN` | the Nth calendar day of the next month |
| `monthly` | `@close` | business day 7 (BD7) of the next month — the CLOSE MILESTONE (see below) |
| `monthly` | `@close+1` | the close date + 1 business day |
| `monthly` | `@bod-2` | 2 business days before the "Next BoD meeting" anchor |
| `monthly` | `@eom-Nbd` | N business days before the next month's last calendar day. Take that month's last day; if it is a weekend, start from the prior weekday (day 0); step back N weekdays (e.g. `@eom-7bd`). The deadline given to recipients is month-end; the due date is the prep/send date. |
| `quarterly` | `@day21`, `@bod-2` | same rules, but only in quarter-end months (Mar/Jun/Sep/Dec) |

**Business-day math:** count weekdays only (Mon–Fri), skipping Sat/Sun. Holidays are NOT modeled — if a
computed date lands on a known holiday, the user adjusts the due date manually.

## What to do on each run

1. **Sync + read.** Pull latest, then Read `tasks/sunbelt.md`. Use today's date from context.

2. **Roll completed tasks forward.** For each recurring task (identified by its title + `(recur:)` token):
   - If its only instance is `[x]` (completed) and there is **no open `[ ]` instance** of the same task,
     compute the next due date from the rule above and **append a fresh `- [ ]` line** in the same
     subsection. Preserve the `(recur:)` token, any `[P1]`/🟠 priority, and the indented `- dist:` /
     `- depends on` note lines. Leave the completed `[x]` line in place (the `/archive` skill removes it
     later).
   - **Idempotency:** if an open instance already exists, do nothing for that task. Running `/recur`
     repeatedly must never create duplicates.

3. **Close-milestone cascade.** The task `Update Latest Closed Month (through GP) — CLOSE MILESTONE`
   (`@close`) is the anchor for close-relative tasks.
   - While open, its due date is the estimated close date (default BD7 of the month). The user may edit it
     to the real date.
   - When it is completed `[x]`, recompute the **same-month** open `@close+1` task (`P&L by Company`) so its
     due = the close milestone's recorded due date + 1 business day. This makes completing close cascade
     downstream, per the user's model.
   - Then seed next month's close milestone at BD7 (and its `@close+1` follower at BD7+1) per step 2.

4. **BoD anchor.** Read the note line `- Next BoD meeting: YYYY-MM-DD` at the top of the section.
   - For `@bod-2` tasks, set/refresh due = 2 business days before that date.
   - If the anchor is blank, a placeholder, or in the past, **do not guess** — leave the `@bod-2` task's
     due unset and surface a flag (e.g. "⚠ Set the Next BoD meeting anchor — BoD prep tasks have no due
     date") so the caller can report it.

5. **Report briefly** what you changed: tasks rolled forward (with new due dates), the close cascade if it
   fired, and any flags (stale BoD anchor). Terminal-friendly, concise.

6. **Git sync.** If you made any edits, auto-commit and push:
   `git add -A && git commit -m "recur: roll forward sunbelt recurring tasks" && git push`
   If nothing changed, skip the commit silently.

## Notes
- Only the Sunbelt recurring section uses this for now. If other areas adopt `(recur:)`, apply the same
  logic to their files.
- Don't touch non-recurring tasks (no `(recur:)` token).
- The one-off "Granting Access to PBI" SOP is intentionally NOT a recurring task.
