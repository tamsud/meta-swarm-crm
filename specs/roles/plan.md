# Module Plan: Roles

**Module**: `roles` | **Spec**: [spec.md](spec.md)

---

## Module Architecture

Standard four-layer module structure:

```
routers/roles.py        → HTTP routing for /roles, permission-gated by "roles:manage"
services/role_service.py → create/update/delete business rules, system-role guard, dependency check
schemas/role.py          → RoleCreate, RoleUpdate, RoleResponse (incl. nested permissions[])
models/role.py           → Role ORM model + RolePermission association object
```

## Components and Responsibilities

| Component | Responsibility |
|---|---|
| `models/role.py` | `Role` table (id, name, description, is_system, timestamps); `RolePermission` association table (role_id, permission_id, created_at) |
| `schemas/role.py` | `RoleCreate { name, description?, permission_ids[] }`, `RoleUpdate { name?, description?, permission_ids? }`, `RoleResponse { ..., permissions: PermissionResponse[], permission_count, user_count }` |
| `services/role_service.py` | Validates `permission_ids` exist (calls into Permissions module's read function); enforces `is_system` immutability on name/permission-set; pre-delete check against `users.role_id` |
| `routers/roles.py` | `GET /roles`, `POST /roles`, `GET /roles/{id}`, `PATCH /roles/{id}`, `DELETE /roles/{id}` — all gated by `require_permission("roles:manage")` |
| Frontend `/admin/roles` page | List (Name, Description, Type badge, Permission count, User count), `RoleForm` (name, description, multi-select permission checklist grouped by module), disabled controls for system rows |
| Frontend `RolePermissionEditor` component | Renders the Permission catalogue (fetched from the Permissions module's `GET /permissions`) as a grouped checklist; `disabled` when editing a system role |

## Data Flow Within the Module

```
[Admin submits RoleForm: name + selected permission_ids]
   → POST /roles or PATCH /roles/{id}
   → [role_service: validate name uniqueness]
   → [role_service: for each permission_id, validate it exists in `permissions` table]
   → [role_service: if target is_system=true → reject any name/permission-set change]
   → INSERT/UPDATE roles row
   → INSERT/DELETE role_permissions rows (diff against existing set)
   → RoleResponse (with resolved permissions[] joined back for the response)

[Admin deletes a role]
   → DELETE /roles/{id}
   → [role_service: SELECT COUNT(*) FROM users WHERE role_id = {id}]
   → if count > 0: 409 ROLE_HAS_USERS {detail includes count}
   → if is_system: 400 SYSTEM_ROLE_IMMUTABLE
   → else: DELETE role_permissions (cascade) → DELETE roles row → 204
```

## Integration Points with Other Modules

| Module | Integration Point |
|---|---|
| [Permissions](../permissions/plan.md) | `role_service` calls the Permissions module's read function to validate `permission_ids` and to resolve the full `Permission` objects for `RoleResponse.permissions[]` |
| [Users](../users/plan.md) | Users' `UserForm` populates its Role dropdown from this module's `GET /roles`; Users' service validates `role_id` exists by calling into this module's read function; the "last active Admin" guard in Users counts `users.role_id` joined to `roles.name = 'Admin'` |
| [Authentication](../authentication/plan.md) | `get_current_user`'s permission-resolution step joins `users.role_id → roles → role_permissions → permissions` to build the effective permission set |

---

## Architectural Decisions Specific to This Module

- **System roles are protected at the service layer, not via a separate immutable table**: `is_system` is a boolean flag on the same `roles` table, checked in every write-path service function, rather than splitting system/custom roles into separate tables — keeping the Users FK and the Roles list page uniform across both kinds.
- **Permission diffing on update**: `PATCH /roles/{id}` with a new `permission_ids` array replaces the entire set (delete-then-insert within one transaction) rather than supporting incremental add/remove operations — simpler API contract, acceptable given Role edits are infrequent admin actions, not high-frequency writes.
