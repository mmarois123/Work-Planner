# Planyfi App — Archive (2026-03)

## Engineering
- [x] Remove Dexie.js / IndexedDB dependency (fully replaced by SQLite)
- [x] Holding price refresh — auto-fetch on load, show staleness indicator
- [x] Test coverage — useMultiYearProjection hook

## Product
- [x] Rent vs. Buy Calculator — standalone /rent-vs-buy page
- [x] Rent vs. Buy — TCO for both options (mortgage, taxes, insurance, HOA, maintenance vs. rent + opportunity cost)
- [x] Guided wizards — Home Purchase
- [x] Net worth projection validation — audit all NW and accompanying values across future years; establish regression test process
- [x] Interactive NW chart — click a data point to see account breakdown at that date
- [x] Effective date timeline visualization

## 2026-03-17 — Completed
- [x] Authentication — Clerk, replace client-side userId context with real sessions
- [x] Add server-side userId validation (via Clerk auth() in all API routes)
- [x] API error handling audit — consistent error shapes across all routes
- [x] Onboarding module — prompt for age, family size, location; auto-populate income/expense/savings benchmarks from US Census / BLS data (baked in at build time); user selects percentile (25th, median, 75th, 90th); alternative path to start from scratch with guided tutorial through accounts setup and current plan setup
- [x] Input field auto-select — all numeric and text inputs highlight on focus for faster editing
