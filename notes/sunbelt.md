# Sunbelt Notes

## Recurring FP&A SOP — reference

Source: `inputs/FP&A SOP.xlsx` → "Task Grid" sheet. The live recurring tasks are in
`tasks/sunbelt.md` under `## Recurring (FP&A SOP)`; this table preserves the full SOP detail
(distribution, source/output, dependencies, instruction sheet). Each task in the workbook has its own
detail sheet of the same name with step-by-step instructions and links.

| # | Task | Freq | Timing | Distribution | Input / Source | Output | Dependencies | Detail sheet |
|---|---|---|---|---|---|---|---|---|
| 1 | Praxis Refresh | Weekly | Mon PM | — | Praxis data | PBI | Praxis data available | Praxis Refresh |
| 2 | Labor Hours | Weekly | Mon PM | — | Labor data | PBI | Labor data available | Labor Hours |
| 3 | Weekly Operations Report | Weekly | Mon PM | Ron | Praxis data | PBI, PDF | Praxis Refresh | Weekly Operations Report |
| 4 | 13WCF | Weekly | Tue | Bob, LJ | 13WCF data | Excel, PDF | Data available | 13WCF |
| 5 | Update ParameterCurrentMonth | Monthly | Day 2 | — | Attributes DF > ParameterCurrentMonth | Model Refresh | — | Update ParameterCurrentMonth |
| 6 | Update Sales Eliminations | Monthly | Day 2 | — | Data > Eliminations > Sales Eliminations.xlsx | Model Refresh | — | (see Sales Eliminations) |
| 7 | Monthly WIP | Monthly | Day 2 | Demi, Wendy | WIP data | Excel | WIP data complete | Monthly WIP |
| 8 | Material Cost - Factor Analysis | Monthly | Day 2 | Bob, Wendy, Robert | Previous Month Excel | Current Month Excel | Current Month Praxis Factors | Material Cost - Factor Analysis |
| 9 | Monthly Operations Report | Monthly | Day 3 | Sales VPs, Ron, Bob, VPs, Mfg Directors, Robert | Operations Report.xlsx | Excel | Operations data complete | Monthly Operations Report |
| 10 | Update Latest Closed Month (through GP) | Monthly | Close | — | Attributes DF > ParameterLatestClosedMonth | Model Refresh | Month Close | Update Latest Closed Month |
| 11 | P&L by Company | Monthly | Close + 1 | Ron, Bob | GL data | Excel, PDF | GL Close complete | P&L by Company |
| 12 | Monthly BoD Presentation | Monthly | BoD Meeting − 2 | Bob, BoD | Various sources | PowerPoint | BoD Template complete | BoD Presentation |
| 13 | Bank Financials | Monthly | Day 21 | Bob | Finalized GL data | Excel | GL finalized | Bank Financials |
| 14 | Quarterly Bank Financials | Quarterly | Day 21 | Bob | Quarterly GL data | Excel | Quarter close complete | Quarterly Bank Financials |
| 15 | Quarterly BoD Presentation | Quarterly | BoD Meeting − 2 | Bob, BoD | Quarterly data | PowerPoint | Quarterly BoD Template ready | Quarterly BoD Presentation |
| — | Granting Access to PBI | One-Off | — | — | User Access.xlsx | — | PBI License Granted | Granting Access to PBI |

Notes:
- "Day N" = Nth calendar day of the month. "Close" = month-end-close milestone (defaulted to ~business
  day 7 in the task file until the close milestone is marked done). "BoD Meeting − 2" = 2 business days
  before the board meeting (driven by the "Next BoD meeting" anchor line in the task file).
- Row 15 "Granting Access to PBI" is a one-off procedure, not a recurring task — kept here for reference
  only.

## BoD

## 13 Week Cash Flow

### Changes to Whitley: Schedule vs Budget — Cash Flow Impact

Using schedule vs budget for Whitley drives short-term cash consumption, with revenue recovery expected in May/Jun. Key dynamics to document:

- Switching from conservative budget assumptions to the schedule they are actually executing
- Fast-growing backlog + improving use of Praxis scheduling is driving higher volume
- Higher near-term volume consumes cash before revenue is realized
- Call out 3–5 specific plants most affected

Narrative thread: this isn't deterioration — it's a timing effect from executing better than budgeted.

## Reporting

### Scheduled Production in Praxis
- Is there a day each week where schedules need to be updated (like WIP)? Or can they remove/replace projects a day+ later?
- Is there direction to have schedules filled through a certain timeframe (2-4 months)?

### Plant Scorecard / One-Pager — Design Notes

Goal: single slide or one-pager per plant showing operational performance. BOD level only — plants will have other metrics at a more detailed level, referenced only when there is a material issue.

**Per plant metrics (not in order of importance):**
- WIP Adj.
- Rev per labor hour
- Rev per week
- Target WIP Adj. Rev per week

Granularity options to explore: Per plant / Per customer / Per end user (market)?

**Adjusted Factor Ranking:**
- PM Backlog, orders, invoicing, trend?
- Rev $ Weighted Target
- Difficulty tiers (1–5) with factor ranges: 0.602 / 0.583 / 0.562 / 0.531 / 0.501

**Backlog/Orders breakdown ($ — Initial Factor / Adj. Factor):**
- PM Backlog
- Orders
- Invoicing
- CM Backlog

**Other metrics:**
- Quoted (as sold) vs actual (as built) factor variance
- Plant forecasted GP (WIP Adj.?)

**Other ways plants affect margin (materially):**
- Warranty (QC, $)
- OT
- Use of contract labor
- Scheduling
- Safety

## Analysis

### SKU Pricing Hypothesis — Estimating vs. Actual Purchasing

SKUs in Praxis are updated weekly with pricing from Sage. When estimators build quotes/BOMs, they select from a list of SKUs and may choose:
- The higher-priced SKU
- An average-priced SKU
- The one they expect will actually be used

The gap: no substitutable SKUs or generic/placeholder items that can be mapped back to actual purchases and inventory. This creates a disconnect between estimated material costs and what's actually bought/used — likely a driver of factor variance.

Worth investigating: can we introduce generic/substitutable SKU logic to improve estimate-to-actual matching?

### Inventory / Purchasing / BOM Analysis — CCC

Components to investigate:
- Actual SKU costs
- Specialty SKUs (write-ins)
- Services (warranty charge, state labels, Engineering)
- Contingencies
- Purchasing Take Offs
- Change Orders
- Cycle Counts

### Call with Jay — SKU / BOM / Estimating Notes

**Comparable/substitutable SKU mapping?**
Not really — currently only category > sub-category. Could go one level deeper for certain sub-categories to get like-for-like comparisons.

**How do estimators select SKUs when building BOMs?**
They select sub-assemblies or create Add-Ons when necessary. Not pulling from a master inventory or recent purchases list.

**How quickly do price changes flow into Praxis/estimating BOMs?**
- Items on contract: updated automatically
- Non-commodity items (caulking, windows, etc.): reviewed monthly using last price paid

## Irina (Direct Report)

### 1:1 Alignment — May 2026

**What's gone well**
- Picking up routine ownership cleanly: Praxis refresh, 13WCF, BR reconciliation, stepping in on routine tasks when Wendy and I were out
- Pushing work into Fabric and moving us off Power BI dataflows toward something that scales

**Where to focus**
- Proactive ownership and follow-through — driving work forward and over-communicating, not waiting until something's done or until I ask
- On my side: owe her better roadmaps and structure on larger projects so she has something concrete to drive against

**Scope going forward**
- End-to-end ownership of the Fabric workspace: lakehouse, medallion architecture, dataflows, pipelines, notebooks
- Taking on new analyses and reports that she'll present to stakeholders directly

**Update cadence**
- EoD Monday, Wednesday, Friday to start
- Goal: step down to Tuesday/Friday, then eventually Friday-only as rhythm develops
- Format: Progress (what moved) / Stuck (where she needs help) / Next (what she's picking up)

**On the horizon**
- Path to share appreciation plan and/or quarterly bonus eligibility as company grows
- Potential for officially designated full-time remote depending on corporate office policy
- These are paths, not commitments

## General

### Ron — 3 Key Focus Areas

1. Estimating / pricing right
2. Purchasing materials / inventory right (materials = ~50% of costs)
3. Volume — increase backlog with orders, capture demand

### Invoicing Process (Plant Level)

The GM initiates the invoicing process in Praxis. The Project Coordinator gets the appropriate signoffs from GM, QC, and Sales, then notifies the Accounting Manager that the building is ready to be invoiced. Once invoicing is completed, the Accounting Manager notifies the Project Coordinator, who enters the data in Praxis.

### Praxis Schedule Confidence Indicator

Idea: add a checkbox to Praxis schedule indicating whether a given week is scheduled or not. Alternative/complement: show a confidence interval of x% or $ within plant target amount for unscheduled weeks.

### Safety Incident Rate Formulas

**Lost Time Incident Rate (LTIR)**
(Number of lost time cases × 200,000) / Total hours worked
→ Represents lost time incidents per 100 full-time employees. The 200,000 baseline = 100 employees × 40 hrs/week × 50 weeks.

**Total Recordable Incident Rate (TRIR)**
(Number of recordable incidents × 200,000) / Total hours worked
→ Standardizes recordable incidents across different-sized companies using the same 200,000 baseline.

**DART Rate** (Days Away, Restricted, or Transferred)
(Number of DART incidents × 200,000) / Total hours worked
→ OSHA-approved rate for injuries/illnesses resulting in missed work, restricted duties, or job transfer. Same 200,000 multiplier.
