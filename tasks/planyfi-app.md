# Planyfi — App

## Engineering
- [ ] Review hidden debug sections (ProjectionVerificationTable, DetailedProjectionBreakdown) — decide keep or delete (by 2026-04-11)
- [ ] Provisioning layer — automate per-user Railway instance creation via API
- [ ] Custom domain routing — map user.planyfi.app to each user's Railway instance
- [ ] Railway staging environment
- [ ] Accessibility pass — add keyboard handlers to backdrop overlays, aria-labels to icon-only buttons, keyboard support to clickable table rows
- [ ] Data export — let users download their SQLite file

- [ ] Add CSV import error handling in TransactionsDrawer — catch malformed files and show user feedback
- [ ] Add retry logic or user-facing toast for transient API failures in repository layer (e.g. scenarioEventsRepo.getByScenario) — currently throws and logs to console only
- [ ] Refactor TransactionsDrawer add-transaction from modal to inline form for consistency with other drawers
- [ ] Unify edit mode state management across drawers (editingId pattern vs mode-based vs boolean)

## Product
- [ ] Research (via Claude) what mortgage info a homeowner typically has access to — use to inform current plan input fields

- [ ] Add calculator section: rent vs buy, buy a home, estimated taxes — pull from current plan inputs with ability to adjust and see quick impact
- [ ] Rent vs. Buy — compare two homes by address, or rent vs. buy a single property
- [ ] Home Purchase — zip code lookup for median home price, county-level property tax, flood/wind insurance zones
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

- [ ] Onboarding module improvements — refine UX and flows as design evolves

- [ ] Add refinance mortgage / other debt as a future event type
- [ ] Tighten up home buying and tracking in future events, accounts, and current plan
- [ ] Finalize onboarding modules with 3 paths
- [ ] Update Milestones module
- [ ] Update event timeline
- [ ] Allow users to enter plan numbers at high-level category (Investments, Fixed, Discretionary) instead of requiring category or account level detail
- [ ] Explore bulk update option for assets
- [ ] Update FI Calculator section on financial planner page — evaluate if still needed, brainstorm improvements
- [ ] Rework Fund Strategy deficit logic: remove forced 2-step order (reduce contributions → withdrawal); allow user to mix and match order; explore situation-based configuration
- [ ] Update Asset Allocation report: show variances between target and current allocations; add ability to include/exclude accounts (e.g. exclude checking/savings); simplify Tax Status chart with focus on asset allocation; brainstorm additional improvements
- [ ] Add recurring transactions to accounts/holdings — auto-approximate periodic additions (weekly/monthly) without manual entry; show Estimated Balance vs Latest Balance (consistent with checking/savings approach)

## Bugs / Issues
- [ ] Irina: document Fabric Lakehouse issue — table not ready after loading @delegated(Irina)
