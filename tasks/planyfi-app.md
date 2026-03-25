# Planyfi — App

## Engineering
- [ ] Provisioning layer — automate per-user Railway instance creation via API
- [ ] Custom domain routing — map user.planyfi.app to each user's Railway instance
- [ ] Data export — let users download their SQLite file
- [ ] Railway staging environment
- [ ] Build out in-app notification system
- [ ] Trigger notification prompt when future event date elapses — ask user to update current plan with event impacts
- [ ] Add CSV import error handling in TransactionsDrawer — catch malformed files and show user feedback
- [ ] Accessibility pass — add keyboard handlers to backdrop overlays, aria-labels to icon-only buttons, keyboard support to clickable table rows
- [ ] Onboarding: Make data writes atomic — wrap sequential API calls (household, accounts, balances, budget) in a transaction or add rollback on partial failure. Currently silent failures leave `onboardingCompleted=1` with broken/missing data
- [ ] Onboarding: Fix double-click race condition — `handleDemographicsNext()` doesn't set `isSubmitting=true`, allowing duplicate `submitWizardState()` calls that create duplicate accounts/budgets
- [ ] Onboarding: Add loading indicator during initial guard check (`page.tsx:55-79`) — currently blank screen while API queries run
- [ ] Onboarding: Await `router.push()` after submit (`page.tsx:180`) — if navigation fails, button stuck permanently disabled with no recovery
- [ ] Onboarding accessibility — add `aria-label`/`htmlFor` to form inputs, `aria-expanded` on partner checkbox, keyboard support (Tab+Enter) to Demographics percentile table rows
- [ ] Onboarding: Validate filing status against partner status — "Married Filing Jointly" allowed with `hasPartner=false`, causing incorrect tax calculations
- [ ] Onboarding: Trim and validate partner name — whitespace-only strings accepted, creating invalid household members. Also block zero-income scenario for retired users (`grossSalary=0` rejected by validation)
- [x] Employer match — add `employerMatchPercent` field to 401K/HSA rows with percentage-based matching, route combined amount to linked account

## Product
- [ ] Onboarding module improvements — refine UX and flows as design evolves
- [ ] Onboarding: Add inline validation error messages — "Next" button silently does nothing when required fields are missing; users have no idea why they can't advance. Also fix disabled button opacity (`opacity-40` renders as ~0.9, visually indistinguishable from enabled)
- [ ] Onboarding: Fix salary placeholder visibility — "75,000" placeholder is indistinguishable from a real value in dark theme; users think field is pre-filled
- [ ] Onboarding: Add post-skip empty state CTA — after skipping onboarding, empty dashboard has no link back to onboarding; user stranded with "No plan data"
- [ ] Onboarding: Mobile responsive fixes — `grid-cols-2` without breakpoint on Filing Status/State dropdowns (cramped at 375px); progress bar step labels overflow at mobile width
- [ ] Onboarding: Minor input/UX polish — validate negative balances on non-debt accounts, explain 50% savings rate cap, warn when expenses exceed take-home, indicate which selected accounts still have $0 balance
- [ ] Add mortgage calculator: show 30 vs 15 yr vs 5/1 ARM, pull current rates, allow user to adjust overall interest rate to compare impact across loan types
- [ ] Enhance home purchase calculator: model after Zillow, add maintenance and other homeownership costs
- [ ] Research (via Claude) what mortgage info a homeowner typically has access to — use to inform current plan input fields
- [ ] Add message to rent vs buy and home buying event: "Renting an equivalent home for $x/month or less would be a better financial decision over 10 years"
- [ ] Add calculator section: rent vs buy, buy a home, estimated taxes — pull from current plan inputs with ability to adjust and see quick impact
- [ ] Rent vs. Buy — compare two homes by address, or rent vs. buy a single property
- [ ] Rent vs. Buy — pull property data by address (Zillow/Redfin API or manual entry)
- [ ] Rent vs. Buy — surface as linked tool inside Scenario Planner HOME_PURCHASE event and Plan
- [ ] Scenario comparison — side-by-side delta view of two scenarios
- [ ] Mobile-responsive layout — full mobile compatibility pass across all pages and components; touch-friendly interactions throughout
- [ ] Integrate US census data more deeply into app
- [ ] Add view mode for filtering/browsing different demographics
- [ ] Quick-compare button — "What if I retire 5 years earlier?"
- [ ] Monte Carlo simulation mode — return variance modeling
- [ ] Interactive demo — hosted read-only instance with sample data
- [ ] Hide or badge future-event-created accounts ($0 balance) until the event occurs (e.g., "Buy a Home — Mortgage")
- [x] Fix "Life Ex.." label truncation on event timeline; clarify visual state for hidden/disabled events

## Bugs / Issues
- [x] Onboarding: Benchmark 50th percentile creates $3,255/yr budget deficit on day 1 — new users see negative Net Remaining immediately after completing onboarding
- [x] Onboarding: if couple or family selected, prompt to add partner and dependents to profile (with option to edit names later)
- [x] Onboarding: set expenses to Joint by default
- [x] Current Plan: remove option to add Employer Match
- [ ] Rename "Guilt-Free Expenses" — consider "Discretionary Expenses" or alternative
