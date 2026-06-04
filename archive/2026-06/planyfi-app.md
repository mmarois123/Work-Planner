# Planyfi App — Archive (2026-06)

- [x] Research available US datasets for household income, saving/investing, and spending — delivered themed HTML report at design-mockups/us-data-report.html
- [x] Home Purchase event summary renders `"$NaN home, undefined% down, undefined% rate, 3% appreciation"` in the Future Events drawer card. Seen on a fresh Quick Setup demo plan (seeded HOME_PURCHASE event) — home price / down payment / rate fields come through undefined when the event is auto-seeded rather than user-entered. Likely the seeded composite payload is missing fields the card summary reads, or the summary doesn't guard against undefined.
