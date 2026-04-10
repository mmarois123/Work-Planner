# Planyfi App — Archive (2026-04)

- [x] Move all drawers to slide in from the left, except profile and notifications
- [x] Update Accounts page assets: make certain attributes editable via edit icon, but render quantities/values/allocations as standard input boxes
- [x] Review all other input sections for consistency with Current Plan styling
- [x] Asset holdings display: show ticker with full name in smaller text below; add tag for holding/market type; include input fields for qty, price, value, and % of total
- [x] Add retry logic or user-facing toast for transient API failures in repository layer (e.g. scenarioEventsRepo.getByScenario) — currently throws and logs to console only
