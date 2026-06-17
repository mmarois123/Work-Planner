# Notch

## Engineering

- [ ] Tailscale setup — configure the Windows PC for Tailscale access so the phone can reach Notch over the tailnet; document in README
- [ ] NSSM Windows service — create and document the NSSM service definition so Notch auto-starts on boot
- [ ] Git-commit daily journals — automate `data/logs/YYYY-MM-DD.md` git commits (cron or on-write hook)
- [ ] Fitbit poller resilience — handle token refresh failures gracefully; surface last-sync status in /api/health
- [ ] Database backup strategy — periodic SQLite backup (cp or `.backup` command) to a second location

## Product

- [ ] Conversational analysis endpoint — "how's my week", "what should I eat to hit protein", "find days I PRed bench" — spawns Claude with tool restrictions, streams to chat drawer
- [ ] Weekly auto-reflection — italic editorial blurb generated for the History view summarizing the week's data
- [ ] Phone-optimized frontend tweaks — touch targets, drawer sizing, bottom nav for mobile Tailscale use
- [x] Meal editing — ability to edit or delete a confirmed meal entry (currently no edit/delete after confirm)
- [ ] History tab: monthly view — the History tab supports 7d/14d/30d/90d timeframes but no calendar-month view
- [ ] Export — CSV or JSON export of meal logs, body metrics, and workouts for a date range
- [ ] Multi-day Fitbit backfill UI — button in frontend to trigger a Fitbit sync for a specific date range (currently auto-polls recent days only)
- [ ] Build Claude chat interface (similar to work planner) for capturing complex nutrition entries to paste into Notch; explore alternative approaches to same problem

## Bugs / Issues
- [x] Streak logic: don't count current day unless already completed; streak breaks if previous day was missed

## General
- [x] Add ability to remove sets in Notch
- [x] Rename workouts: MAPS 15 Advanced 3.1, 3.2, etc.
- [x] Add ability to replace exercises
- [x] Full edit capability during active workout
- [x] Auto-highlight numbers when tapping input boxes during workout
- [ ] Replace MAPS program view on main Train page with full workout list; show recent workouts by default with search; move PDFs to reference attachments on workouts or a separate menu
