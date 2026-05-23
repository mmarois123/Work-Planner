# Notch

## Engineering

- [ ] Tailscale setup — configure the Windows PC for Tailscale access so the phone can reach Notch over the tailnet; document in README
- [ ] NSSM Windows service — create and document the NSSM service definition so Notch auto-starts on boot
- [ ] Git-commit daily journals — automate `data/logs/YYYY-MM-DD.md` git commits (cron or on-write hook)
- [x] Parser cache persistence — the in-process LLM parser cache (24h TTL) doesn't survive restarts; consider SQLite-backed cache
- [x] OFF serving_g fallback — when OFF entry has no serving_g, fall back to LLM-estimated grams instead of silently using None
- [x] Alias default_grams audit — review whether aliases written with midpoint grams (from ranges) cause drift on repeat captures
- [ ] Error monitoring — structured logging or lightweight error tracking (Sentry-free) for production use
- [ ] Fitbit poller resilience — handle token refresh failures gracefully; surface last-sync status in /api/health
- [ ] Database backup strategy — periodic SQLite backup (cp or `.backup` command) to a second location
- [ ] Test coverage for shortcuts service — `services/shortcuts.py` has 227 lines; expand edge-case tests (duplicate names, bucket boundaries)
- [ ] Quick capture: shortcut source — quick capture supports usda/off sources but shortcut-based quick items need integration testing end-to-end

## Product

- [ ] Conversational analysis endpoint — "how's my week", "what should I eat to hit protein", "find days I PRed bench" — spawns Claude with tool restrictions, streams to chat drawer
- [ ] Weekly auto-reflection — italic editorial blurb generated for the History view summarizing the week's data
- [ ] Phone-optimized frontend tweaks — touch targets, drawer sizing, bottom nav for mobile Tailscale use
- [ ] Meal editing — ability to edit or delete a confirmed meal entry (currently no edit/delete after confirm)
- [x] Targets management UI — set/update daily macro targets from the frontend (currently requires direct DB insert)
- [ ] Shortcut management UI — view, edit, reorder, and delete shortcuts from the frontend (currently API-only CRUD)
- [ ] History tab: monthly view — the History tab supports 7d/14d/30d/90d timeframes but no calendar-month view
- [ ] Streak tracking — surface current and best streaks for habits (logged food, workout, protein target hit, etc.)
- [ ] Add max streak tracking to Notch
- [ ] Export — CSV or JSON export of meal logs, body metrics, and workouts for a date range
- [ ] Multi-day Fitbit backfill UI — button in frontend to trigger a Fitbit sync for a specific date range (currently auto-polls recent days only)

## Bugs / Issues

- [x] CRLF warnings on every commit — git warns about LF→CRLF replacement on Windows; configure `.gitattributes` to normalize
- [x] Fitbit callback test was asserting 401 for an auth-exempt route — fixed in latest commit, but review other auth tests for similar staleness
