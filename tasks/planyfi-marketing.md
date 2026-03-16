# Planyfi — Marketing

## Campaigns

### Website (Done)
- [x] Landing page live at planyfi.app — hero, problem/solution, features, waitlist CTA
- [x] Website hero — headline, subheadline, product screenshot or animation
- [x] Website problem section — "You've outgrown spreadsheets. You don't need a consultant."
- [x] Website features section — Scenario Planner, Plan, Net Worth, Cash Flow
- [x] Website FAQ — 8 Q&As on /faq page (details/summary, no JS)
- [x] Privacy policy + Terms of service — real pages with hello@planyfi.app
- [x] Pricing page — Free vs Premium ($5/mo or $50/yr)
- [x] Domain + DNS finalized — planyfi.app via Cloudflare (DKIM, SPF MX, SPF TXT)
- [x] Meta tags + OG images on all pages — Chrome headless OG generation
- [x] Sitemap + robots.txt — @astrojs/sitemap auto-generates at build
- [x] Favicon — SVG rising chart with green gradient

### Website (Remaining)
- [ ] Website social proof — currently hidden, need real early-user quotes
- [ ] Product screenshot or demo animation for hero section
- [ ] A/B test headline copy or CTA wording

### Email
- [x] Choose email platform — Resend (API key: planyfi-marketing-waitlist)
- [x] Waitlist email capture with confirmation — POST /api/waitlist, graceful degradation
- [x] Waitlist welcome email — sent via hello@planyfi.app on signup
- [ ] Launch announcement sequence (2-3 emails)
- [ ] Onboarding drip — feature highlight emails post-signup
- [ ] Monthly newsletter or FIRE tips series

### Launch & Distribution
- [ ] Reddit launch posts — r/financialindependence, r/Fire, r/personalfinance
- [ ] Product Hunt — prep assets, hunter outreach, timing
- [ ] Hacker News "Show HN"
- [ ] Twitter/X build-in-public thread series
- [ ] Indie Hackers profile + milestone posts
- [ ] Podcast outreach — FI and personal finance shows

### Growth
- [ ] "Calculate your FIRE date" free tool for lead gen
- [ ] Affiliate / referral program (post-launch)
- [ ] SEO keyword tracking — monitor rankings for target terms
- [ ] Backlink outreach to FIRE bloggers and personal finance sites

## Content

### Published (5 posts)
- [x] "Understanding Your FIRE Numbers" — understanding-fire-numbers.mdx
- [x] "Multi-Year Financial Planning" — multi-year-financial-planning.mdx (2026-01-20)
- [x] "Coast FIRE Explained" — coast-fire-explained.mdx (2026-02-10)
- [x] "What is Financial Independence?" — what-is-financial-independence.mdx (2026-02-24)
- [x] "Do You Need a Financial Planner?" — do-you-need-a-financial-planner.mdx (2026-03-10)

### Planned
- [ ] "Why I built PlanyFI" — founder story (high priority for launch)
- [ ] "The problem with spreadsheet financial planning" — problem-aware traffic
- [ ] "How to build a 10-year financial model for your life" — top of funnel
- [ ] "Barista FIRE vs Coast FIRE — what's the difference?" — SEO keyword gap
- [ ] "How much do I need to retire at 40/45/50?" — calculator-style SEO content
- [ ] Comparison post: "PlanyFI vs spreadsheet vs financial advisor"

## Analytics
- [x] Vercel Analytics enabled via adapter config
- [ ] Set up Vercel Analytics dashboard and monitor traffic
- [ ] Google Search Console — submit sitemap, monitor indexing
- [ ] Track waitlist conversion rate (visits → signups)
- [ ] Set up basic funnel: landing → pricing → waitlist signup
