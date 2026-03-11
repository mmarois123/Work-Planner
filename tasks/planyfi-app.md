# Planyfi — App

## Engineering
- [ ] Authentication — NextAuth.js, replace client-side userId context with real sessions
- [ ] Provisioning layer — automate per-user Fly.io instance creation via API
- [ ] Custom domain routing — map user.planyfi.app to each user's Fly instance
- [ ] Data export — let users download their SQLite file
- [ ] Remove Dexie.js / IndexedDB dependency (fully replaced by SQLite)
- [ ] Add server-side userId validation (currently client-only)
- [ ] API error handling audit — consistent error shapes across all routes
- [ ] Test coverage — useMultiYearProjection hook
- [ ] Fly.io staging environment
- [ ] Holding price refresh — auto-fetch on load, show staleness indicator
- [ ] Account merge preview — show diff before confirming

## Product
- [ ] Onboarding module — prompt for age, family size, location; auto-populate benchmarks from Census/BLS data; user selects percentile; alternative guided tutorial path
- [ ] Net worth projection validation — audit all NW and accompanying values across future years; establish regression test process
- [ ] Rent vs. Buy Calculator — standalone /rent-vs-buy page
- [ ] Rent vs. Buy — compare two homes by address, or rent vs. buy a single property
- [ ] Rent vs. Buy — TCO for both options (mortgage, taxes, insurance, HOA, maintenance vs. rent + opportunity cost)
- [ ] Rent vs. Buy — pull property data by address (Zillow/Redfin API or manual entry)
- [ ] Rent vs. Buy — surface as linked tool inside Scenario Planner HOME_PURCHASE event and Plan
- [ ] Hero section — net worth projection chart above the fold
- [ ] Scenario cards — sparklines + key metrics (FIRE date, projected NW at 65)
- [ ] Guided wizards — Home Purchase, Coast FIRE, Job Change, Baby, Sabbatical
- [ ] Scenario comparison — side-by-side delta view of two scenarios
- [ ] Milestone events — FINANCIAL_INDEPENDENCE, BABY_BORN with end conditions
- [ ] Interactive NW chart — click a data point to see account breakdown at that date
- [ ] Asset allocation donut — target vs. actual drift indicator
- [ ] Path to FI widget — progress bar + projected date
- [ ] Effective date timeline visualization
- [ ] Income tax summary card — estimated annual burden per plan
- [ ] LLM-powered transaction categorization via Claude API
- [ ] CSV import — support multiple bank formats
- [ ] Recurring transaction detection — flag likely recurring items
- [ ] Mobile-responsive layout pass
- [ ] Shareable scenario links — read-only, time-limited
- [ ] PDF/PNG export of projection charts
- [ ] Quick-compare button — "What if I retire 5 years earlier?"
- [ ] Monte Carlo simulation mode — return variance modeling
- [ ] Interactive demo — hosted read-only instance with sample data
- [ ] Public API for power users

## Bugs / Issues
