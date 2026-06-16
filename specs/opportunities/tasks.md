# Module Tasks: Opportunities

**Module**: `opportunities` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Prerequisites

- [ ] [Project Setup](../project-setup/tasks.md) T-SETUP-13 completed — needs the backend scaffold to exist.
- [ ] [Accounts module](../accounts/tasks.md) T-ACCT-1 (schema) completed — required FK target.
- [ ] [Contacts module](../contacts/tasks.md) T-CONT-1 (schema) completed — optional FK target (may stub/defer contact validation if Contacts lags slightly, but should not ship to production without it).

---

## Implementation Tasks

| # | Task | Depends On |
|---|---|---|
| T-OPP-1 | Create `opportunities` table Alembic migration (incl. `opportunity_stage` ENUM, CHECK constraints) | Accounts T-ACCT-1, Contacts T-CONT-1 |
| T-OPP-2 | Implement `models/opportunity.py` | T-OPP-1 |
| T-OPP-3 | Implement `schemas/opportunity.py` with value/probability validators | T-OPP-2 |
| T-OPP-4 | Implement `services/opportunity_service.py`: FK validation, default-stage logic, filter/sort/paginate | T-OPP-2, T-OPP-3, Accounts + Contacts read functions |
| T-OPP-5 | Implement `routers/opportunities.py`: all 5 endpoints | T-OPP-4 |
| T-OPP-6 | Frontend: `/opportunities` board/table toggle page | T-OPP-5, Accounts + Contacts (for filters/dropdowns) |
| T-OPP-7 | Frontend: `/opportunities/:id` detail page (activity list renders empty until Activities exists) | T-OPP-5 |
| T-OPP-8 | Integration tests: default stage, value/probability rejection, stage filter, non-linear stage update | T-OPP-5 |

## Task Sequencing

```
T-OPP-1 ──► T-OPP-2 ──► T-OPP-3 ──► T-OPP-4 ──► T-OPP-5 ──┬──► T-OPP-6
                                                             ├──► T-OPP-7
                                                             └──► T-OPP-8
```

---

## Acceptance Criteria

- [ ] AC-1: Opportunity created without a `stage` defaults to `prospecting` (FR-OPP-002).
- [ ] AC-2: A `value` of 0 or negative is rejected with 422 before persistence (FR-OPP-003, SC-OPP-001).
- [ ] AC-3: A `probability` outside 0–100 is rejected with 422.
- [ ] AC-4: `PATCH` stage from any value to any other value succeeds with no sequence restriction (FR-OPP-004).
- [ ] AC-5: `GET /opportunities?stage=proposal` returns only matching records (FR-OPP-005); the board view groups all 5 stages into correct columns with accurate totals (SC-OPP-002).
- [ ] AC-6: A Sales Rep's `DELETE /opportunities/{id}` returns 403; Manager/Admin succeeds (FR-OPP-006).

## Dependencies and Prerequisites Recap

- **Hard blockers**: [Accounts](../accounts/tasks.md) T-ACCT-1, [Contacts](../contacts/tasks.md) T-CONT-1 before T-OPP-1.
- **Downstream**: [Leads](../leads/tasks.md)'s conversion logic is blocked on T-OPP-4 (needs the Opportunity-creation function). [Activities](../activities/tasks.md) is blocked on T-OPP-1 (FK target).
- **Parallelizable with**: [Contacts](../contacts/tasks.md) — both depend only on Accounts, not on each other.
