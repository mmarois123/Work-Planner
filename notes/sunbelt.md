# Sunbelt Notes

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

### Inventory / Purchasing / BOM Analysis — CCC

Components to investigate:
- Actual SKU costs
- Specialty SKUs (write-ins)
- Services (warranty charge, state labels, Engineering)
- Contingencies
- Purchasing Take Offs
- Change Orders
- Cycle Counts

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
