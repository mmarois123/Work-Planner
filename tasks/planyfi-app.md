# Planyfi — App

## Engineering

### Free tier / monetization (prerequisite for public beta)
Business model: Free tier is session-only (full feature access, no persistence). Premium ($5/mo or $50/yr) unlocks save, scenario comparison, unlimited saved scenarios, CSV export, priority support.
### Infrastructure / ops (before inviting friends)
- [ ] Stripe account setup — create account, configure test prices ($5/mo, $50/yr), add webhook for staging (`incredible-inspiration-production.up.railway.app/api/stripe/webhook`), set STRIPE_* env vars on both production and staging Railway services
### Deferred / reconsidered
- [~] ~~Provisioning layer — automate per-user Railway instance creation via API~~ — DROPPED. Shared multi-tenant SQLite + Clerk userId scoping already covers isolation. Per-instance economics kill $5/mo margin. Revisit only as Enterprise tier.
- [~] ~~Custom domain routing — map user.planyfi.app to each user's Railway instance~~ — DROPPED with the above.
- [~] ~~Data export — let users download their SQLite file~~ — REPLACED with per-user JSON export (SQLite file would leak other users' data in shared-DB model).
- [ ] Data export (JSON) for Premium — per-user server-side export endpoint — DEFERRED, not needed for beta
- [ ] Add CSV import error handling in TransactionsDrawer — catch malformed files and show user feedback — DEFERRED, low priority

## Product
- [x] Onboarding: capture partner/spouse info in Quick Start — when "I have a partner/spouse" is checked, expand to collect partner name, age/DOB, and current/future salary. Auto-switch Filing Status to "Married Filing Jointly." Pre-populate partner section in Current Plan post-onboarding. Currently partner is completely invisible despite checking the spouse box (QA-026, QA-031, QA-005, QA-011)
- [x] Onboarding: add age/DOB field — age is critical for retirement projections, FI date, and Social Security estimates. Currently not collected in any onboarding path (QA-003)
- [x] Onboarding: improve Expenses & Savings step clarity — add tooltip/examples for Fixed vs Discretionary ("Rent, car payment, insurance" vs "dining, entertainment, shopping"); remove negative signs from Monthly Summary outflows (use color only, not minus + red); explain what "Remaining" money represents; clarify whether Savings Rate is gross or net and whether it includes 401k (QA-014, QA-015, QA-020, QA-021, QA-023, QA-016, QA-032)
- [x] Onboarding: minor UX polish — add tooltip to color dot next to name; explain or remove green border highlight on Roth IRA / Auto Loan in accounts step; set Bonus default frequency to "Yr" instead of "Every 2 wks" (QA-001, QA-008, QA-029)
- [x] Post-onboarding guided experience — after completing setup, show a "What's Next" checklist or guided tour highlighting: add bonus/additional income, link 401k to savings, add future events (partner's job, house purchase), review FI projections. Address the cold-start problem where users see a dense dashboard with no clear next action (QA-025)
- [x] Improve "FI Date: Not reached" first impression — when FI is not reached, explain why (e.g., savings not linked to accounts, single income only) and suggest actions to improve. Consider showing estimated FI date if savings were linked, or a "Close to FI if…" prompt instead of flat "Not reached" (QA-022)
- [x] Expand event templates — add composite events for common life changes: "Partner starts working" (income change for spouse), "Have a baby" (new dependent + expense increase), "Job change" (salary + benefits change), "Move to new state" (tax impact + housing cost change). Empty state in Future Events should suggest relevant events based on profile (married → "Partner income change", has dependents → "Childcare changes") (QA-040, QA-038, QA-039)
- [x] Chart default views — Outlays chart should default to stacked/breakout view showing taxes, expenses, and savings separately instead of a single line identical to Income. Income chart should indicate whether inflation/raises are modeled, or add a note about assumptions (QA-045, QA-046)
- [x] Add "Real" vs "Nominal" tooltip — event form has Real/Nominal toggle with no explanation. Add tooltip: "Real = today's dollars (adjusted for inflation), Nominal = future dollar amounts" (QA-042)

- [ ] Research (via Claude) what mortgage info a homeowner typically has access to — use to inform current plan input fields

- [ ] Add calculator section: rent vs buy, buy a home, estimated taxes — pull from current plan inputs with ability to adjust and see quick impact
- [ ] Rent vs. Buy — compare two homes by address, or rent vs. buy a single property
- [ ] Home Purchase — zip code lookup for median home price, county-level property tax, flood/wind insurance zones
- [ ] Rent vs. Buy — pull property data by address (Zillow/Redfin API or manual entry)
- [ ] Rent vs. Buy — surface as linked tool inside Scenario Planner HOME_PURCHASE event and Plan
- [ ] Scenario comparison — side-by-side delta view of two scenarios
- [x] Mobile-responsive layout — full mobile compatibility pass across all pages and components; touch-friendly interactions throughout
- [ ] Integrate US census data more deeply into app
- [ ] Add view mode for filtering/browsing different demographics
- [ ] Interactive demo — hosted read-only instance with sample data
- [ ] Send beta version to Zach, Julie, AJ, James, and others (blocked on: session-only free tier + backups + error monitoring)

- [ ] Add recurring transactions to accounts/holdings — auto-approximate periodic additions (weekly/monthly) without manual entry; show Estimated Balance vs Latest Balance (consistent with checking/savings approach)

- [x] Add linked account option to both Current Plan and Accounts (not just one)
- [x] When adding new investment/savings plan category, insert new line directly — no modal
- [x] Merge Linked Account and Funding Source into single concept with combined pop-up and icon; explore clearer terminology for "where it's coming from and going to"
- [x] Onboarding plan: show owner names on income/investment line items (e.g., "Kylie's Salary", "Kevin's Bonus") instead of requiring hover on tiny person icon — critical for households with two earners
- [x] Onboarding: partner salary placeholder — when partner is not working, show $0 default instead of $65k placeholder, or add "Not currently employed" toggle to avoid ambiguity
- [x] Onboarding: add childcare/daycare as default expense category when user has dependents — often the single biggest family expense, currently missing from both Fixed and Discretionary defaults
- [ ] Onboarding plan: progressive disclosure — add collapsible sections, section jump nav, and reduce visual complexity (6 icons per line item overwhelms new users; consider hiding advanced controls behind a "more" menu)
- [x] Onboarding: filter account types shown for dependents — a 9-month-old doesn't need Traditional 401k, Mortgage, or HELOC options; show only age-appropriate types (529 Plan, Savings, Brokerage)
- [x] Onboarding accounts review: show net worth total at bottom of account list as an early "wow moment" before reaching the dashboard
- [x] Mobile: surface "What's Next" checklist on mobile — currently hidden on small screens, losing the key new-user engagement tool
- [x] Dashboard: rename "Outlays" chart tab to "Expenses" or "Spending" — "Outlays" is financial jargon unfamiliar to most users
- [x] Guided tour: expand from 3 to 5+ steps — add coverage for Milestones, What's Next checklist, and how to edit the plan
- [ ] Scenario Comparison feature: ability to hide/adjust Current Plan, Events, Milestones, Market Assumptions; full plan summary/net worth for a given year; line chart plotting net worth, income, expenses for up to 3 scenarios
- [x] If user enters plan mid-year with no prior plan, assume same for full year; otherwise use appropriate mix based on effective dates
- [x] Credit card account enrichment — extend CC editor with loan-detail-style fields (APR per card, minimum payment tracking, payoff estimates)
- [x] Onboarding/quick entry: start with accounts first, then auto-populate Current Plan categories
- [x] Add category list (fixed, discretionary, custom) when adding new expense — typeable field with dropdown similar to Empower; evaluate if useful elsewhere (accounts/holdings)
- [x] Add % of take-home pay as an input option for expenses in Edit Current Plan

- [x] Rename onboarding path "Start from Scratch" — consider "Quick Start" or similar
- [x] Add ability to change household member colors during onboarding
- [x] Make first entered checking and savings accounts the primary cash flow accounts by default

### Design Review (Apr 2026)
Source: Claude Design review of Planner, Accounts, Current Plan, Events, Milestones, and Net Worth surfaces. Quick wins first: #03, #06, #05, #09 (all S effort). Net Worth order: A → E → B → D → C.

**Planner**
- [ ] Scratch-pad what-if scrubbers — live sliders (retirement age, savings rate, return, home price) overlay a ghost projection on the chart; delta readout vs. saved plan; "Save as event" to persist [M effort, High leverage]
- [ ] Allocation drift panel — show top 3 drifted asset classes (actual vs. target bars) in Net Worth summary rail; rebalance recommendation line [S effort, Med leverage]

**Accounts**

**Drawers (Current Plan / Events / Milestones)**
- [ ] Event impact sparklines — 180×40px sparkline per event card showing projection-with minus projection-without; magnitude number (+$412k at FI); left-border color by event type [M effort, High leverage]

**Net Worth chart deep dive**
- [ ] Confidence band — fan chart with p10/p50/p90; Phase 1: deterministic ±1.5σ; Phase 2: Monte Carlo [M effort, High leverage]
- [ ] Narrative annotations — auto-detect peak, FI crossover, drawdown start; place type-on-chart labels with sentences; max 4 visible, toggleable [S effort, Med leverage]

## Security

## Engineering (New User Experience)
- [x] Auto-link 401k to savings plan line after onboarding — when user selects a 401k account in onboarding AND sets a savings rate, auto-create a linked contribution routing savings to that account. Currently the account and plan line are disconnected, requiring manual linking that new users won't discover (QA-037)
- [x] Add tooltips to icon-only buttons across app — account action icons (link, add, owner, edit, delete) and plan line icons (link, calendar, chart, delete) have no labels. Add aria-label and hover tooltip to each. On mobile, nav tab icons also need labels or a labeled fallback (QA-036, QA-047, QA-034)
- [x] Disable beforeunload dialog for guest/session-only users — "Leave site?" dialog fires even though data won't persist. Only show for signed-in users with unsaved changes (QA-049)

## Bugs / Issues
- [x] Update CLAUDE.md route table and QA skill — `/profile`, `/budget-actuals`, `/transactions`, `/accounts`, `/net-worth`, `/cash-flow` all redirect to `/financial-planner`; route list is stale
- [x] Detailed onboarding: jump straight into account wizard without requiring button press to launch
- [x] After adding accounts, success message shows but displays 0 accounts and blocks navigation to next screen
- [x] Update account wizard UI to match rest of app styling
- [x] Renaming accounts: replace inline rename with edit icon + popup for better mobile UX
- [x] Editing account names in onboarding (mobile) is still difficult — update UI
- [x] Ticker symbol search for holdings not working — make seamless; search should pull up ranked list of securities with best match
- [x] Investments subtotal not updating when adding underlying account balances — only shows first entered amount
- [x] Popup boxes blend into background on mobile — increase contrast/color to make them stand out; applies to Accounts and Current Plan modules specifically
- [x] Account balances not saving from detailed onboarding process
- [x] Date input on mobile still broken — can't type "/" so manual entry fails; date picker/navigator also poor experience; needs full fix across app
- [x] Mortgage rates in home purchase event may not be updating — verify live rate pull; should refresh when user creates event and display current avg rate as a note when event is opened
- [x] Frequency toggle (Wk/Mo/Yr) converts existing values instead of changing entry mode — entering $500 then switching to Mo shows $41.66666666 (repeating decimal). Users expect to enter $500/mo, not have their value divided by 12. Should either change entry mode without recalculating, or at minimum round to 2 decimal places.
- [x] Milestones badge shows "4" but 6 milestones are listed (Coast FI, FI, 2x Retirement, 2x Life Expectancy) — badge count is wrong
- [x] "Collectables" typo in account type selection during onboarding — should be "Collectibles"
- [x] Mobile nav tabs are icon-only with no visible labels — despite tooltip work (QA-047), new mobile users still can't identify tabs; need visible text labels or a labeled bottom nav bar
- [ ] Fix Daily SQLite Backup GitHub Actions workflow failure
