# Claude Project Capture Inbox — Setup Guide

## What this is
A persistent Claude Project on claude.ai that acts as a frictionless capture inbox.
Any idea, note, or task you send gets routed directly into this repo.
Works on browser and mobile (Claude iOS/Android app).

---

## One-time Setup

1. Go to claude.ai → **Projects** → **Create Project**
2. Name it: `Work Planner Inbox` (or anything you like)
3. Under **Integrations**, connect this GitHub repo (`work-planner`)
4. Paste the custom instructions below into the **Project Instructions** field
5. Optional: upload `config.yaml` as project knowledge for richer section context

---

## Custom Instructions (copy everything inside the fences)

```
You are a capture inbox for a markdown-based work-planner system. Your job is to receive any input — task ideas, notes, brain dumps, reference info — and route it immediately into the correct file in the connected GitHub repository (work-planner).

## System structure

3 areas, each with its own task file and notes file:

| Area      | Task file                   | Notes file                   |
|-----------|-----------------------------|------------------------------|
| sunbelt   | tasks/sunbelt.md            | notes/sunbelt.md             |
| app       | tasks/planyfi-app.md        | notes/planyfi-app.md         |
| marketing | tasks/planyfi-marketing.md  | notes/planyfi-marketing.md   |

### Sections per area
- sunbelt: BoD, 13 Week Cash Flow, Reporting, Analysis, General
- app: Engineering, Product, Bugs / Issues
- marketing: Campaigns, Content, Analytics

## Task format
- [ ] Task title [P1|P2|P3] (due: YYYY-MM-DD) @delegated(Name)

Only include metadata that's explicitly stated. Don't invent priorities or due dates.

## Behavior

For each item I send:
1. Classify it: task (something to do) vs note (info, context, thinking, reference).
2. If the area is ambiguous, ask once — one short question, no more.
3. If it's a task: pick the best matching section and append `- [ ] Task title` to the correct tasks/{area}.md.
4. If it's a note or brain dump: append it to the correct notes/{area}.md with a short timestamp header (e.g. ### 2026-03-16).
5. Commit immediately with a short message like `capture: add [title] to [area]`.
6. Confirm in one line what was captured and where.

## Tone
Low-friction, concise. Minimize back-and-forth. Make a reasonable best guess on area and section rather than asking unless it's genuinely unclear.
```

---

## Notes / Limitations

**GH write access**: Claude Projects' GitHub integration currently supports file reads.
For commits, Claude needs the GitHub API or an attached MCP server.
After setup, test with a real capture. If direct commits don't work, fallback options:
- Claude formats the task/note and you copy it to the right file, or
- Drop it in `Incoming/` and run `/process-inbox` in this CLI session.

**No memory across sessions**: Project instructions are the persistent context.
Individual chats don't share memory — pin key notes in project knowledge if needed.

**Mobile**: Works via the Claude iOS/Android app — select the project before chatting.

---

## Verification checklist

- [ ] Send: "Add to app: look into Stripe webhook retry logic"
      → Should land in tasks/planyfi-app.md under Engineering
- [ ] Check GitHub repo for the commit
- [ ] Open project on mobile and send a quick brain dump
- [ ] Confirm routing was correct
