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
- [x] Review Fund Strategy and Roth Conversion Ladder — verify accuracy, defaults, and quality of explanations. /qa Jun 2026: fixed Roth target-bracket text hardcoding MFJ figures (now uses plan's filing status), fixed deficit-withdraw "Available" totals double-counting overlapping accounts, updated drawer subtitle to mention Roth conversions. Verdict: Roth tab belongs in Fund Strategy (fund-movement logic); keep Surplus/Deficit as separate tabs. Residual items below.
- [x] Research available US datasets for household income, saving/investing, and spending — delivered themed HTML report at design-mockups/us-data-report.html
- [ ] Add help/info icons to each drawer/page with in-depth explanations; explore on-screen tutorial as well
- [>] Add insights to Current Plan page: hover/tap to see typical US household spend by category with user comparison; show impact of reducing expenses or increasing contributions on net worth
- [ ] Reframe Current Plan as standalone input feature; Financial Planner shows the output/results — make the distinction clearer in UX
- [ ] Add multiple lines to net worth chart based on different market performance assumptions (e.g. 6% vs 7%)
- [ ] Fund Strategy — auto-mirror Deficit Strategy default from Surplus Routing order (drain accounts in reverse of fill order) and expose manual deficit config as "advanced", so most users never hand-configure the deficit waterfall. Note: deficit's "reduce contributions" step has no surplus analog, so the two tabs stay distinct.
- [ ] Consult Claude on improving account-adding UX; review full onboarding flow in separate project chat
- [ ] Show warning popup if non-premium user tries to refresh page — prevent accidental loss of progress, especially on mobile

### QA Sweep (Jun 2026) — component consistency + light contrast
Source: /qa sweep focused on component consistency (text, icons, dropdowns, popups) and light-theme contrast. Fixed in-sweep: muted/tertiary text + chart-axis contrast (now WCAG AA), Fund Strategy tabs converted to underline style, Timeline legend "Milestone"→"Milestones". Remaining (deferred):
- [x] Account-group label casing inconsistent across panels — aligned on sentence-case. Hoisted shared `ACCOUNT_GROUP_LABELS` map in AccountsContent.tsx; account-list card headers now use it (were raw title-case `{group}`), matching the balance-sheet summary
- [x] Per-row action icons differ in color — added shared `ROW_ACTION_ICON` / `ROW_ACTION_ICON_DANGER` constants (brand-classes.ts) documenting the convention: resting = subtle gray, neutral hover = muted, destructive hover = red. Applied to CreditCardItem edit/remove. Plan gear's emerald is the intentional *active* (customized) state, left as-is
- [x] Top tab-bar status indicators mix metaphors — formalized convention: count/info = badge, customized/attention = dot. Market Assumptions dot was a hardcoded hex (#34d399); switched to `var(--color-accent)` token so the "customized" signal matches the plan gear's active treatment app-wide
- [x] Plan Summary Waterfall "Expenses" row defaults expanded even with no child rows — ExpRow now detects real children (React.Children); when empty it hides the chevron and renders a non-interactive (non-toggling) row. Benefits Taxes/Investments rows too

Mobile responsive pass (code audit only — viewport emulation wasn't controllable via browser automation; no breakage found, app is consistently responsive). Optional polish:
- [x] Onboarding benchmark table (DemographicsStep) forces horizontal scroll on phones — added a mobile-only (`sm:hidden`) stacked layout: one selectable card per percentile with a 2-col label/value breakdown (radiogroup + keyboard support). Desktop table now gated `hidden sm:block`, no more horizontal scroll on phones
- [x] Credit-card editor Field uses fixed w-40 (160px) input on mobile — made fluid: input wrapper now `flex-1 min-w-0 max-w-[160px]` on mobile (fills the row up to 160px, shrinks on 320px screens), reverts to column width at `sm:`

### Scheduled QA (Jun 2026) — Tomás, recently divorced single dad rebuilding finances
Source: Automated code-level audit through the eyes of Tomás (42, recently divorced, two kids, splitting retirement accounts, tracking child support, planning future home purchase). Prod health check: all endpoints returned HTTP 403 — Railway WAF blocking automated fetches, not an app error; manual browser verification recommended.

**Calculation bugs**
- [ ] Tax calculator treats weekly-frequency items as annual — `getAnnualDollarAmount` (`tax-calculator.ts:154`) and additional-income classification (`tax-calculator.ts:339`) only branch on `monthly` vs. fallback; weekly income/deduction items are off by ×52. Compare to `annualize()` in `useMultiYearProjection.ts:32` which handles weekly correctly. Fix: add `item.frequency === 'weekly' ? dollarAmount * 52 :` branch in both locations (/qa scheduled 2026-06-15)
- [ ] One-time budget items with no `startDate` repeat in every projection year — `annualizeForYear` (`useMultiYearProjection.ts:48-54`) returns the full amount for every year when `categoryFrequency === 'one-time'` and `startDate` is absent, because the year-gating `if (item.startDate)` is skipped. Fix: return 0 when `startDate` is missing for one-time items (/qa scheduled 2026-06-15)
- [ ] Missing household birth dates default to age 30, silently applying 10% early-withdrawal penalty on all pre-retirement withdrawals — `primaryAge` fallback at `useProjectedNetWorth.ts:1386` uses `?? 30`, which is below the 59.5 penalty-free threshold. Fix: default to 60 (no-penalty) or surface a warning when no birth dates are configured (/qa scheduled 2026-06-15)
- [ ] Inconsistent event `endDate` boundary between income and contribution proration — `computeProratedAnnual` (`projectPlan.ts:772`) subtracts 1 from endDate month (exclusive), while `prorateInYearContributions` (`projectPlan.ts:925`) does not (inclusive). An event ending June 30 is active through May for income but through June for contributions. Fix: align both functions on the same convention (/qa scheduled 2026-06-15)

**UI / error handling**
- [ ] Five mutation handlers in `financial-planner/page.tsx` lack try/catch — `handleDeleteEvent` (:1645), `handleAccountUpdate` (:1675), `handleCreateAccount` (:1682), `handleDeleteAccount` (:1688), `handleBalanceUpdate` (:1654) all await API calls with no error handling; network failures produce silent data loss with no toast (/qa scheduled 2026-06-15)
- [ ] TimelineDrawer custom-form save: `setSaving(false)` fires before async completes — `customFormRef.current.save()` is not awaited (`TimelineDrawer.tsx:749`), so the `finally` block resets the loading state immediately, enabling double-submit. Fix: have the custom form return a promise and await it (/qa scheduled 2026-06-15)
- [ ] Plan History popover row actions (duplicate/delete) unreachable on touch devices — `CurrentPlanDrawer.tsx:399` uses `opacity-0 group-hover:opacity-100` with no tap/long-press fallback. Fix: always show actions on mobile (`sm:opacity-0 sm:group-hover:opacity-100`) or add a row-level context menu (/qa scheduled 2026-06-15)
- [ ] Error toast in TimelineDrawer hardcoded to "Failed to save retirement settings" for all event types — catch block at `TimelineDrawer.tsx:754` shows this message for Home Purchase, Car, State Move, etc. Fix: use generic "Failed to save event" (/qa scheduled 2026-06-15)

**Accessibility**
- [ ] Drawer component (`app/components/Drawer.tsx:119`) missing `role="dialog"`, `aria-modal="true"`, and focus trap — Tab key freely escapes into background content when any drawer is open. Affects all drawers app-wide (Current Plan, Events, Accounts, Profile, etc.) (/qa scheduled 2026-06-15)
- [ ] Onboarding: unchecking "I have a partner" silently resets filing status to "Single", overwriting a user's manual "Head of Household" selection — `HouseholdIncomeStep.tsx:142` and `page.tsx:619` both force `filingStatus: 'Single'` without checking current value. Fix: only reset if current status is MFJ/MFS (/qa scheduled 2026-06-15)

**Product gap**
- [ ] No "Child Support" or "Alimony" expense category in onboarding or plan editor — divorced/separated users must miscategorize court-mandated fixed payments as discretionary "Other Expense" (`ExpensesSavingsStep.tsx:31-43`). Child support is the #1 expense for many single parents and should be a fixed-expense category with appropriate tax treatment (not deductible post-2019 TCJA). Consider adding to both onboarding defaults and the plan editor category list (/qa scheduled 2026-06-15)

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
- [x] Credit card UI broken/poor on mobile; replace with "Add credit card" flow similar to adding holdings, then prompt for details
- [x] Home Purchase event summary renders `"$NaN home, undefined% down, undefined% rate, 3% appreciation"` in the Future Events drawer card. Seen on a fresh Quick Setup demo plan (seeded HOME_PURCHASE event) — home price / down payment / rate fields come through undefined when the event is auto-seeded rather than user-entered. Likely the seeded composite payload is missing fields the card summary reads, or the summary doesn't guard against undefined.
- [ ] Fix input boxes for fixed and discretionary expenses on mobile
- [ ] Fund Strategy surplus routing can exceed a tax-status cap when a later account-group bucket also matches the capped account. Default config: Roth IRA is funded by both the "Tax-Free / $7k annual limit" bucket AND the broader "Investments" bucket, so routeSurplus contributes beyond the IRS limit. Decide whether group buckets should exclude accounts already capped/claimed by an earlier bucket (engine: `lib/utils/allocation-engine.ts` routeSurplus has no claim mechanism, unlike withdrawByPriority).
- [ ] Adding holding/ticker on mobile: move search bar to bottom with matched results displayed above it — make it feel more integrated
- [ ] Holdings overflow horizontally on mobile when values have too many digits — stack layout vertically instead
- [ ] Font, icons, and UI elements too small on mobile — explore improvements without full redesign
- [ ] Plan investment/savings categories should auto-link after being added in the previous onboarding step

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
