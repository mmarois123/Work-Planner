# PlanyFI Backlog

> Single source of truth for app and marketing work.
> Edit freely — sections are marked for LLM find-and-replace.
> Last updated: 2026-03-08 (rev 2)

---

<!-- SECTION: launch-blockers -->
## 🔴 Launch Blockers
_Everything here must be done before paid users._

### App
- [ ] Authentication — NextAuth.js, replace client-side userId context with real sessions
- [ ] Provisioning layer — automate per-user Fly.io instance creation via API
- [ ] Custom domain routing — map `user.planyfi.app` to each user's Fly instance
- [ ] Data export — let users download their SQLite file
- [ ] **Onboarding module** — prompt for age, family size, location; auto-populate income/expense/savings benchmarks from US Census / BLS data (baked in at build time); user selects percentile (25th, median, 75th, 90th); alternative path to start from scratch with guided tutorial through accounts setup and current plan setup
- [ ] **Net worth projection validation** — fully audit that NW and all accompanying values (account balances, tax estimates, surplus/deficit, contributions) are calculated correctly across future years; establish a regression test process so future engine changes cannot silently break core calculations; block new engine features until this is complete

### Marketing
- [ ] Landing page live at planyfi.app — hero, problem/solution, features, waitlist CTA
- [ ] Waitlist email capture with confirmation
- [ ] Privacy policy + Terms of service
- [ ] Pricing page (even a placeholder)
- [ ] Domain + DNS finalized
<!-- /SECTION: launch-blockers -->

---

<!-- SECTION: app-features -->
## 🔵 App Features

### Rent vs. Buy Calculator
- [ ] Standalone `/rent-vs-buy` page
- [ ] Compare two homes by address, or rent vs. buy a single property
- [ ] Total Cost of Ownership (TCO) for both options — mortgage P&I, taxes, insurance, HOA, maintenance vs. rent + opportunity cost of down payment
- [ ] Pull property data by address (Zillow / Redfin API or manual entry fallback)
- [ ] Surface as a linked tool inside Scenario Planner HOME_PURCHASE event and inside Plan

### Financial Planner & Scenario Planner
- [ ] Hero section — net worth projection chart above the fold
- [ ] Scenario cards — sparklines + key metrics (FIRE date, projected NW at 65)
- [ ] Guided wizards — Home Purchase, Coast FIRE, Job Change, Baby, Sabbatical
- [ ] Scenario comparison — side-by-side delta view of two scenarios
- [ ] Milestone events — FINANCIAL_INDEPENDENCE, BABY_BORN with end conditions

### Dashboard & Net Worth
- [ ] Interactive NW chart — click a data point to see account breakdown at that date
- [ ] Asset allocation donut — target vs. actual drift indicator
- [ ] "Path to FI" widget — progress bar + projected date

### Plan
- [ ] Effective date timeline visualization
- [ ] Income tax summary card — estimated annual burden per plan

### Accounts
- [ ] Holding price refresh — auto-fetch on load, show staleness indicator
- [ ] Account merge preview — show diff before confirming

### Transactions & Budget Actuals
- [ ] LLM-powered transaction categorization via Claude API
- [ ] CSV import — support multiple bank formats
- [ ] Recurring transaction detection — flag likely recurring items

### Technical Debt
- [ ] Remove Dexie.js / IndexedDB dependency (fully replaced by SQLite)
- [ ] Add server-side userId validation (currently client-only)
- [ ] API error handling audit — consistent error shapes across all routes
- [ ] Test coverage — useMultiYearProjection hook
- [ ] Fly.io staging environment
<!-- /SECTION: app-features -->

---

<!-- SECTION: marketing -->
## 🟢 Marketing

### Website
- [ ] Hero — headline, subheadline, product screenshot or animation
- [ ] Problem section — "You've outgrown spreadsheets. You don't need a consultant."
- [ ] Features section — Scenario Planner, Plan, Net Worth, Cash Flow
- [ ] Social proof — placeholder for early user quotes
- [ ] FAQ — pricing, data ownership, how it works
- [ ] Meta tags + OG images on all pages
- [ ] Sitemap + robots.txt

### Content
- [ ] "Why I built PlanyFI" — founder story
- [ ] "What is Coast FIRE and how do I model it?" — SEO + product demo
- [ ] "The problem with spreadsheet financial planning" — problem-aware traffic
- [ ] "How to build a 10-year financial model for your life" — top of funnel

### Acquisition
- [ ] r/financialindependence, r/Fire, r/personalfinance — launch posts
- [ ] Product Hunt — prep assets, hunter outreach, timing
- [ ] Hacker News "Show HN"
- [ ] Twitter/X build-in-public thread series
- [ ] Indie Hackers profile + milestone posts

### Email
- [ ] Choose platform — Resend, ConvertKit, or Loops
- [ ] Waitlist welcome email
- [ ] Launch announcement sequence (2–3 emails)
- [ ] Onboarding drip — feature highlight emails post-signup
<!-- /SECTION: marketing -->

---

<!-- SECTION: ideas -->
## 💡 Ideas
_Not yet scoped. Capture only — don't action without promoting to a section above._

- [ ] Mobile-responsive layout pass
- [ ] Shareable scenario links — read-only, time-limited
- [ ] PDF/PNG export of projection charts
- [ ] "What if I retire 5 years earlier?" quick-compare button
- [ ] Monte Carlo simulation mode — return variance modeling
- [ ] Interactive demo — hosted read-only instance with sample data
- [ ] "Calculate your FIRE date" free tool for lead gen
- [ ] Public API for power users
- [ ] Affiliate / referral program (post-launch)
- [ ] Podcast outreach — FI and personal finance shows
<!-- /SECTION: ideas -->

---

<!-- SECTION: shipped -->
## ✅ Shipped

- [x] Product identity — PRODUCT.md with purpose, mission, vision
- [x] Scenario Planner — generates Plan-shaped objects, renders via Plan template
- [x] Composite events — HOME_PURCHASE, RETIREMENT, JOB_CHANGE via registry
- [x] Multi-year projection engine — useScenarioNetWorth orchestrator
- [x] Allocation engine — surplus routing and withdrawal priority
- [x] Tax calculator — progressive brackets, FICA, state taxes
- [x] Accounts + Plan — complete with effective-dated plans
<!-- /SECTION: shipped -->
