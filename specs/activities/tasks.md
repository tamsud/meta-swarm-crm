# Module Tasks: Activities

**Module**: `activities` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Prerequisites

- [ ] [Project Setup](../project-setup/tasks.md) T-SETUP-13 completed — needs the backend scaffold to exist.
- [ ] [Contacts](../contacts/tasks.md) T-CONT-1 (schema) completed — FK target.
- [ ] [Opportunities](../opportunities/tasks.md) T-OPP-1 (schema) completed — FK target.
- [ ] [Users](../users/tasks.md) T-USR-1 (schema) completed — FK target for `created_by_user_id`.

---

## Implementation Tasks

| # | Task | Depends On |
|---|---|---|
| T-ACT-1 | Create `activities` table Alembic migration (incl. `activity_type` ENUM, link-required CHECK constraint, `created_by_user_id` FK) | Contacts T-CONT-1, Opportunities T-OPP-1, Users T-USR-1 |
| T-ACT-2 | Implement `models/activity.py` | T-ACT-1 |
| T-ACT-3 | Implement `schemas/activity.py` with the link-required model validator | T-ACT-2 |
| T-ACT-4 | Implement `services/activity_service.py`: FK validation, ownership filter, filter/sort/paginate | T-ACT-2, T-ACT-3, Contacts + Opportunities read functions |
| T-ACT-5 | Implement `routers/activities.py`: all 5 endpoints | T-ACT-4 |
| T-ACT-6 | Frontend: `/activities` unified timeline page | T-ACT-5 |
| T-ACT-7 | Frontend: wire Contact detail "History" tab + "days since last contact"; wire Opportunity detail activity list + "Log activity" button | T-ACT-5, Contacts T-CONT-7, Opportunities T-OPP-7 |
| T-ACT-8 | Integration tests: link-required rejection (both client-equivalent and DB CHECK), dual-link support, type filter, ownership 403 | T-ACT-5 |

## Task Sequencing

```
T-ACT-1 ──► T-ACT-2 ──► T-ACT-3 ──► T-ACT-4 ──► T-ACT-5 ──┬──► T-ACT-6
                                                             ├──► T-ACT-7
                                                             └──► T-ACT-8
```

---

## Acceptance Criteria

- [ ] AC-1: Activity creation with both `contact_id` and `opportunity_id` null returns 400 `ACTIVITY_NO_LINK` before any DB write occurs (FR-ACT-002, SC-ACT-001).
- [ ] AC-2: Activity creation with both `contact_id` and `opportunity_id` set succeeds (FR-ACT-003).
- [ ] AC-3: `GET /activities?type=call` returns only call-type activities (FR-ACT-005).
- [ ] AC-4: `activity_date` defaults to the creation timestamp when omitted (FR-ACT-004).
- [ ] AC-5: A Sales Rep cannot update/delete an Activity logged by a different user (403); Manager/Admin can (FR-ACT-006, SC-ACT-002).
- [ ] AC-6: Contact detail's "days since last contact" and History tab, and Opportunity detail's activity list, all render correctly once this module is wired in (cross-module integration check).

## Dependencies and Prerequisites Recap

- **Hard blockers**: [Contacts](../contacts/tasks.md) T-CONT-1, [Opportunities](../opportunities/tasks.md) T-OPP-1, [Users](../users/tasks.md) T-USR-1.
- **No downstream blockers** — Activities is a terminal/leaf module; no other module's schema or service depends on it. It is, however, read by the cross-cutting Dashboard page and by Contacts'/Opportunities' detail pages (frontend-level integration only, not a schema dependency).
- This module can be considered the **last** module fully completed in a strict dependency-ordered build, alongside or just after Leads.
