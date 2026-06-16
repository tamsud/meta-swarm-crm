# Module Tasks: Dockerization & Seed Data

**Module**: `deployment` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Prerequisites

- [ ] [Project Setup](../project-setup/tasks.md) T-SETUP-13 completed.
- [ ] All 9 CRM modules' service layers complete and stable: [Permissions](../permissions/tasks.md), [Roles](../roles/tasks.md), [Users](../users/tasks.md), [Authentication](../authentication/tasks.md), [Accounts](../accounts/tasks.md), [Contacts](../contacts/tasks.md), [Opportunities](../opportunities/tasks.md), [Leads](../leads/tasks.md), [Activities](../activities/tasks.md) — the seed script calls every one of their `create_*` (and Leads' `convert_*`) service functions directly, so none may be a stub.

This is the **last module** implemented in the project. Do not begin until every other module's acceptance criteria pass.

---

## Implementation Tasks

| # | Task | Depends On |
|---|---|---|
| T-DEPLOY-1 | Write `backend/Dockerfile` (Python 3.11-slim, install deps, run migrations + uvicorn on container start) | All 9 modules' migrations finalized |
| T-DEPLOY-2 | Write `frontend/Dockerfile` (Node v22.17.1 build stage → static-serving runtime stage) | All 9 modules' frontend pages finalized |
| T-DEPLOY-3 | Write `docker-compose.yml` (backend + frontend services, named volume for the SQLite file, shared network, env vars matching Project Setup's `.env.example` contracts) | T-DEPLOY-1, T-DEPLOY-2 |
| T-DEPLOY-4 | Implement `backend/app/scripts/seed.py`'s `seed_all()`: 3 demo Users, 50+ Accounts, 50+ Contacts, 50+ Opportunities (all 5 stages), 50+ Leads (all 4 statuses incl. real conversions), 50+ Activities (all 3 types) — each via the owning module's real service function | All 9 modules' service layers |
| T-DEPLOY-5 | Implement `clear_all()`: deletes all CRM records while preserving Permissions/Roles/the 3 demo Users | T-DEPLOY-4 |
| T-DEPLOY-6 | Expose `POST /seed` and `DELETE /seed` endpoints (Admin-permission-gated for clear; seed itself may be open in dev or also Admin-gated — match each CRM module's existing `seed:*`-style permission convention) | T-DEPLOY-4, T-DEPLOY-5 |
| T-DEPLOY-7 | Frontend: `/admin/seed` page wiring ("Seed demo data" + "Clear all data" buttons, result panel, confirmation dialog) | T-DEPLOY-6 |
| T-DEPLOY-8 | Integration tests: full `docker compose up` → restart → data-persists check → `down -v` → data-gone check; seed idempotency check; clear-preserves-catalogue check; referential-integrity spot check on seeded converted Leads | T-DEPLOY-3, T-DEPLOY-6 |

## Task Sequencing

```
T-DEPLOY-1 ──┐
              ├──► T-DEPLOY-3 ──────────────────────────────────────────────┐
T-DEPLOY-2 ──┘                                                                │
T-DEPLOY-4 ──► T-DEPLOY-5 ──► T-DEPLOY-6 ──► T-DEPLOY-7                       │
                                       └──────────────────────────────────────┴──► T-DEPLOY-8
```

---

## Acceptance Criteria

- [ ] AC-1: `docker compose up` from a clean checkout starts both services and reaches a usable state in under 3 minutes (FR-DEPLOY-001, SC-DEPLOY-001).
- [ ] AC-2: `docker compose restart` and `docker compose down` (without `-v`) both preserve 100% of existing data; `docker compose down -v` followed by `up` produces an empty database (FR-DEPLOY-002, SC-DEPLOY-002).
- [ ] AC-3: `POST /seed` produces at least 50 records for each of Accounts, Contacts, Leads, Opportunities, Activities, plus the 3 demo Users, in under 30 seconds (FR-DEPLOY-005, SC-DEPLOY-003).
- [ ] AC-4: Calling `POST /seed` twice in a row does not double any entity's count (FR-DEPLOY-006, SC-DEPLOY-004).
- [ ] AC-5: Seeded Leads include all 4 statuses and at least one real, atomically-converted Lead with a valid `converted_opportunity_id` (FR-DEPLOY-008).
- [ ] AC-6: Seeded Opportunities include all 5 stages; seeded Activities include all 3 types with a realistic mix of single- and dual-linked records (FR-DEPLOY-009, FR-DEPLOY-010).
- [ ] AC-7: `DELETE /seed` removes all CRM data but the Permissions catalogue, the 3 system Roles, and the 3 demo Users remain intact and able to log in afterward (FR-DEPLOY-007).
- [ ] AC-8: A non-Admin's `DELETE /seed` call returns 403.

## Dependencies and Prerequisites Recap

- **Hard blockers**: every other module in the project (Project Setup + all 9 CRM modules) must be complete — this module has no partial-implementation path, since its seed script calls real service functions across the entire system.
- **No downstream blockers** — this is the final module; nothing else in the documented system depends on it.
