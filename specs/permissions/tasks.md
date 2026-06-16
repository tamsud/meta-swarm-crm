# Module Tasks: Permissions

**Module**: `permissions` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Prerequisites

- [ ] [Project Setup](../project-setup/tasks.md) T-SETUP-13 completed — needs the backend scaffold (`models/`, `alembic/` baseline) to exist. Otherwise this is the zero-CRM-dependency, first-built CRM module in the system.

---

## Implementation Tasks

| # | Task | Depends On |
|---|---|---|
| T-PERM-1 | Create `permissions` table Alembic migration (schema per data model) | Backend project scaffolding only |
| T-PERM-2 | Write the seed migration enumerating the full catalogue (one row per `{module}:{action}` across all 9 modules) | T-PERM-1 |
| T-PERM-3 | Implement `models/permission.py` | T-PERM-1 |
| T-PERM-4 | Implement `schemas/permission.py` (`PermissionResponse` only) | T-PERM-3 |
| T-PERM-5 | Implement `services/permission_service.py` (`list_permissions`) | T-PERM-3, T-PERM-4 |
| T-PERM-6 | Implement `routers/permissions.py` (`GET /permissions`) | T-PERM-5 |
| T-PERM-7 | Frontend: `/admin/permissions` read-only table page | T-PERM-6 |
| T-PERM-8 | Write a codebase-consistency test asserting every `require_permission("...")` string literal used anywhere in the backend exists in the seeded catalogue | T-PERM-2, all other modules' route definitions (run this task last, after every module is built) |

## Task Sequencing

```
T-PERM-1 ──► T-PERM-2 (seed)
T-PERM-1 ──► T-PERM-3 ──► T-PERM-4 ──► T-PERM-5 ──► T-PERM-6 ──► T-PERM-7
T-PERM-8 runs last, after all other modules' routers exist
```

---

## Acceptance Criteria

- [ ] AC-1: `GET /permissions` returns a non-empty catalogue immediately after the seed migration, with zero duplicate `code` values (FR-PERM-001, SC-PERM-002).
- [ ] AC-2: `GET /permissions?module=leads` returns only Leads-module rows (FR-PERM-002).
- [ ] AC-3: No `POST`, `PATCH`, or `DELETE` route exists for `/permissions` anywhere in the router (FR-PERM-003) — verified by route-table inspection, not just a runtime 404.
- [ ] AC-4: Every permission code referenced by any other module's `require_permission(...)` call exists in the seeded catalogue (T-PERM-8 passes).

## Dependencies and Prerequisites Recap

- **No blockers** — this module can and should be the first implemented.
- **Downstream**: [Roles](../roles/tasks.md) T-ROLE-1/T-ROLE-2 are blocked on T-PERM-1/T-PERM-2.
