# Planyfi — App

## Engineering
- [ ] Authentication — NextAuth.js, replace client-side userId context with real sessions
- [ ] Provisioning layer — automate per-user Fly.io instance creation via API
- [ ] Custom domain routing — map user.planyfi.app to each user's Fly instance
- [ ] Data export — let users download their SQLite file
- [x] Remove Dexie.js / IndexedDB dependency (fully replaced by SQLite)
- [ ] Add server-side userId validation (currently client-only)
- [ ] API error handling audit — consistent error shapes across all routes
- [ ] Fly.io staging environment
- [ ] Holding price refresh — auto-fetch on load, show staleness indicator
- [x] Test coverage — useMultiYearProjection hook

## Product
- [ ] Onboarding module — prompt for age, family size, location; auto-populate benchmarks from Census/BLS data; user selects percentile; alternative guided tutorial path
- [ ] Rent vs. Buy Calculator — standalone /rent-vs-buy page
- [ ] Rent vs. Buy — compare two homes by address, or rent vs. buy a single property
- [ ] Rent vs. Buy — TCO for both options (mortgage, taxes, insurance, HOA, maintenance vs. rent + opportunity cost)
- [ ] Rent vs. Buy — pull property data by address (Zillow/Redfin API or manual entry)
- [ ] Rent vs. Buy — surface as linked tool inside Scenario Planner HOME_PURCHASE event and Plan
- [ ] Hero section — net worth projection chart above the fold
- [ ] Guided wizards — Home Purchase
- [ ] Scenario comparison — side-by-side delta view of two scenarios
- [ ] Mobile-responsive layout pass
- [ ] Quick-compare button — "What if I retire 5 years earlier?"
- [ ] Monte Carlo simulation mode — return variance modeling
- [ ] Interactive demo — hosted read-only instance with sample data
- [x] Net worth projection validation — audit all NW and accompanying values across future years; establish regression test process
- [x] Interactive NW chart — click a data point to see account breakdown at that date
- [x] Effective date timeline visualization

## Bugs / Issues
