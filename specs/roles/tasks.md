# Module Tasks: Roles

**Module**: `roles` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Prerequisites

- [ ] [Project Setup](../project-setup/tasks.md) T-SETUP-13 completed — needs the backend scaffold to exist.
- [ ] [Permissions module](../permissions/tasks.md) catalogue migration/seed completed — Roles cannot validate or attach permissions that do not yet exist.

---

## Implementation Tasks

| # | Task | Depends On |
|---|---|---|
| T-ROLE-1 | Create `roles` and `role_permissions` Alembic migration (schema per data model) | Permissions catalogue migration |
| T-ROLE-2 | Seed migration: insert the 3 system roles (Admin, Manager, Sales Rep) with their permission mappings | T-ROLE-1, Permissions catalogue seeded |
| T-ROLE-3 | Implement `models/role.py` (Role + RolePermission ORM models) | T-ROLE-1 |
| T-ROLE-4 | Implement `schemas/role.py` (Create/Update/Response, incl. nested permissions) | T-ROLE-3 |
| T-ROLE-5 | Implement `services/role_service.py`: create, update (with system-role guard), delete (with dependency + system-role guard), list (with counts) | T-ROLE-3, T-ROLE-4 |
| T-ROLE-6 | Implement `routers/roles.py`: all 5 endpoints, gated by `require_permission("roles:manage")` | T-ROLE-5, Authentication's `require_permission` dependency |
| T-ROLE-7 | Frontend: `/admin/roles` list page + `RoleForm` modal + `RolePermissionEditor` component | T-ROLE-6, Permissions module's `GET /permissions` |
| T-ROLE-8 | Integration tests: system role immutability, role-has-users 409, custom role CRUD round trip | T-ROLE-6 |

## Task Sequencing

```
T-ROLE-1 ──► T-ROLE-2 (seed)
T-ROLE-1 ──► T-ROLE-3 ──► T-ROLE-4 ──► T-ROLE-5 ──► T-ROLE-6 ──► T-ROLE-7
                                                          └──► T-ROLE-8
```

---

## Acceptance Criteria

- [ ] AC-1: `GET /roles` returns exactly 3 system roles immediately after the seed migration, each with `is_system: true` and the correct permission mappings per the data model (FR-ROLE-001).
- [ ] AC-2: `DELETE /roles/{admin_role_id}` returns 400 `SYSTEM_ROLE_IMMUTABLE` (FR-ROLE-001).
- [ ] AC-3: `PATCH /roles/{admin_role_id}` with a `name` change returns 400 `SYSTEM_ROLE_IMMUTABLE` (FR-ROLE-001).
- [ ] AC-4: Creating a custom role with a chosen permission subset, assigning it to a test user, and exercising that user's access matches exactly the selected permissions (FR-ROLE-002, SC-ROLE-002).
- [ ] AC-5: Attempting to delete a role assigned to ≥1 user returns 409 `ROLE_HAS_USERS` with the correct count (FR-ROLE-003).
- [ ] AC-6: `GET /roles` list items include accurate `permission_count` and `user_count` fields (FR-ROLE-004).

## Dependencies and Prerequisites Recap

- **Hard blocker**: [Permissions](../permissions/tasks.md) T-PERM-1/T-PERM-2 (catalogue schema + seed) must complete before T-ROLE-1/T-ROLE-2.
- **Downstream**: [Users](../users/tasks.md) is blocked on T-ROLE-2 (seed roles must exist before seed users can be assigned a `role_id`).
