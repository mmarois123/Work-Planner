# Planyfi — App

## Engineering

### Free tier / monetization (prerequisite for public beta)
Business model: Free tier is session-only (full feature access, no persistence). Premium ($5/mo or $50/yr) unlocks save, scenario comparison, unlimited saved scenarios, CSV export, priority support.
### Infrastructure / ops (before inviting friends)
- [~] ~~Stripe account setup~~ — REPLACED with Clerk Billing (migrated May 2026)
### Deferred / reconsidered
- [~] ~~Provisioning layer — automate per-user Railway instance creation via API~~ — DROPPED. Shared multi-tenant SQLite + Clerk userId scoping already covers isolation. Per-instance economics kill $5/mo margin. Revisit only as Enterprise tier.
- [~] ~~Custom domain routing — map user.planyfi.app to each user's Railway instance~~ — DROPPED with the above.
- [~] ~~Data export — let users download their SQLite file~~ — REPLACED with per-user JSON export (SQLite file would leak other users' data in shared-DB model).

## Product
- [ ] Add calculator section: rent vs buy, buy a home, estimated taxes — pull from current plan inputs with ability to adjust and see quick impact
- [ ] Rent vs. Buy — compare two homes by address, or rent vs. buy a single property
- [ ] Home Purchase — zip code lookup for median home price, county-level property tax, flood/wind insurance zones
- [ ] Rent vs. Buy — pull property data by address (Zillow/Redfin API or manual entry)
- [ ] Rent vs. Buy — surface as linked tool inside Scenario Planner HOME_PURCHASE event and Plan
- [>] Integrate US census data more deeply into app
- [>] Add view mode for filtering/browsing different demographics
- [ ] 🟠 Send beta version to Zach, Julie, AJ, James, and others (blocked on: session-only free tier + backups + error monitoring)
- [ ] Add recurring transactions to accounts/holdings — auto-approximate periodic additions (weekly/monthly) without manual entry; show Estimated Balance vs Latest Balance (consistent with checking/savings approach)
- [ ] Scenario Comparison feature: ability to hide/adjust Current Plan, Events, Milestones, Market Assumptions; full plan summary/net worth for a given year; line chart plotting net worth, income, expenses for up to 3 scenarios
- [ ] Add button that generates a generic LLM prompt — instructs any AI tool to review attached transactions and categorize them against the user's current plan (specific categories + sub-categories) in a format uploadable to Planyfi for plan comparison or updates
- [ ] Review Fund Strategy and Roth Conversion Ladder — verify accuracy, defaults, and quality of explanations
- [x] Research available US datasets for household income, saving/investing, and spending — delivered themed HTML report at design-mockups/us-data-report.html
- [ ] Add help/info icons to each drawer/page with in-depth explanations; explore on-screen tutorial as well
- [>] Add insights to Current Plan page: hover/tap to see typical US household spend by category with user comparison; show impact of reducing expenses or increasing contributions on net worth
- [ ] Reframe Current Plan as standalone input feature; Financial Planner shows the output/results — make the distinction clearer in UX
- [ ] Add multiple lines to net worth chart based on different market performance assumptions (e.g. 6% vs 7%)

### Design Review (Apr 2026)
Source: Claude Design review of Planner, Accounts, Current Plan, Events, Milestones, and Net Worth surfaces. Quick wins first: #03, #06, #05, #09 (all S effort). Net Worth order: A → E → B → D → C.

**Planner**
- [ ] Allocation drift panel — show top 3 drifted asset classes (actual vs. target bars) in Net Worth summary rail; rebalance recommendation line [S effort, Med leverage]

**Accounts**

**Drawers (Current Plan / Events / Milestones)**
**Net Worth chart deep dive**
- [ ] Narrative annotations — auto-detect peak, FI crossover, drawdown start; place type-on-chart labels with sentences; max 4 visible, toggleable [S effort, Med leverage]

## Security

## Engineering (New User Experience)

## Bugs / Issues
- [>] Credit card UI broken/poor on mobile; replace with "Add credit card" flow similar to adding holdings, then prompt for details
- [x] Home Purchase event summary renders `"$NaN home, undefined% down, undefined% rate, 3% appreciation"` in the Future Events drawer card. Seen on a fresh Quick Setup demo plan (seeded HOME_PURCHASE event) — home price / down payment / rate fields come through undefined when the event is auto-seeded rather than user-entered. Likely the seeded composite payload is missing fields the card summary reads, or the summary doesn't guard against undefined.

## Parking Lot
- [ ] Scratch-pad what-if scrubbers — live sliders (retirement age, savings rate, return, home price) overlay a ghost projection on the chart; delta readout vs. saved plan; "Save as event" to persist [M effort, High leverage]
- [ ] Event impact sparklines — 180×40px sparkline per event card showing projection-with minus projection-without; magnitude number (+$412k at FI); left-border color by event type [M effort, High leverage]
- [ ] Confidence band — fan chart with p10/p50/p90; Phase 1: deterministic ±1.5σ; Phase 2: Monte Carlo [M effort, High leverage]
- [ ] Data export (JSON) for Premium — per-user server-side export endpoint — DEFERRED, not needed for beta
- [ ] Add CSV import error handling in TransactionsDrawer — catch malformed files and show user feedback — DEFERRED, low priority
- [ ] Zillow ZORI/ZHVI by ZIP code — download monthly CSV (~50MB), serve via API route for ZIP-level rent/home value benchmarks in onboarding and rent-vs-buy calculator [M effort, High leverage] — POST-BETA
- [ ] FRED API integration — pull live savings rate (PSAVERT), 30-yr mortgage rate, PCE inflation at runtime; cache daily with hardcoded fallbacks [M effort, Med leverage] — POST-BETA
- [ ] Census ACS API — ZIP-level income percentile comparisons ("you earn more than X% of households in your ZIP"); free REST API with caching [M effort, Med leverage] — POST-BETA
- [ ] SSA benefit formula — implement PIA calculation (90%/32%/15% of AIME at bend points) for Social Security income in retirement projections; bend points update annually [M effort, High leverage] — POST-BETA
