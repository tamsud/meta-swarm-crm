# Module Tasks: Leads

**Module**: `leads` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Prerequisites

- [ ] [Project Setup](../project-setup/tasks.md) T-SETUP-13 completed — needs the backend scaffold to exist.
- [ ] [Accounts](../accounts/tasks.md) T-ACCT-4 (service layer, incl. find-or-create-by-name function) completed.
- [ ] [Contacts](../contacts/tasks.md) T-CONT-4 (service layer, incl. find-by-email function) completed.
- [ ] [Opportunities](../opportunities/tasks.md) T-OPP-4 (service layer, incl. create function) completed.
- [ ] [Users](../users/tasks.md) T-USR-1 (schema) completed — FK target for `created_by_user_id`.

This is the most heavily-blocked module in the system — do not start backend implementation until all four prerequisites are satisfied.

---

## Implementation Tasks

| # | Task | Depends On |
|---|---|---|
| T-LEAD-1 | Create `leads` table Alembic migration (incl. `lead_status` ENUM, `created_by_user_id` FK) | Users T-USR-1, Opportunities T-OPP-1 (FK target for `converted_opportunity_id`) |
| T-LEAD-2 | Implement `models/lead.py` | T-LEAD-1 |
| T-LEAD-3 | Implement `schemas/lead.py` | T-LEAD-2 |
| T-LEAD-4 | Implement the state-machine validation function in `services/lead_service.py` | T-LEAD-2, T-LEAD-3 |
| T-LEAD-5 | Implement the ownership-filter logic in `services/lead_service.py` | T-LEAD-4, Users + Roles/Permissions effective-permission resolution available |
| T-LEAD-6 | Implement the conversion orchestration function in `services/lead_service.py` | T-LEAD-4, Accounts T-ACCT-4, Contacts T-CONT-4, Opportunities T-OPP-4 |
| T-LEAD-7 | Implement `routers/leads.py`: all 6 endpoints | T-LEAD-4, T-LEAD-5, T-LEAD-6 |
| T-LEAD-8 | Frontend: `/leads` list page (status tabs, search) | T-LEAD-7 |
| T-LEAD-9 | Frontend: `/leads/:id` detail page (`LeadStatusControl`, Convert button, Converted badge/link) | T-LEAD-7 |
| T-LEAD-10 | Integration tests: full state machine (all valid + invalid transitions), conversion happy path, double-conversion rejection, ownership 403, atomicity-under-failure test (force a mid-transaction error and assert no orphaned rows) | T-LEAD-7 |

## Task Sequencing

```
T-LEAD-1 ──► T-LEAD-2 ──► T-LEAD-3 ──► T-LEAD-4 ──┬──► T-LEAD-5 ──┐
                                                     └──► T-LEAD-6 ──┴──► T-LEAD-7 ──┬──► T-LEAD-8
                                                                                       ├──► T-LEAD-9
                                                                                       └──► T-LEAD-10
```

---

## Acceptance Criteria

- [ ] AC-1: All valid transitions succeed and all invalid transitions (including any transition away from `lost`) are rejected with 400 `INVALID_LEAD_TRANSITION` (FR-LEAD-003, SC-LEAD-001).
- [ ] AC-2: Conversion of a qualified, unconverted Lead creates exactly one Opportunity, reuses or creates exactly one Account and one Contact, and updates the Lead's `converted_opportunity_id` — verified with zero additional API calls beyond the one `convert` call (FR-LEAD-006, SC-LEAD-002).
- [ ] AC-3: A forced failure injected mid-conversion-transaction leaves zero new rows in `accounts`, `contacts`, `opportunities`, and `leads.converted_opportunity_id` remains NULL (atomicity).
- [ ] AC-4: Re-converting an already-converted Lead returns 400 `LEAD_ALREADY_CONVERTED` with the existing `converted_opportunity_id` in the body.
- [ ] AC-5: A Sales Rep cannot update/delete a Lead created by a different user (403); Manager/Admin can act on any Lead (FR-LEAD-005, SC-LEAD-003).

## Dependencies and Prerequisites Recap

- **Hard blockers**: [Accounts](../accounts/tasks.md) T-ACCT-4, [Contacts](../contacts/tasks.md) T-CONT-4, [Opportunities](../opportunities/tasks.md) T-OPP-4, [Users](../users/tasks.md) T-USR-1 — all four must complete before T-LEAD-1/T-LEAD-6.
- **No downstream blockers** — no other module depends on Leads' table, though [Activities](../activities/tasks.md) is built in parallel/after and may reference Leads-created Opportunities incidentally (not a schema dependency).
