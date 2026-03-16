# Planyfi — App

## Engineering
- [ ] Authentication — NextAuth.js, replace client-side userId context with real sessions
- [ ] Provisioning layer — automate per-user Fly.io instance creation via API
- [ ] Custom domain routing — map user.planyfi.app to each user's Fly instance
- [ ] Data export — let users download their SQLite file
- [ ] Add server-side userId validation (currently client-only)
- [ ] API error handling audit — consistent error shapes across all routes
- [ ] Fly.io staging environment

## Product
- [ ] Onboarding module — prompt for age, family size, location; auto-populate income/expense/savings benchmarks from US Census / BLS data (baked in at build time); user selects percentile (25th, median, 75th, 90th); alternative path to start from scratch with guided tutorial through accounts setup and current plan setup
- [ ] Onboarding module improvements — refine UX and flows as design evolves
- [ ] Rent vs. Buy — compare two homes by address, or rent vs. buy a single property
- [ ] Rent vs. Buy — pull property data by address (Zillow/Redfin API or manual entry)
- [ ] Rent vs. Buy — surface as linked tool inside Scenario Planner HOME_PURCHASE event and Plan
- [ ] Hero section — net worth projection chart above the fold
- [ ] Scenario comparison — side-by-side delta view of two scenarios
- [ ] Mobile-responsive layout — full mobile compatibility pass across all pages and components; touch-friendly interactions throughout
- [ ] Input field auto-select — all numeric and text inputs highlight on focus for faster editing; especially important in Plan and Accounts where users frequently overwrite values
- [ ] Quick-compare button — "What if I retire 5 years earlier?"
- [ ] Monte Carlo simulation mode — return variance modeling
- [ ] Interactive demo — hosted read-only instance with sample data

## Bugs / Issues
