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

## 2026-03-23 — Archived
### Engineering
- [x] Add loading indicators to drawers that fetch data async (CurrentPlanDrawer, EventsDrawer, MilestonesDrawer, TargetAllocationDrawer)
- [x] Add toast error notifications to drawer save/delete operations (EventsDrawer, MilestonesDrawer, TransactionsDrawer)
- [x] Add error boundary to main financial-planner page for graceful failure handling
### Product
- [x] Distinguish duplicate plan line-item labels — show person name next to items like "Salary"
- [x] Flag or auto-archive elapsed events in Future Events drawer
- [x] Add tooltips to plan editor line-item icon toolbar
- [x] Improve chart Y-axis scaling in "Real" mode
### Bugs / Issues
- [x] EventTimeline and DetailedProjectionBreakdown return null on empty data
