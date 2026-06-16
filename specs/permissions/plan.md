# Module Plan: Permissions

**Module**: `permissions` | **Spec**: [spec.md](spec.md)

---

## Module Architecture

The simplest module in the system — a single read-only resource, no business logic beyond an optional filter.

```
routers/permissions.py        → GET /permissions (with ?module= filter)
services/permission_service.py → list/filter query (no create/update/delete)
schemas/permission.py          → PermissionResponse only (no Create/Update schemas exist)
models/permission.py           → Permission ORM model
alembic/versions/xxx_seed_permissions.py → the catalogue's single authorship point
```

## Components and Responsibilities

| Component | Responsibility |
|---|---|
| `models/permission.py` | `Permission` table (id, code, module, action, description, created_at — no `updated_at`, immutable) |
| `schemas/permission.py` | `PermissionResponse { id, code, module, action, description }` — no Create/Update schema exists, reinforcing the read-only contract at the type level |
| `services/permission_service.py` | `list_permissions(module: str | None) -> list[Permission]` — the only function this module exposes |
| `routers/permissions.py` | `GET /permissions` gated by `require_permission("permissions:read")` |
| Seed migration | Defines every `{module}:{action}` row referenced anywhere in this spec set |
| Frontend `/admin/permissions` page | Read-only table, grouped/filterable by module — no create/edit/delete controls anywhere on the page |

## Data Flow Within the Module

```
[Seed migration runs once, at deployment]
   → INSERT permissions (code, module, action, description) for every catalogue entry

[Any request to GET /permissions]
   → [permission_service.list_permissions(module=?)]
   → SELECT * FROM permissions [WHERE module = ?] ORDER BY module, action
   → PermissionResponse[]
```

There are no write code paths in this module beyond the seed migration itself — this is a deliberate architectural simplification reflecting FR-PERM-003.

## Integration Points with Other Modules

| Module | Integration Point |
|---|---|
| [Roles](../roles/plan.md) | The Roles service calls `permission_service`'s read function to validate `permission_ids` on create/update, and to resolve full `Permission` objects for `RoleResponse.permissions[]` |
| [Authentication](../authentication/plan.md) | Transitively reads this module's table (via the Roles join) when resolving a request's effective permission set |
| Every other module | Each module's own `require_permission("{module}:{action}")` calls reference a code that must exist as a row in this module's seeded table — this is a documentation/code-review-time contract, not a runtime FK check, since permission codes are referenced as string literals in route decorators, not joined at the SQL level on every request |

---

## Architectural Decisions Specific to This Module

- **No FK from "permission code used in code" to the `permissions` table**: `require_permission("leads:create")` is a string literal in route code, not a database-validated reference. The catalogue and the code are kept in sync by code review and a startup-time consistency check (recommended: a test that asserts every string passed to `require_permission(...)` across the codebase exists in the seeded catalogue) rather than a runtime FK, since the catalogue is loaded once and the call sites are static.
- **Single seed migration as sole source of truth**: All ~34 permission rows are defined in one Alembic migration file, reviewed as a single artifact, rather than each module's migration adding its own rows — this prevents the catalogue from becoming inconsistently formatted across 9 separate PRs.
