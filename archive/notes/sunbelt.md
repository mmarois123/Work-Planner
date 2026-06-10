# Sunbelt Notes — Archive

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
