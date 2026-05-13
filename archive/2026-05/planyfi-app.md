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
