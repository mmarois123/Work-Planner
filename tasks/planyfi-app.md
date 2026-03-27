# Planyfi — App

## Engineering
- [ ] Provisioning layer — automate per-user Railway instance creation via API
- [ ] Custom domain routing — map user.planyfi.app to each user's Railway instance
- [ ] Railway staging environment
- [ ] Accessibility pass — add keyboard handlers to backdrop overlays, aria-labels to icon-only buttons, keyboard support to clickable table rows
- [ ] Data export — let users download their SQLite file
- [ ] Onboarding accessibility — add `aria-label`/`htmlFor` to form inputs, `aria-expanded` on partner checkbox, keyboard support (Tab+Enter) to Demographics percentile table rows
- [ ] Add CSV import error handling in TransactionsDrawer — catch malformed files and show user feedback

## Product
- [ ] Add mortgage calculator: show 30 vs 15 yr vs 5/1 ARM, pull current rates, allow user to adjust overall interest rate to compare impact across loan types
- [ ] Enhance home purchase calculator: model after Zillow, add maintenance and other homeownership costs
- [ ] Research (via Claude) what mortgage info a homeowner typically has access to — use to inform current plan input fields
- [ ] Add message to rent vs buy and home buying event: "Renting an equivalent home for $x/month or less would be a better financial decision over 10 years"
- [ ] Add calculator section: rent vs buy, buy a home, estimated taxes — pull from current plan inputs with ability to adjust and see quick impact
- [ ] Rent vs. Buy — compare two homes by address, or rent vs. buy a single property
- [ ] Rent vs. Buy — pull property data by address (Zillow/Redfin API or manual entry)
- [ ] Rent vs. Buy — surface as linked tool inside Scenario Planner HOME_PURCHASE event and Plan
- [ ] Scenario comparison — side-by-side delta view of two scenarios
- [ ] Mobile-responsive layout — full mobile compatibility pass across all pages and components; touch-friendly interactions throughout
- [ ] Integrate US census data more deeply into app
- [ ] Add view mode for filtering/browsing different demographics
- [ ] Quick-compare button — "What if I retire 5 years earlier?"
- [ ] Monte Carlo simulation mode — return variance modeling
- [ ] Interactive demo — hosted read-only instance with sample data
- [ ] Add contact, submit feedback, and support functionality to app
- [ ] Hide or badge future-event-created accounts ($0 balance) until the event occurs (e.g., "Buy a Home — Mortgage")
- [ ] Onboarding module improvements — refine UX and flows as design evolves

## Bugs / Issues
