# Notch — Archive (2026-05)

## Engineering
- [x] Parser cache persistence — the in-process LLM parser cache (24h TTL) doesn't survive restarts; consider SQLite-backed cache
- [x] OFF serving_g fallback — when OFF entry has no serving_g, fall back to LLM-estimated grams instead of silently using None
- [x] Alias default_grams audit — review whether aliases written with midpoint grams (from ranges) cause drift on repeat captures
- [x] Error monitoring — structured logging or lightweight error tracking (Sentry-free) for production use
- [x] Test coverage for shortcuts service — `services/shortcuts.py` has 227 lines; expand edge-case tests (duplicate names, bucket boundaries)
- [x] Quick capture: shortcut source — quick capture supports usda/off sources but shortcut-based quick items need integration testing end-to-end

## Product
- [x] Targets management UI — set/update daily macro targets from the frontend (currently requires direct DB insert)
- [x] Shortcut management UI — view, edit, reorder, and delete shortcuts from the frontend (currently API-only CRUD)
- [x] Streak tracking — surface current and best streaks for habits (logged food, workout, protein target hit, etc.)
- [x] Add max streak tracking to Notch

## Bugs / Issues
- [x] CRLF warnings on every commit — git warns about LF→CRLF replacement on Windows; configure `.gitattributes` to normalize
- [x] Fitbit callback test was asserting 401 for an auth-exempt route — fixed in latest commit, but review other auth tests for similar staleness
