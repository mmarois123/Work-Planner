# Planyfi — App

## Engineering
- [ ] Accessibility pass — add keyboard handlers to backdrop overlays, aria-labels to icon-only buttons, keyboard support to clickable table rows

### Free tier / monetization (prerequisite for public beta)
Business model: Free tier is session-only (full feature access, no persistence). Premium ($5/mo or $50/yr) unlocks save, scenario comparison, unlimited saved scenarios, CSV export, priority support.
- [x] Upgrade prompts — on nav away, `Ctrl+S`, manual save clicks; persistent "session only — sign up to save" indicator in UI
- [ ] Stripe Checkout integration — wire to existing `plan: free|premium` Clerk metadata; webhook → `clerkClient.users.updateUserMetadata`
- [x] Feature gating — enforce `isPremium` on save actions, scenario comparison, >N saved scenarios, CSV export
- [x] CSV export for Premium (feature-gated)

### Infrastructure / ops (before inviting friends)
- [x] Automated SQLite backups — daily `sqlite3 .backup` → upload to S3/R2/B2 (critical: loss surface is Premium user data)
- [x] Create Sentry project (Next.js platform) and set `NEXT_PUBLIC_SENTRY_DSN` in Railway
- [x] Configure R2 bucket + set `R2_*` env vars in Railway — create bucket, generate API token, add credentials
- [x] Set up daily cron trigger for `/api/admin/backup` — Railway cron service or GitHub Action
- [ ] Railway staging environment — second service pointed at a branch, separate volume
- [ ] Data export (JSON) for Premium — per-user server-side export endpoint

### Deferred / reconsidered
- [~] ~~Provisioning layer — automate per-user Railway instance creation via API~~ — DROPPED. Shared multi-tenant SQLite + Clerk userId scoping already covers isolation. Per-instance economics kill $5/mo margin. Revisit only as Enterprise tier.
- [~] ~~Custom domain routing — map user.planyfi.app to each user's Railway instance~~ — DROPPED with the above.
- [~] ~~Data export — let users download their SQLite file~~ — REPLACED with per-user JSON export (SQLite file would leak other users' data in shared-DB model).

- [ ] Add CSV import error handling in TransactionsDrawer — catch malformed files and show user feedback
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
- [ ] Quick-compare button — "What if I retire 5 years earlier?"
- [ ] Monte Carlo simulation mode — return variance modeling
- [ ] Interactive demo — hosted read-only instance with sample data
- [ ] Add contact, submit feedback, and support functionality to app

- [ ] Send beta version to Zach, Julie, AJ, James, and others (blocked on: session-only free tier + backups + error monitoring)
- [ ] Onboarding module improvements — refine UX and flows as design evolves

- [ ] Add refinance mortgage / other debt as a future event type
- [ ] Tighten up home buying and tracking in future events, accounts, and current plan
- [ ] Finalize onboarding modules with 3 paths
- [ ] Update event timeline
- [ ] Allow users to enter plan numbers at high-level category (Investments, Fixed, Discretionary) instead of requiring category or account level detail
- [ ] Add recurring transactions to accounts/holdings — auto-approximate periodic additions (weekly/monthly) without manual entry; show Estimated Balance vs Latest Balance (consistent with checking/savings approach)

- [x] Add reset button to banner for guest/free users
- [ ] Add linked account option to both Current Plan and Accounts (not just one)
- [ ] When adding new investment/savings plan category, insert new line directly — no modal
- [ ] Merge Linked Account and Funding Source into single concept with combined pop-up and icon; explore clearer terminology for "where it's coming from and going to"
- [ ] Scenario Comparison feature: ability to hide/adjust Current Plan, Events, Milestones, Market Assumptions; full plan summary/net worth for a given year; line chart plotting net worth, income, expenses for up to 3 scenarios
- [ ] Add ability to hide/archive elapsed and applied events (events drawer, event timeline, or both)
- [ ] If user enters plan mid-year with no prior plan, assume same for full year; otherwise use appropriate mix based on effective dates
- [ ] Debt accounts — add support for: Auto loan (original amount, term, APR, start/end date, auto-calc payment w/ override), Mortgage (loan type, rate, amount, start/end date, auto-calc payment, taxes/insurance/PMI), Student loans, Personal loans, Credit cards
- [ ] Add monthly view to financial planner, especially for 1–10 year timeframe
- [ ] Verify that after mortgage on home event ends, property taxes, insurance, and maintenance costs continue
- [ ] Fix Future Events and Fund Strategy mobile layout bugs
- [ ] Fix date entry for mobile across app — easy to type or select (bug found in profile birthday field)
- [ ] Onboarding/quick entry: start with accounts first, then auto-populate Current Plan categories
- [ ] Add category list (fixed, discretionary, custom) when adding new expense — typeable field with dropdown similar to Empower; evaluate if useful elsewhere (accounts/holdings)

## Bugs / Issues
- [x] Guest store data loss on HMR — dev-mode Hot Module Reload resets module-level `state` in `guest-store.ts`, losing all in-memory data and bouncing users back to onboarding via `OnboardingGuard`
- [x] CurrentPlanDrawer Save Plan button not disabled during save — `triggerSaveRef` pattern needs an `isSavingRef` plumbed back from PlanEditor
- [x] Account edit form (AccountEditModal) — missing visible field validation error messages (silently blocks submit on empty name, no feedback for invalid APY/interest)
- [x] Account setup wizard (AccountSetupWizard) — no validation on empty draft account names before creation
