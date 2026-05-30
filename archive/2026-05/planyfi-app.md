# Planyfi — App — Archive (2026-05)

## Engineering
- [x] Accessibility pass — add keyboard handlers to backdrop overlays, aria-labels to icon-only buttons, keyboard support to clickable table rows
- [x] Accessibility: add aria-labels to icon-only toolbar buttons, keyboard handlers to sortable `<th>` (TransactionsDrawer), expandable `<tr>` (VarianceTracker), clickable `<div>` in HoldingCard and PlanView
- [x] Add empty state handling to: TransactionsDrawer (no transactions), BalanceHistoryTab (no entries), ProfileDrawer household members list, AllocationPriorityList/DeficitPriorityList (no buckets)
- [x] Clerk production instance — create Production instance in Clerk dashboard, swap `sk_test_`/`pk_test_` keys for live keys on Railway production service (currently using Development keys)

## Product
- [x] Add contact, submit feedback, and support functionality to app
- [x] Onboarding module improvements — refine UX and flows as design evolves
- [x] Finalize onboarding modules with 3 paths
- [x] Allow users to enter plan numbers at high-level category (Investments, Fixed, Discretionary) instead of requiring category or account level detail
- [x] Add linked account option to both Current Plan and Accounts (not just one)
- [x] When adding new investment/savings plan category, insert new line directly — no modal
- [x] Merge Linked Account and Funding Source into single concept with combined pop-up and icon; explore clearer terminology for "where it's coming from and going to"
- [x] If user enters plan mid-year with no prior plan, assume same for full year; otherwise use appropriate mix based on effective dates
- [x] Credit card account enrichment — extend CC editor with loan-detail-style fields (APR per card, minimum payment tracking, payoff estimates)
- [x] Onboarding/quick entry: start with accounts first, then auto-populate Current Plan categories
- [x] Add % of take-home pay as an input option for expenses in Edit Current Plan
- [x] Rename onboarding path "Start from Scratch" — consider "Quick Start" or similar
- [x] Add ability to change household member colors during onboarding
- [x] Make first entered checking and savings accounts the primary cash flow accounts by default

## Security
- [x] Rate limiting — add rate limits on `/api/feedback`, `/api/finance/*`, and auth-adjacent endpoints (consider `@upstash/ratelimit` or middleware-based)
- [x] Request body size limits — cap POST body size on `/api/guest-migrate` and `/api/onboarding/submit` to prevent memory/write abuse
- [x] Admin token hardening — rotate `ADMIN_SECRET`, consider IP allowlist or short-lived tokens for `/api/admin/*` routes
- [x] CORS policy — explicitly configure allowed origins in `next.config.ts` headers for API routes
- [x] Content-Security-Policy header — add CSP to restrict script sources (requires auditing inline scripts and third-party loads)

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
- [x] Sentry setup — create Sentry project, set `NEXT_PUBLIC_SENTRY_DSN` on Railway (`app/error.tsx` already has `Sentry.captureException`; optional: `SENTRY_AUTH_TOKEN`/`SENTRY_ORG`/`SENTRY_PROJECT` for source maps)
- [x] Home Purchase event should populate full mortgage details on auto-created accounts — set `originalAmount`, `loanTermMonths`, `loanStartDate`, `pairedAccountId`, and escrow fields from wizard inputs so AccountEditModal and MortgageBreakdownSummary work immediately
- [x] Auto-pair Mortgage and Real Estate accounts when created together — set `pairedAccountId` on both when created via Account Setup wizard or Home Purchase event
- [x] Event type buttons truncated in Add Event drawer — text cut to "Custo...", "Job Ch..." at drawer width; consider icons-only with tooltips or scrollable single-row layout
- [x] Home Purchase form UX for second/vacation home — "Rent to Remove" is confusing for existing homeowners buying another property; add "second home" toggle or auto-detect from existing Real Estate accounts; also fix truncated labels in Ongoing Costs section ("Property Tax Rate", "Home Appreciation" cut off)
- [x] Insurance unit mismatch between HomePurchaseForm (monthly) and AccountEditModal (annual) — standardize or auto-convert when transferring event data to accounts
- [x] Onboarding: capture partner/spouse info in Quick Start
- [x] Onboarding: add age/DOB field
- [x] Onboarding: improve Expenses & Savings step clarity
- [x] Onboarding: minor UX polish
- [x] Post-onboarding guided experience
- [x] Improve "FI Date: Not reached" first impression
- [x] Expand event templates — add composite events for common life changes
- [x] Chart default views — Outlays chart should default to stacked/breakout view
- [x] Add "Real" vs "Nominal" tooltip
- [x] Research (via Claude) what mortgage info a homeowner typically has access to
- [x] Mobile-responsive layout — full mobile compatibility pass across all pages and components
- [x] Interactive demo — hosted read-only instance with sample data
- [x] Onboarding plan: show owner names on income/investment line items
- [x] Onboarding: partner salary placeholder
- [x] Onboarding: add childcare/daycare as default expense category when user has dependents
- [x] Onboarding plan: progressive disclosure
- [x] Onboarding: filter account types shown for dependents
- [x] Onboarding accounts review: show net worth total at bottom of account list
- [x] Mobile: surface "What's Next" checklist on mobile
- [x] Dashboard: rename "Outlays" chart tab to "Expenses" or "Spending"
- [x] Guided tour: expand from 3 to 5+ steps
- [x] Standardize drawer width on mobile
- [x] Standardize overlay theme
- [x] Standardize form controls across overlays
- [x] Add category list (fixed, discretionary, custom) when adding new expense
- [x] Add upgrade prompt/link on onboarding screen where previous session cleared message appears
- [x] Remove balance and account name prompts during onboarding if user can edit both on the following screen
- [x] Add owner tag to accounts, consistent with Current Plan
- [x] Auto-link investment and savings accounts by default
- [x] Student loan and auto loan payments should auto-populate in plan when entered as accounts
- [x] Show net worth total at bottom of accounts screen on mobile
- [x] Equivalent rent icon should open popup showing actual numbers and logic used to calculate equivalent rent
- [x] Auto-link 401k to savings plan line after onboarding
- [x] Add tooltips to icon-only buttons across app
- [x] Disable beforeunload dialog for guest/session-only users
- [x] Home Purchase event fails to save for guest/session users
- [x] Income Type dropdown on mobile clips last items
- [x] Property Tax % in Account Edit Modal calculated against loan amount instead of home value
- [x] Frequency toggle (Wk/Mo/Yr) converts existing values instead of changing entry mode
- [x] Milestones badge shows "4" but 6 milestones are listed — badge count is wrong
- [x] "Collectables" typo in account type selection during onboarding — should be "Collectibles"
- [x] Mobile nav tabs are icon-only with no visible labels
- [x] Fix Daily SQLite Backup GitHub Actions workflow failure
- [x] Fix mobile layout — constrain to screen width, eliminate horizontal scroll/movement
- [x] Bug: hitting Upgrade within profile view on mobile doesn't show checkout screen — blocked by profile modal
- [x] Convert all drawers to full pages on mobile to eliminate bugginess
- [x] Quick Start onboarding resets on last step when logged in as guest
- [x] Current Plan still has slight horizontal scroll on mobile
- [x] "Customize your accounts" screen broken on mobile — account names not visible, balances difficult to see
- [x] Duplicate blue confirmation messages appearing when adding accounts in onboarding
- [x] Ticker search on accounts/holdings page broken on mobile
- [x] Hide link icon in onboarding if there's no budget item to link to
- [x] Subtotals (investments and others) not updating when adding new account amounts
- [x] "Create plan" starts at bottom of screen — should start at top
- [x] Fundrise appearing in onboarding without being explicitly entered — investigate and remove
- [x] Next button no longer shows as green after clicking first tutorial popup on mobile
- [x] Account balances not saving from onboarding — critical fix needed [P1]
- [x] Employer Match popup styling inconsistent with other popups on Current Plan page
- [x] No option to clear "What's Next" to-do list on mobile; items don't auto-dismiss after completion

## Product
- [x] Merge Quick Start and US Benchmarks onboarding paths — use optional fields so user can click through quickly or fill in their own info
- [x] Remove High Yield Savings account type — redundant alongside Savings
- [x] Fixed and discretionary expense totals should default to match itemized values
- [x] Add "Homeowner?" checkbox to Quick Start onboarding

## Bugs / Issues
- [x] Changing state in Quick Start onboarding doesn't update income or other benchmark values as expected
