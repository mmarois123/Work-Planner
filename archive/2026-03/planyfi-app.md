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

## 2026-03-26 — Archived
### Engineering
- [x] Build out in-app notification system
- [x] Trigger notification prompt when future event date elapses
- [x] Onboarding: Make data writes atomic (transaction/rollback on partial failure)
- [x] Onboarding: Fix double-click race condition on handleDemographicsNext
- [x] Onboarding: Add loading indicator during initial guard check
- [x] Onboarding: Await router.push() after submit
- [x] Onboarding: Validate filing status against partner status
- [x] Onboarding: Trim and validate partner name + block zero-income retired users
- [x] Employer match — employerMatchPercent field for 401K/HSA
### Product
- [x] Onboarding: Add inline validation error messages + fix disabled button opacity
- [x] Onboarding: Fix salary placeholder visibility (dark theme)
- [x] Onboarding: Mobile responsive fixes (grid-cols-2, progress bar overflow)
- [x] Onboarding: Minor input/UX polish (negative balances, savings cap, $0 accounts)
- [x] Fix "Life Ex.." label truncation on event timeline
### Bugs / Issues
- [x] Onboarding: Benchmark 50th percentile budget deficit on day 1
- [x] Onboarding: prompt to add partner/dependents for couple/family
- [x] Onboarding: set expenses to Joint by default
- [x] Current Plan: remove option to add Employer Match
- [x] Rename "Guilt-Free Expenses" to "Discretionary Expenses"

## 2026-03-31 — Archived
### Engineering
- [x] Onboarding accessibility — add `aria-label`/`htmlFor` to form inputs, `aria-expanded` on partner checkbox, keyboard support (Tab+Enter) to Demographics percentile table rows
### Product
- [x] Add mortgage calculator: show 30 vs 15 yr vs 5/1 ARM, pull current rates, allow user to adjust overall interest rate to compare impact across loan types
- [x] Enhance home purchase calculator: model after Zillow, add maintenance and other homeownership costs
- [x] Add message to rent vs buy and home buying event: "Renting an equivalent home for $x/month or less would be a better financial decision over 10 years"
- [x] Hide or badge future-event-created accounts ($0 balance) until the event occurs (e.g., "Buy a Home — Mortgage")
- [x] Handling elapsed events — update current plan accordingly
- [x] Remove scenarios from Future Events and all other references in app — scenarios will be handled separately in a future feature
- [x] Make Buy a House event module inputs match the look/feel of Current Plan
- [x] Combine tickers and crypto into a single asset option with a lookup/search function
- [x] Redesign Accounts page to match Current Plan page style: add summary panel on side, allow balance updates at category level or broken out by asset (similar to sub-category breakout), use consistent row icons, add containers for account types/groups
