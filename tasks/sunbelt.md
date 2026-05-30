# Sunbelt FP&A

## BoD
- [ ] 🟠 BoD deck charts: remove "Quoted"; break out Ordered Trend by Custom vs Fleet; same breakout for Invoiced and Backlog

## Forecasting
- [ ] Regroup with Wendy on Leases, Insurance, Property Tax, Management Fees
  - [x] Update Property Taxes with updated list from Wendy Teams
  - [ ] Add insurance annual outflow schedule (Jun/Jul) to 13WCF
- [ ] Fix Payroll/Bonus section
- [ ] Create Daily cash balances (book cash) plotted in a graph
- [x] Analyze overhead components vs revenue — identify fixed vs variable; build forecast based on revenue or other drivers; assess relationship to factor
- [x] 🟠 FC App: create detailed COGS/materials view — include factor effect, buffer effect, fleet %, etc.
  - [x] Custom % (Act + FC) row added to P&L, COGS-Mat, COGS-Lab drill-ins (invoice mix actualized / scheduled-production mix forward; uses model Custom % measures) — refreshed + deployed to OneDrive
  - [x] Created model measures: Weighted Factor Difficulty (base) + Backlog / Scheduled Production / Ordered / Invoiced variants ($-weighted, blanks ignored like Weighted Factor) — in _Measures, localhost
  - [x] Added Factor Difficulty (Act + FC) row beneath Custom % on P&L, COGS-Mat, COGS-Lab; added both Custom % + Factor Difficulty to Revenue drill-in. Real 0 renders 0%/0.00, no data renders — . Refreshed + deployed.


## Reporting
- [ ] Production Report Enhancements
  - [ ] Utilize Calendar table from Joy for working days
  - [x] Add MR Steel Invoicing from Sage
  - [ ] Add dates to Current and Previous WIP in card visual
  - [ ] Use historical backlog in card for Line Time / Drawings
  - [x] Create override functionality for detail table if date is selected aside from timeframe
  - [ ] Add Factors in charts / option to add factors
- [ ] Add quarter/year view to balance sheet
- [ ] 🟠 Restructure AR Summary into three tabs: Invoices, Payments (historical payment patterns), and AR Aging Balance
- [ ] 🟠 Add Custom | Fleet field to Production report (consider Operations and Backlog as well)
- [ ] Fix Timeframe and date selection in Finance and Operations reports; explore bookmark approach for switching between timeframe and date selection modes
- [ ] Build Plant Scorecard PDFs per plant: current data, historical trends, and qualitative info (project types, etc.) — per Bob's concept

## Analysis
- [x] 🟠 Analyze Whitley (Evergreen + rest) orders and invoices over time — track price, price/mod, and factors; determine if pricing shifted from 2024–1H 2025 into 2H 2025 prior to Praxis implementation

## General
- [ ] Document and standardize monthly WIP reconciliation process
  - WIP % by project, Price per project
  - Material, Labor, OH % — should these change frequently? Quarterly? Revisit in April
  - Do we need to adjust Labor/OH %'s for WIP? (per Demi question)
  - [ ] WIP Collection: Integrate with Demi and create monthly approval/review process (Praxis?)
- [ ] Ron - Sales & Executive Dashboard
  - Quote Turnaround Days metric (by Plant, Salesperson, Difficulty)
  - Quote \$, Factor, Order \$, Factor
  - Open Quotes breakdown: Plant, Difficulty, Fleet/Custom
  - Weekly/monthly high-level: Quotes/Orders/Invoices, Quote Turnaround, Total Backlog (Orders + Line Time), Revenue/GP/EBITDA, Safety
- [ ] CRM, Sales & Marketing Dashboard
  - [ ] Meet with Gary re: BD Dashboard example from Ron/Scott
  - [ ] Initial mock-up of Quote \> Order flow
  - [ ] Integrate Toni's GA data into dashboard
  - [ ] Review Toni's marketing KPI format and integrate into dashboard
  - CRM Pipeline: dealers (Frank), building type, plant, \$ Quoted \> \$ Sold
  - Marketing KPI: website analytics, NPM, Google, LinkedIn; Pre-CRM leads \> monthly
  - Activity-based KPIs
  - Bring in updated CRM data \> create mock-up
- [ ] 🟠 Integrate Sep–Dec invoice data from Whitley
- [ ] Add Britco, C&B, NWBS detailed account information
- [ ] Check if overstating COGS for WMC due to Intercompany elimination (Rev/COGS, 5023-001)
- [ ] Create survey for Power BI users to solicit feedback, get ideas for future features
- [ ] 🟠 Add recurring tasks for sunbelt to work-planner
- [ ] Meeting with Devin: production reporting check-in — getting what you need? What's missing? Still using personal Excel sheet?
- [ ] Meeting with Devin: worth setting up meeting with Joe + GM to see if they're getting what they need?
- [ ] 🟠 FC App: add projects (name + project ID) from WIP to Revenue section or dropdown — show which projects are expected to invoice in current month, next month, etc.

## Bob Review
- [ ] Pull UA estimated factors into PRAXIS (w/ Jay) — post Board Call
  - [ ] Start with Project Ramp Up at Whitley South
  - [ ] Evaluate bringing over UA factors for all remaining backlog projects
- [ ] Review with Bob: factor impact from baseline
- [ ] Ask Bob about labor and OH % for WIP entry


## Irina (Direct Report)
- [ ] Integrate new AR Logic into Fabric @delegated(Irina)
- [ ] AR Payment Report @delegated(Irina)
- [ ] Fabric Analytics Engineer certification @delegated(Irina)
- [ ] Build project roadmaps and structure for Irina on larger workstreams so she has something concrete to drive against
- [ ] Include sales eliminations process into GL Transactions automatically @delegated(Irina)
