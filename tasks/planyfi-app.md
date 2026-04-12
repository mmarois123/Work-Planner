# Planyfi — App

## Engineering
- [x] Review hidden debug sections (ProjectionVerificationTable, DetailedProjectionBreakdown) — decide keep or delete (by 2026-04-11)
- [ ] Accessibility pass — add keyboard handlers to backdrop overlays, aria-labels to icon-only buttons, keyboard support to clickable table rows

### Free tier / monetization (prerequisite for public beta)
Business model: Free tier is session-only (full feature access, no persistence). Premium ($5/mo or $50/yr) unlocks save, scenario comparison, unlimited saved scenarios, CSV export, priority support.
- [x] API route audit — flag routes that must hit server (yahoo-finance quote, notifications/generate) vs routes that can run guest-local
- [x] Build `guestStore` — in-memory store mirroring the repository/api-client shape (accounts, budgets, scenarios, events, holdings)
- [x] Data layer router — branch `isGuest` → `guestStore` vs `api-client` (wrapper around existing repos)
- [x] Update `middleware.ts` — make app routes public; keep API routes auth-gated
- [x] `ProfileContext` guest branch — when `user === null`, return `{ isGuest: true, currentUserId: 'guest', plan: 'free' }` without DB fetch; wire the already-defined `isGuest` field
- [x] Onboarding wizard guest path — final submit step branches: guest → `guestStore`, authed → API (reuses existing census-based builder untouched)
- [ ] Upgrade migration flow — on sign-up + checkout success, push `guestStore` contents to API in one call (conversion-critical)
- [ ] Upgrade prompts — on nav away, `Ctrl+S`, manual save clicks; persistent "session only — sign up to save" indicator in UI
- [ ] Stripe Checkout integration — wire to existing `plan: free|premium` Clerk metadata; webhook → `clerkClient.users.updateUserMetadata`
- [ ] Feature gating — enforce `isPremium` on save actions, scenario comparison, >N saved scenarios, CSV export
- [ ] CSV export for Premium (feature-gated)

### Infrastructure / ops (before inviting friends)
- [ ] Automated SQLite backups — daily `sqlite3 .backup` → upload to S3/R2/B2 (critical: loss surface is Premium user data)
- [ ] Error monitoring — Sentry (or similar) free tier
- [ ] Railway staging environment — second service pointed at a branch, separate volume
- [ ] Data export (JSON) for Premium — per-user server-side export endpoint

### Deferred / reconsidered
- [~] ~~Provisioning layer — automate per-user Railway instance creation via API~~ — DROPPED. Shared multi-tenant SQLite + Clerk userId scoping already covers isolation. Per-instance economics kill $5/mo margin. Revisit only as Enterprise tier.
- [~] ~~Custom domain routing — map user.planyfi.app to each user's Railway instance~~ — DROPPED with the above.
- [~] ~~Data export — let users download their SQLite file~~ — REPLACED with per-user JSON export (SQLite file would leak other users' data in shared-DB model).

- [ ] Add CSV import error handling in TransactionsDrawer — catch malformed files and show user feedback
- [x] Refactor TransactionsDrawer add-transaction from modal to inline form for consistency with other drawers
- [x] Unify edit mode state management across drawers (editingId pattern vs mode-based vs boolean)

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
- [x] Update Milestones module
- [ ] Update event timeline
- [ ] Allow users to enter plan numbers at high-level category (Investments, Fixed, Discretionary) instead of requiring category or account level detail
- [x] Explore bulk update option for assets
- [x] Update FI Calculator section on financial planner page — evaluate if still needed, brainstorm improvements
- [x] Rework Fund Strategy deficit logic: remove forced 2-step order (reduce contributions → withdrawal); allow user to mix and match order; explore situation-based configuration
- [x] Update Asset Allocation report: show variances between target and current allocations; add ability to include/exclude accounts (e.g. exclude checking/savings); simplify Tax Status chart with focus on asset allocation; brainstorm additional improvements
- [ ] Add recurring transactions to accounts/holdings — auto-approximate periodic additions (weekly/monthly) without manual entry; show Estimated Balance vs Latest Balance (consistent with checking/savings approach)

## Bugs / Issues
- [x] Irina: document Fabric Lakehouse issue — table not ready after loading @delegated(Irina)
