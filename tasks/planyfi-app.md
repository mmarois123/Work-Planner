# Planyfi — App

## Engineering

### Free tier / monetization (prerequisite for public beta)
Business model (PIVOTED 2026-06-15): Account REQUIRED to use the app (guest flow retired/dormant). Free accounts get full feature access AND data persistence to the DB. Premium ($5/mo or $50/yr) unlocks scenario comparison, unlimited saved scenarios, CSV export, priority support. Persistence stays a Premium concept, to be limited deliberately (retention window) — see below.
- [ ] Retention email reminders (optional) — transactional email at T-7 + on freeze, complementing the in-app notifications already shipped. Needs an email provider (only R2 backups are wired today; e.g. Resend): provider account + API key, a send helper, and a trigger (cron over `getRetentionState`, or piggyback the notification-generate pass). Lower priority than the in-app notices since those + the banner already cover the freeze UX. Split out of the Phase 3 item above.
### Infrastructure / ops (before inviting friends)
- [~] ~~Stripe account setup~~ — REPLACED with Clerk Billing (migrated May 2026)
### Deferred / reconsidered
- [~] ~~Provisioning layer — automate per-user Railway instance creation via API~~ — DROPPED. Shared multi-tenant SQLite + Clerk userId scoping already covers isolation. Per-instance economics kill $5/mo margin. Revisit only as Enterprise tier.
- [~] ~~Custom domain routing — map user.planyfi.app to each user's Railway instance~~ — DROPPED with the above.
- [~] ~~Data export — let users download their SQLite file~~ — REPLACED with per-user JSON export (SQLite file would leak other users' data in shared-DB model).
### QA sweep (Jun 2026) — full sweep

### Code review (Jun 2026) — scenario-comparison branch cleanups
Source: /code-review high on the unmerged `scenario-comparison` branch (worktree included). Bugs from the same review are in Bugs / Issues, tagged (/code-review Jun 2026).

### QA sweep (Jun 2026) — missing states, consistency & a11y
Source: /qa full sweep (desktop visual + 3-dimension code audit). Mobile was code-audit-only (dev-env renderer froze on viewport resize — same limitation as prior passes). Coverage was reassuring: the 11 financial-planner drawers all share Drawer.tsx (Esc + backdrop + X), charts/tables have rich empty states, and save paths are well-covered with toasts + spinners. Gaps below.

### QA sweep (Jun 2026) — drawers, modals & event-forms
Source: /qa full sweep — desktop objective audit (JS-based: horizontal-overflow / clipped-text / accessible-name / font-size, since screenshots froze the renderer AND `resize_window` doesn't change the CSS viewport in this dev env — both browser checks non-functional) + 3-dimension code audit + console read. /financial-planner + /rent-vs-buy are structurally clean (no overflow/clip, every control labeled, no missing alt, no JS errors/hydration warnings); /plan/edit is an intentional redirect stub to /financial-planner. Mobile not visually verifiable (viewport pinned ~1528px) — known mobile-overflow items already tracked under "visual + mobile polish" above. Gaps cluster in drawers/modals/event-forms.

## Product
- [x] Add help/info icons to each drawer/page with in-depth explanations; explore on-screen tutorial as well
- [ ] Rent vs. Buy — compare two homes by address, or rent vs. buy a single property
- [ ] Home Purchase — zip code lookup for median home price, county-level property tax, flood/wind insurance zones
- [ ] Rent vs. Buy — pull property data by address (Zillow/Redfin API or manual entry)
- [ ] 🟠 Send beta version to Zach, Julie, AJ, James, and others. Original blockers all CLEARED: free-tier limit (retention freeze — built), backups (R2 daily cron — confirmed working), error monitoring (Sentry + PostHog — wired in code). REMAINING before invite: (1) **Deploy master** — `scenario-comparison` was MERGED into master 2026-06-19 (retention freeze + Scenario Compare + Allocation view & Primary-cash-flow account hidden behind flags for beta); the merge is local/unpushed + undeployed. tsc clean, 924/924 tests, build green. (2) Verify `NEXT_PUBLIC_SENTRY_DSN` + `NEXT_PUBLIC_POSTHOG_KEY` are actually set in Railway prod. (3) Owner self-tests the real Clerk upgrade flow in prod (doubles as the retention rollout — see above). (4) Decide whether beta testers get comped premium or accept the 30-day free-tier freeze window (a beta running >30 days will freeze their data otherwise).
- [ ] Add button that generates a generic LLM prompt — instructs any AI tool to review attached transactions and categorize them against the user's current plan (specific categories + sub-categories) in a format uploadable to Planyfi for plan comparison or updates
- [~] ~~Fund Strategy — auto-mirror Deficit Strategy default from Surplus Routing order (drain in reverse of fill order)~~ — DROPPED 2026-06-23. The "advanced-gating" half already shipped (the Deficit tab opens on the simple plain-English order; "Customize order" is the opt-in advanced path). The remaining "reverse-of-fill" default is financially unsound — it would drain tax-advantaged/retirement accounts before the cash buffer (early-withdrawal penalties, lost growth, Roth raided), regressing the current sensible tax-aware default (reduce contributions → Cash → Taxable → Tax-Deferred, Roth preserved).
- [ ] Revisit Balance History tab — clarify purpose, explore improvements, consider relocating
- [~] ~~Revisit and update UI for FI section~~ — SUPERSEDED 2026-06-24 by the "### Financial Independence section redesign (Luis)" subsection below (design approved; spec + mockup ready).

### QA Sweep (Jun 2026) — component consistency + light contrast
Source: /qa sweep focused on component consistency (text, icons, dropdowns, popups) and light-theme contrast. Fixed in-sweep: muted/tertiary text + chart-axis contrast (now WCAG AA), Fund Strategy tabs converted to underline style, Timeline legend "Milestone"→"Milestones". Remaining (deferred):

Mobile responsive pass (code audit only — viewport emulation wasn't controllable via browser automation; no breakage found, app is consistently responsive). Optional polish:

### Design Review (Apr 2026)
Source: Claude Design review of Planner, Accounts, Current Plan, Events, Milestones, and Net Worth surfaces. Quick wins first: #03, #06, #05, #09 (all S effort). Net Worth order: A → E → B → D → C.

**Planner**
_(Allocation drift panel moved to Parking Lot 2026-06-24 — Allocation view hidden behind `NEXT_PUBLIC_FEATURE_ALLOCATION` for beta.)_

**Accounts**

**Drawers (Current Plan / Events / Milestones)**
**Net Worth chart deep dive**

### QA sweep (Jun 2026) — onboarding + Compare deep dive
Source: /qa full visual sweep as a new Quick Setup user + Compare-mode product review.

### Design consistency (Luis)
Source: /luis full review focused on the Financial Planner page + Scenario Compare feature. Design-system/lens drift only (functional bugs go elsewhere). Token discipline is broadly good — no native `<select>`, hex literals are mostly legit chart-palette/SVG. Drift is concentrated below.

### Design consistency (Luis) — Fund Strategy (2026-06-22)
Source: /luis review scoped to the Fund Strategy surface (AllocationStrategyDrawer + AllocationSummaryBox + AllocationPriorityList + DeficitPriorityList). Design-system/lens drift only — no functional bugs. Through-line: green is spent as decoration rather than as the accent, and several controls hand-roll classes that `brand-classes.ts` already provides. Token discipline is otherwise good (shared `Select` throughout, no native `<select>`; the Roth enable switch matches its peers across other drawers).
  - [~] ~~Terminology drift "Allocation Summary" → "Fund Strategy"~~ — PULLED 2026-06-23 (Luis misread): the "Allocation Summary" rail and the "Fund Strategy" drawer are two distinct surfaces (the rail's "Fund Strategy" button opens the drawer), so a rename would collide. `AllocationSummaryBox.tsx:224` stays.

### Design consistency (Luis) — Main chart (2026-06-24)
Source: /luis review scoped to the Financial Planner main chart (ScenarioChart + ScenarioChartTooltip + ComparisonChart + the new FIProjectionChart + ChartAxisStrips + ChartLegendBar + ChartControlsBar + chartGeometry + theme.ts chart config). Design-system/lens drift only. Through-line: the three charts on this one surface each solve the same color/tooltip/axis problems three different ways, and the two older ones break a rule the repo documents twice. Bones are good (emerald area+gradient, horizontal-only grid, click-to-select year, multi-strip age axis).
**DONE 2026-06-24** — all 7 addressed in one pass (commit `d8a9098`, branch `worktree-luis-chart-consistency`; unmerged/undeployed). The fix centralized: F1+F5 live in `lib/theme.ts` (every SVG-bound chart color → literal per-theme hex; grid → dashed `3 3` @ 0.5 opacity), which fixes grid/axis/reference-line/cursor across the Scenario / Comparison / CashFlow / FI charts at once. F2 routed the Compare tooltip through `themeConfig.chart.tooltip.bgClass`; F3 set axis ticks to 11px everywhere; F4 unified swatches to round 10px dots; F7 gave ScenarioChart a selected/end-year hero (above the click-wrapper, sized to complement not compete with the right-rail hero). F6 needed NO change — the global mobile floor in `globals.css` already bumps `text-[10px]`→12px on phones (the review missed the existing floor). Verified: tsc clean + FIProjectionChart 23/23. Visual click-through pending (dark+light, hover tooltip, Compare toggle, click-year hero update).

### Scenario Compare redesign — shared event pool (Luis + Claude Design, 2026-06-17)
Design approved. Spec + visual contract: `design-mockups/luis/scenario-compare-workspace/` (`SPEC.md`
= engineering spec, `index.html` = 3-screen mockup). Model: one shared event pool + per-scenario
membership (junction table) + optional overrides + draft-by-default; three views over the pool (Plan
Timeline drawer = author, swim-lane = read, matrix popup = bulk edit). **Contracts:** projection engine
untouched; post-backfill projections must be byte-identical to today. Supersedes the "Applies to
checkboxes" + "Promote scenario to plan" compare items above. Build in stages (see SPEC.md):

### Current Plan header redesign — switcher-title (Luis, 2026-06-22)
Design approved. Spec + visual contract: `design-mockups/luis/current-plan-header/` (`SPEC.md` = engineering
spec, `option-B-switcher-title.html` = mockup, `index.html` = 3-direction comparison). The drawer header crams
four jobs into one un-wrapping row (identity, an ambiguous pencil "Manage Plans", the new "Compare to US avg"
view toggle, Save/close) → crowds on desktop, overflows at 390px. Fix: the **title becomes the plan switcher**
(`Current Plan ⌄` opens the existing version popover), date+status move to a subtitle, and the view toggle gets
a deliberate home (inline-right on desktop, full-width strip on mobile). **All changes in
`app/financial-planner/components/CurrentPlanDrawer.tsx`.** **Contracts:** the consolidated popover behaves
identically (only its trigger moves); the benchmark toggle stays ONE node portaled from PlanEditor
(`page.tsx:2130`) — repositioned by CSS, never duplicated; all header states preserved (current/archived/frozen/
review/new). Regression gate is visual: tsc clean + every state renders in dark+light at 390px (no engine code →
no financial suites). Build in stages (see SPEC.md):

### Financial Independence section redesign (Luis, 2026-06-24)
Design approved. Spec + visual contract: `design-mockups/luis/fi-section/` (`SPEC.md` = engineering spec, `final-the-answer-cockpit.html` = approved mockup, `index.html` = 3-direction comparison + featured final). Redesign of the FI drawer (`FinancialIndependenceDrawer.tsx`): give it a date-led hero answering "When can you stop working?", add the missing net-worth-vs-FI-target chart with the crossover annotated, and replace the buried What-if accordion with an always-on cockpit (live sliders → ghost overlay on the chart → live result tiles). Direction = "The Answer + Cockpit" (A spine + C's live what-if). Supersedes the old "Revisit and update UI for FI section" Product item. **Contracts:** UI-only — NO changes to `lib/utils/fire-calculator.ts` or the projection engine; same inputs → identical FI number/date/ages/coast; what-if stays local/non-persisted; rail panel (`FinancialIndependenceSection`) keeps its current output. **Regression gate:** tsc clean + `fire-calculator`/`useScenarioNetWorth` tests green + the new tiles equal the old `DeltaRow` output for the same overrides + every state renders dark+light at 390px. Build in stages (see SPEC.md):

### Net Worth chart redesign — tooltips, event cards + connectors, hero (Luis, 2026-06-26)
Design approved. Spec + visual contract: `design-mockups/luis/net-worth-chart-system/` (`SPEC.md` = engineering spec; `chart-modes.html` = the approved build — ledger tooltip across modes + breakout, bordered-card events, per-year connectors; `chart-tooltips.html` = 3 tooltip variants on the riser base; `modes-index.html` / `tooltips-index.html` = comparisons; `README.md` = writeup). Presentational redesign of the Financial Planner main chart (`ScenarioChart` + `ScenarioChartTooltip` + `ChartAxisStrips`), across all four modes (Net Worth line + breakout, Income, Outflows). Builds on the "Main chart" consistency pass (`d8a9098`) and fulfils the empty "Net Worth chart deep dive" placeholder. **Contracts:** projection/chart data untouched (no engine edits); tooltip stays a pure fn of its payload; axis strips keep click-to-select-year + keyboard slider + multi-strip gutter; chart line/fill/gridlines stay matched to `theme.ts`; **the hero stays RIGHT-ALIGNED as today** (the mockup's left-aligned variant is NOT adopted). **Regression gate:** tsc clean + useProjectedNetWorth/useScenarioNetWorth/projectPlan green (unaffected) + visual click-through (dark+light; hover tooltip in all 4 modes incl. breakout; cluster collapse → hover fan-out; same-year events share one connector; hero right-aligned at 390px). Build in stages (see SPEC.md):

### Compare mode — interactive scenario cards (Luis, 2026-06-27)
Design approved. Spec + visual contract: `design-mockups/luis/compare-chart-lens/` (`SPEC.md` = engineering spec; `scenario-cards.html` = the approved build; `index.html` = lead frame + the 3 parent explorations A/B/C; `README.md` = writeup). Evolves the chosen Compare direction (C · Outcome Scoreboard) into an interactive **scenario-card manager**: each card folds in the per-scenario controls that live in the cramped chip bar (`ScenarioManagerBar.tsx`) today. Applies the net-worth-chart lens (kept C's clean ledger tooltip verbatim). **Presentational/IA only — no projection or data-layer edits.** **Contracts:** projection engine untouched (`useComparisonProjections`/`scenarioProjectionCore`/`useScenarioNetWorth` not edited); card net worth + variance read from the SAME `results` map `ComparisonTable` already consumes (single source of truth — must match its Net Worth row exactly); `MAX_COMPARISON_SCENARIOS = 3` visible cap holds, Base always index 0; Base stays non-destructive (no rename/delete — its edit path is the live plan); per-scenario edit behavior identical (reuse `onAdd`/`onRemove`/`onUpdate`/`onToggleEventHidden`/`onEditTimeline` + `MarketAssumptionsPopover`; keep the `ScenarioNameInput` draft/commit-on-blur pattern, not per-keystroke). **Regression gate:** tsc clean + comparison/projection suites green & unchanged + visual click-through (add/rename/recolor/edit-events/assumptions/duplicate/delete via the cards; card NW+variance == ComparisonTable; Saved picker swaps the ≤3 shown; Base has no delete/rename; dark+light). Build in stages (see SPEC.md):

### Compare — Edit scenarios studio + chart-integrated events (Luis, 2026-06-27)
Design approved. Spec + visual contract: `design-mockups/luis/compare-edit-scenarios/` (`SPEC.md` = engineering spec; `option-C-studio-modal.html` = the approved interactive build; `index.html`/`README.md` = the 3 directions + writeup). **Supersedes / absorbs** the "interactive scenario cards" ticket above — consolidates ALL Compare scenario management into one **"Edit scenarios" studio modal** (replaces the "Manage events across scenarios" button + `EventMatrixModal`, the Add/Saved tile, and the per-card popovers), and pulls the N swim-lanes into **one chart-integrated event strip** (markers anchored to the plot x-grid + category-colour guide lines into the curves + scenario colour-pips). Modal: left roster (inline rename, recolor, **"On chart" checkbox with the 3-cap**, variance, single **⋮ kebab** = Add event/Assumptions/Duplicate/Delete) + right **chronological** membership matrix (year chip per row, **no** shared/differs grouping). Assumptions = **popover** (`MarketAssumptionsPopover`), not a panel. **Event create/edit routes to the Plan Timeline drawer** (`TimelineDrawer` `eventsStore`/`initialEditEvent`/add-mode) — never an in-modal editor. Right `ComparisonTable` untouched. **Presentational/IA only — no projection or data-layer edits.** **Contracts:** engine untouched (`scenarioProjectionCore`/`useComparisonProjections`/`comparisonMetrics`); matrix cell = same membership write as today's `EventMatrixModal.onToggle`; `MAX_COMPARISON_SCENARIOS = 3` is the single charted-set enforcement point; Premium gating on saved scenarios preserved. **Regression gate:** tsc clean + `useScenarioNetWorth`/`useComparisonProjections`/`comparisonMetrics`/`projectPlan` suites green & unchanged; for the same scenarios + membership, comparison series/card NW/variance/`ComparisonTable` identical before↔after; click-through (rename/recolor/toggle-charted-at-cap/⋮-Assumptions-popover/⋮-Add-event→Plan Timeline/matrix toggle == chart+table; dark+light). Build in stages (see SPEC.md):
- [ ] Chart-integrated single event strip (anchored markers + guide lines + scenario pips; refactor `SwimLaneTimeline`, reuse `EventMarkerCard`) (/luis 2026-06-27)
- [ ] "Edit scenarios" modal shell + roster (rename/recolor/duplicate/delete/Add scenario/Saved + On-chart checkbox & 3-cap; retire `ScenarioManagerBar` remnants) (/luis 2026-06-27)
- [ ] Chronological membership matrix in the modal (reuse `buildEventMatrix`; sort by date, drop shared/differs, add year chip) — regression gate vs old `EventMatrixModal` (/luis 2026-06-27)
- [ ] Assumptions popover per roster row (`MarketAssumptionsPopover`) (/luis 2026-06-27)
- [ ] Route event create/edit to `TimelineDrawer` (⋮ Add event = add-mode for scenario; row pencil = `initialEditEvent`); remove in-modal event editing (/luis 2026-06-27)
- [ ] Cleanup: delete `EventMatrixModal` + the standalone "Manage events across scenarios" button (+ `SwimLaneTimeline` if superseded) (/luis 2026-06-27)

### QA sweep (Jun 2026) — Plan Timeline + projection horizons
Source: /qa walkthrough — onboarding → Plan Timeline → create future event → confirm projections at 5Y / 35Y. The create-event → projection-update → delete flow works (verified live: a Set-Salary $250K event moved terminal NW $11.6M→$14.1M and pulled FI 2038→2036; delete reverted everything cleanly). Projections read sensibly across the horizon (5Y ≈ $1.7M; 35Y/2061 ≈ $16M on the clean plan; Full/2086 ≈ $85.9M). Onboarding itself redirects to /financial-planner for an already-onboarded account (expected) — the fresh wizard wasn't exercised. Functional/age bugs filed under Bugs / Issues; visual-label nits below.

### QA sweep (Jun 2026) — visual + mobile polish
Source: /qa desktop visual sweep + code-audit mobile pass (renderer froze on resize — mobile verified in code only).

### Scheduled QA (Jun 2026) — Tomás, 42, recently divorced dad restarting financial plan
Source: automated nightly code-level QA audit (no browser — code-only). Persona: Tomás, 42, recently divorced single dad splitting assets and restarting his financial plan with child support obligations, a 401(k), and a taxable brokerage. Key journeys: onboarding with existing accounts, adding recurring expenses, modeling a home purchase event, checking net worth projections. Production health check blocked by sandbox egress proxy — could not verify `app.planyfi.app/api/health`. Bugs filed under Bugs / Issues tagged `(/qa scheduled 2026-06-28)`.
- [ ] Drawer.tsx (base component, lines 97–150): missing `role="dialog"`, `aria-modal="true"`, `aria-labelledby`, and focus trap — affects all 10+ drawers in the app. The `<h2>` title at line 115 needs an `id`; the panel div at line 107 needs dialog ARIA attributes. Keyboard users can Tab behind the backdrop. Fix: add dialog semantics to the panel div and implement a focus trap (e.g. `focus-trap-react` or manual) (/qa scheduled 2026-06-28)
- [ ] Select.tsx: `role="option"` on `<button>` elements (lines 285–313) is invalid ARIA — native button semantics conflict with the option role. Also the `role="listbox"` div (line 268) has no `aria-label`. Fix: change option elements from `<button>` to `<div role="option" tabIndex={-1}>` and add `aria-label` to the listbox (/qa scheduled 2026-06-28)
- [ ] page.tsx `loadBaseData` failure leaves an empty planner with no persistent error UI (lines 546–552). The toast disappears after seconds; user sees blank chart, zero accounts, no budget, no explanation. Fix: add an `error` state variable, render a persistent error banner with a retry button when `error && !loading` (/qa scheduled 2026-06-28)
- [ ] Event-form labels not programmatically linked to inputs (systemic — no `htmlFor`/`id` association): RetirementForm.tsx (lines 98, 118, 122, 128), StateMoveForm.tsx (133, 143), ChildBirthForm.tsx (91, 100, 112, 131, 136), CarPurchaseForm.tsx (76, 82, 106, 111, 133), MortgageRefinanceForm.tsx (field names in `<span>` not `<label>`). Fix: add `id` props to each input and `htmlFor` to each label, or use `aria-label` (/qa scheduled 2026-06-28)
- [ ] Onboarding Back buttons not disabled during async submissions — HouseholdIncomeStep.tsx:290 and ExpensesSavingsStep.tsx:316. The Next/Complete button is correctly `disabled={isSubmitting}` but the Back button stays enabled, allowing navigation away while the API call is in-flight. Fix: pass `disabled={isSubmitting}` to both Back buttons (/qa scheduled 2026-06-28)
- [ ] Five custom modals/overlays missing `role="dialog"` and `aria-modal="true"`: TransactionsDrawer.tsx CSV column-mapping modal (lines 302–331), TimelineDrawer.tsx delete-event confirmation (lines 1706–1741), HomePurchaseForm.tsx rent breakdown overlay (lines 554–657), TransactionEditModal.tsx (line 282), FeedbackModal.tsx (line 62). Fix: add dialog semantics and `aria-labelledby` to each overlay's inner panel div (/qa scheduled 2026-06-28)

## Security

## Engineering (New User Experience)
Source: account-onboarding UX review (design-mockups/account-onboarding-ux-review/). Outstanding observations split out from the now-closed "Consult Claude on account-adding UX" item.
- [~] ~~Progressive disclosure for rarer account types in onboarding (Obs #8)~~ — DROPPED 2026-06-16. (Was: all types are always-visible rows, only "I own my home" gated; add a "+ more account types" collapse.)
- [~] ~~Strengthen holdings reconciliation signal — delta is colored in the editor footer but easy to miss; consider an account-row-level badge when holdings ≠ balance (Obs #11)~~ — DROPPED 2026-06-21. Redundant by design: saving a holdings account always rewrites its recorded balance to the holdings sum (`useAccountHoldings.ts:337` → `balanceHistoryApi.add({ amount: sum })`), so holdings can never *persistently* disagree with the recorded balance. The only remaining diffs are unsaved edits (already flagged by the dirty dot) or live stock/crypto market movement (already shown in the row's change column) — a badge would add noise, not clarity. The one genuinely non-noisy reconciliation gap (allocation-mode account whose target %s ≠ 100%) is already surfaced in the expanded editor's "Allocated X% (Y% left)" line.

## Bugs / Issues
- [ ] ImpactCard.tsx: `useMemo` called inside `switch/case` branches in `ImpactFieldRenderer` (lines 623, 934, 953, 1048, 1082, 1160) violates React Rules of Hooks — switching impact type changes hook call order → runtime crash. Fix: move all `useMemo` calls to the top of the component unconditionally, or extract each case into its own sub-component (/qa scheduled 2026-06-28)
- [ ] chartGeometry.ts:80: `delta: d ? d : null` uses falsy check — when year-over-year delta is exactly `0`, it's treated as `null` and tooltip shows "---" instead of "+$0". Fix: change to `delta: d != null ? d : null` (/qa scheduled 2026-06-28)
- [ ] AllocationFilterBar.tsx:123: `{acct.name}` uses optional legacy `name?` field instead of required `accountName` — dropdown labels render blank for accounts without the legacy field. Fix: change to `{acct.accountName}` (/qa scheduled 2026-06-28)
- [ ] SwimLaneTimeline.tsx (lines 39, 40, 87) + EventMatrixModal.tsx (lines 102, 168, 255, 270): `text-muted`/`text-secondary` are undefined Tailwind classes (should be `text-theme-muted`/`text-theme-secondary`) — text falls back to inherited/default color with no visible styling. Note: both files may be superseded by the Compare redesign; fix if they survive (/qa scheduled 2026-06-28)

## Parking Lot
- [ ] Add calculator section: rent vs buy, buy a home, estimated taxes — pull from current plan inputs with ability to adjust and see quick impact — MOVED to Parking Lot 2026-06-27 via /next (defer to post-beta).
- [ ] Rent vs. Buy — surface as linked tool inside Scenario Planner HOME_PURCHASE event and Plan — MOVED to Parking Lot 2026-06-27 via /next (defer to post-beta).
- [ ] Add view mode for filtering/browsing different demographics — PARKED 2026-06-26 via /done. A standalone "browse demographics" mode (filter/explore typical households by age/income/region) tied to the dormant no-account comparison flow; the per-category benchmark badges already deliver the inline comparison, so a dedicated browse surface is post-beta scope. Revisit alongside the future demographics/comparison browsing mode (the retired guest flow).
- [ ] Allocation drift panel — show top 3 drifted asset classes (actual vs. target bars) in Net Worth summary rail; rebalance recommendation line [S effort, Med leverage] — PARKED 2026-06-24: Allocation view hidden behind `NEXT_PUBLIC_FEATURE_ALLOCATION` for beta; revisit when the Allocation surface is re-enabled.
- [ ] Narrative annotations — auto-detect peak, FI crossover, drawdown start; place type-on-chart labels with sentences; max 4 visible, toggleable [S effort, Med leverage] — PARKED 2026-06-24 via /next.
- [ ] Scratch-pad what-if scrubbers — live sliders (retirement age, savings rate, return, home price) overlay a ghost projection on the chart; delta readout vs. saved plan; "Save as event" to persist [M effort, High leverage]
- [ ] Event impact sparklines — 180×40px sparkline per event card showing projection-with minus projection-without; magnitude number (+$412k at FI); left-border color by event type [M effort, High leverage]
- [ ] Confidence band — fan chart with p10/p50/p90; Phase 1: deterministic ±1.5σ; Phase 2: Monte Carlo [M effort, High leverage]
- [ ] Data export (JSON) for Premium — per-user server-side export endpoint — DEFERRED, not needed for beta
- [ ] Add CSV import error handling in TransactionsDrawer — catch malformed files and show user feedback — DEFERRED, low priority
- [ ] Zillow ZORI/ZHVI by ZIP code — download monthly CSV (~50MB), serve via API route for ZIP-level rent/home value benchmarks in onboarding and rent-vs-buy calculator [M effort, High leverage] — POST-BETA
- [ ] FRED API integration — pull live savings rate (PSAVERT), 30-yr mortgage rate, PCE inflation at runtime; cache daily with hardcoded fallbacks [M effort, Med leverage] — POST-BETA
- [ ] Census ACS API — ZIP-level income percentile comparisons ("you earn more than X% of households in your ZIP"); free REST API with caching [M effort, Med leverage] — POST-BETA
- [ ] SSA benefit formula — implement PIA calculation (90%/32%/15% of AIME at bend points) for Social Security income in retirement projections; bend points update annually [M effort, High leverage] — POST-BETA
- [ ] Debt & balance benchmarks (Phase 3 of the demographic benchmark buildout) — benchmark the NET-WORTH surface, not an expense line: show "typical for your age" bands/badges for debt balances (credit card, student, auto, mortgage) and retirement/investment balances. Data: Fed SCF + NY Fed Household Debt (profiles already cite SCF and carry `suggestedAccounts` balances to aggregate from). Build: a balance-benchmark resolver keyed by age (+ percentile) reusing the suggestedAccounts aggregation; render on the net-worth + accounts views. Context: Phase 1 (income + investment-contribution badges in the Current Plan editor) shipped 2026-06-22; Phase 2 (splitting the discretionary lump into CEX sub-categories) was DECLINED — total-discretionary comparison is sufficient. [M effort, Med leverage] — POST-BETA
- [ ] Add multiple lines to net worth chart based on different market performance assumptions (e.g. 6% vs 7%) — PARKED 2026-06-26 via /next (defer to post-beta; now cheaper — reuses the peak/FI-crossover detection built for the FI + net-worth chart redesigns; sibling to the Confidence-band item). [M effort, Med leverage]
- [ ] Add recurring transactions to accounts/holdings — auto-approximate periodic additions (weekly/monthly) without manual entry; show Estimated Balance vs Latest Balance (consistent with checking/savings approach) — PARKED 2026-06-26 via /next (defer to post-beta; include account/holding linking per the feature-implementation rule). [M effort, Med leverage]
