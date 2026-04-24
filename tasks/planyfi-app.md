# Planyfi — App

## Engineering
- [ ] Accessibility pass — add keyboard handlers to backdrop overlays, aria-labels to icon-only buttons, keyboard support to clickable table rows

### Free tier / monetization (prerequisite for public beta)
Business model: Free tier is session-only (full feature access, no persistence). Premium ($5/mo or $50/yr) unlocks save, scenario comparison, unlimited saved scenarios, CSV export, priority support.
### Infrastructure / ops (before inviting friends)
- [x] Railway staging environment — second service pointed at a branch, separate volume
- [ ] Stripe account setup — create account, configure test prices ($5/mo, $50/yr), add webhook for staging (`incredible-inspiration-production.up.railway.app/api/stripe/webhook`), set STRIPE_* env vars on both production and staging Railway services
### Deferred / reconsidered
- [~] ~~Provisioning layer — automate per-user Railway instance creation via API~~ — DROPPED. Shared multi-tenant SQLite + Clerk userId scoping already covers isolation. Per-instance economics kill $5/mo margin. Revisit only as Enterprise tier.
- [~] ~~Custom domain routing — map user.planyfi.app to each user's Railway instance~~ — DROPPED with the above.
- [~] ~~Data export — let users download their SQLite file~~ — REPLACED with per-user JSON export (SQLite file would leak other users' data in shared-DB model).
- [ ] Data export (JSON) for Premium — per-user server-side export endpoint — DEFERRED, not needed for beta
- [ ] Add CSV import error handling in TransactionsDrawer — catch malformed files and show user feedback — DEFERRED, low priority

- [ ] Hide cash flow features in production

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
- [ ] Interactive demo — hosted read-only instance with sample data
- [ ] Add contact, submit feedback, and support functionality to app

- [ ] Send beta version to Zach, Julie, AJ, James, and others (blocked on: session-only free tier + backups + error monitoring)
- [ ] Onboarding module improvements — refine UX and flows as design evolves

- [x] Add refinance mortgage / other debt as a future event type
- [x] Tighten up home buying and tracking in future events, accounts, and current plan
- [ ] Finalize onboarding modules with 3 paths
- [ ] Update event timeline
- [ ] Allow users to enter plan numbers at high-level category (Investments, Fixed, Discretionary) instead of requiring category or account level detail
- [ ] Add recurring transactions to accounts/holdings — auto-approximate periodic additions (weekly/monthly) without manual entry; show Estimated Balance vs Latest Balance (consistent with checking/savings approach)

- [ ] Add linked account option to both Current Plan and Accounts (not just one)
- [ ] When adding new investment/savings plan category, insert new line directly — no modal
- [ ] Merge Linked Account and Funding Source into single concept with combined pop-up and icon; explore clearer terminology for "where it's coming from and going to"
- [ ] Scenario Comparison feature: ability to hide/adjust Current Plan, Events, Milestones, Market Assumptions; full plan summary/net worth for a given year; line chart plotting net worth, income, expenses for up to 3 scenarios
- [ ] If user enters plan mid-year with no prior plan, assume same for full year; otherwise use appropriate mix based on effective dates
- [ ] Credit card account enrichment — extend CC editor with loan-detail-style fields (APR per card, minimum payment tracking, payoff estimates)
- [x] Fix Future Events and Fund Strategy mobile layout bugs
- [x] Fix date entry for mobile across app — easy to type or select (bug found in profile birthday field)
- [ ] Onboarding/quick entry: start with accounts first, then auto-populate Current Plan categories
- [ ] Add category list (fixed, discretionary, custom) when adding new expense — typeable field with dropdown similar to Empower; evaluate if useful elsewhere (accounts/holdings)

### Design Review (Apr 2026)
Source: Claude Design review of Planner, Accounts, Current Plan, Events, Milestones, and Net Worth surfaces. Quick wins first: #03, #06, #05, #09 (all S effort). Net Worth order: A → E → B → D → C.

**Planner**
- [ ] Scratch-pad what-if scrubbers — live sliders (retirement age, savings rate, return, home price) overlay a ghost projection on the chart; delta readout vs. saved plan; "Save as event" to persist [M effort, High leverage]
- [ ] Mode-specific summary rails — replace monolithic ScenarioSummaryBox with per-mode components (NetWorthRail, IncomeRail, etc.); each has one-sentence thesis + ≤5 stats + CTA [M effort, High leverage]
- [ ] Event ↔ chart causal hover — hover a year → see upstream events + per-event delta; hover an event → see contribution on chart; attribute deltas via projection-with minus projection-without [M effort, Med leverage]
- [ ] Allocation drift panel — show top 3 drifted asset classes (actual vs. target bars) in Net Worth summary rail; rebalance recommendation line [S effort, Med leverage]

**Accounts**
- [ ] Freshness-first account list + Monthly Update flow — "Updated X days ago" on every row; Monthly Update mode filters stale accounts (>30 days) with focus-and-advance keyboard flow; net worth delta preview [S effort, High leverage]
- [ ] Explicit account-mode chips — persistent [Manual] / [Holdings · N] / [Allocation] chip per row; chip becomes mode-switch menu; add freshness, day-change, link badge to same row [S effort, Med leverage]

**Drawers (Current Plan / Events / Milestones)**
- [ ] Plan editor progressive disclosure — lift 3 key overrides (cadence, end condition, growth) as visible chips on each row; collapse to nothing if all defaults; keep 17 fields behind "Advanced →" [M effort, High leverage]
- [ ] Event impact sparklines — 180×40px sparkline per event card showing projection-with minus projection-without; magnitude number (+$412k at FI); left-border color by event type [M effort, High leverage]
- [x] Milestones on the x-axis — add 'milestones' to XAxisMode; ticks become milestone labels with vertical guides; clicking a tick shows usage panel (which budget/event items reference it); collapses milestones drawer [S effort, Med leverage]

**Net Worth chart deep dive**
- [ ] Living axis — year strip + per-member age strips + milestone strip + event strip below chart; hover/clickable; color-coded life phases [M effort, High leverage]
- [ ] Confidence band — fan chart with p10/p50/p90; Phase 1: deterministic ±1.5σ; Phase 2: Monte Carlo [M effort, High leverage]
- [ ] Composition reveal (peelable layers) — default single line; "Break out" chip splits into stacked investments / home equity / cash / liabilities; collapses mode switcher [M effort, Med leverage]
- [ ] Ghost lines — prior plan versions as faded dashed lines; delta callout ("retirement moved forward 14 months since March"); "Why" link opens events since that version [S effort, Med leverage]
- [ ] Narrative annotations — auto-detect peak, FI crossover, drawdown start; place type-on-chart labels with sentences; max 4 visible, toggleable [S effort, Med leverage]

## Bugs / Issues
- [x] Fix Daily SQLite Backup GitHub Action failure [P1]
