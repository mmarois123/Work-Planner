# Notch — Archive (2026-06)

- [x] Tailscale setup — configure the Windows PC for Tailscale access so the phone can reach Notch over the tailnet; document in README
- [x] NSSM Windows service — create and document the NSSM service definition so Notch auto-starts on boot
- [x] Fitbit poller resilience — handle token refresh failures gracefully; surface last-sync status in /api/health
- [x] Database backup strategy — periodic SQLite backup (cp or `.backup` command) to a second location
- [x] Phone-optimized frontend tweaks — touch targets, drawer sizing, bottom nav for mobile Tailscale use
- [x] Meal editing — ability to edit or delete a confirmed meal entry (currently no edit/delete after confirm)
- [x] History tab: monthly view — the History tab supports 7d/14d/30d/90d timeframes but no calendar-month view
- [x] Export — CSV or JSON export of meal logs, body metrics, and workouts for a date range
- [x] Multi-day Fitbit backfill UI — button in frontend to trigger a Fitbit sync for a specific date range (currently auto-polls recent days only)
- [x] Streak logic: don't count current day unless already completed; streak breaks if previous day was missed
- [x] Add ability to remove sets in Notch
- [x] Rename workouts: MAPS 15 Advanced 3.1, 3.2, etc.
- [x] Add ability to replace exercises
- [x] Full edit capability during active workout
- [x] Auto-highlight numbers when tapping input boxes during workout
- [x] Replace MAPS program view on main Train page with full workout list; show recent workouts by default with search; move PDFs to reference attachments on workouts or a separate menu
