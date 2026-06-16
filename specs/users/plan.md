# Module Plan: Users

**Module**: `users` | **Spec**: [spec.md](spec.md)

---

## Module Architecture

Standard four-layer module structure, plus the cross-cutting "last active Admin" invariant living in the service layer:

```
routers/users.py        → /users (admin CRUD) + /users/me (self-service)
services/user_service.py → create/update/list, last-admin guard, password hashing delegation
schemas/user.py          → UserCreate, UserUpdate, UserSelfUpdate, UserResponse (never includes hashed_password)
models/user.py           → User ORM model
```

## Components and Responsibilities

| Component | Responsibility |
|---|---|
| `models/user.py` | `User` table (id, email, hashed_password, display_name, role_id FK, is_active, timestamps) |
| `schemas/user.py` | `UserCreate { email, password, display_name?, role_id }`, `UserUpdate { role_id?, is_active?, display_name? }` (Admin), `UserSelfUpdate { display_name }` (self), `UserResponse` (excludes `hashed_password` always) |
| `services/user_service.py` | Email-uniqueness check (409), password hashing delegation to Authentication's `core/security/passwords.py`, role-existence validation (calls Roles module), last-active-Admin count guard before any deactivation/role-change write |
| `routers/users.py` | `GET /users`, `POST /users`, `GET /users/{id}`, `PATCH /users/{id}` (all `require_permission("users:*")`), `GET /users/me`, `PATCH /users/me` (`require_permission("users:manage-self")`) |
| Seed step | Creates the 3 demo users, idempotently (skip if email already exists) |
| Frontend `/admin/users` page | List (Email, Display Name, Role badge, Status badge, Created), `UserForm` (create/edit), disabled Active-toggle + role-dropdown with tooltip when `isLastActiveAdmin` |
| Frontend `/profile` page | Self-service display-name edit; Admin sees an embedded Users tab |

## Data Flow Within the Module

```
[Admin submits UserForm: email, password, display_name, role_id]
   → POST /users
   → [user_service: SELECT users WHERE email] → if found: 409 EMAIL_CONFLICT
   → [user_service: validate role_id exists — calls Roles module's read function]
   → [core/security/passwords.hash_password(password)]
   → INSERT users row (is_active default true)
   → UserResponse (no hashed_password field)

[Admin deactivates a user OR changes their role away from Admin]
   → PATCH /users/{id} {is_active: false} or {role_id: <non-admin-role>}
   → [user_service: if target.role.name == 'Admin' AND target.is_active == true]
        → SELECT COUNT(*) FROM users WHERE is_active = true AND role.name = 'Admin'
        → if count == 1 (this user is the last one): 400 LAST_ADMIN_LOCKOUT
   → else: UPDATE users row → UserResponse

[Any authenticated user updates their own display name]
   → PATCH /users/me {display_name}
   → [user_service: UPDATE users SET display_name WHERE id = current_user.id]
   → UserResponse (own record only; role_id/is_active in the body are rejected with 422 if present)
```

## Integration Points with Other Modules

| Module | Integration Point |
|---|---|
| [Roles](../roles/plan.md) | `user_service` validates `role_id` against Roles' read function on every create/update; Users' frontend `UserForm` populates its Role dropdown from `GET /roles` |
| [Authentication](../authentication/plan.md) | `POST /auth/login` and `get_current_user` both call into `user_service`'s credential-lookup and active-status-check functions; password hashing/verification is shared via Authentication's `core/security/passwords.py` |
| [Leads](../leads/plan.md) | Leads' service reads `users.id` to populate `created_by_user_id` and resolves display names for the UI's "created by" column |
| [Activities](../activities/plan.md) | Same pattern as Leads, for `activities.created_by_user_id` |

---

## Architectural Decisions Specific to This Module

- **Soft deactivation only, no hard delete**: Hard-deleting a User would orphan or require cascading through `leads.created_by_user_id`/`activities.created_by_user_id` (both `ON DELETE SET NULL`), losing audit history. Deactivation (`is_active = false`) preserves the FK and the historical "who created this" record while fully blocking the account's access.
- **Last-Admin guard checked at write-time, not via a DB constraint**: Counting "active Admins" requires a join through Roles, which is not expressible as a simple CHECK constraint; the guard lives in `user_service` immediately before the UPDATE statement, inside the same transaction, to avoid a race between the count-check and the write.
