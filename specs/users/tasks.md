# Module Tasks: Users

**Module**: `users` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Prerequisites

- [ ] [Project Setup](../project-setup/tasks.md) T-SETUP-13 completed — needs the backend scaffold to exist.
- [ ] [Roles module](../roles/tasks.md) schema + seed (3 system roles) completed — Users cannot assign a `role_id` to anything that doesn't exist yet.
- [ ] [Authentication module](../authentication/tasks.md)'s `core/security/passwords.py` exists (T-AUTH-2) — Users delegates hashing to it rather than duplicating bcrypt logic.

---

## Implementation Tasks

| # | Task | Depends On |
|---|---|---|
| T-USR-1 | Create `users` table Alembic migration | Roles schema (FK target) |
| T-USR-2 | Implement `models/user.py` | T-USR-1 |
| T-USR-3 | Implement `schemas/user.py` (Create/Update/SelfUpdate/Response) | T-USR-2 |
| T-USR-4 | Implement `services/user_service.py`: create (email uniqueness, role validation, password hashing), update (last-admin guard), list (search/filter/sort), self-update | T-USR-2, T-USR-3, Authentication T-AUTH-2, Roles read function |
| T-USR-5 | Implement `routers/users.py`: all 6 endpoints | T-USR-4, Authentication's `require_permission` (once available — may stub with no-op gate until T-AUTH-4 lands) |
| T-USR-6 | Write the seed-users script/migration (3 demo users, idempotent) | T-USR-4 |
| T-USR-7 | Frontend: `/admin/users` list + `UserForm` | T-USR-5, Roles' `GET /roles` |
| T-USR-8 | Frontend: `/profile` self-service page (display name edit + Admin's embedded Users tab) | T-USR-5 |
| T-USR-9 | Integration tests: email conflict, last-admin lockout, deactivation blocks login (requires Authentication's login endpoint for the last assertion) | T-USR-5, T-USR-6, Authentication T-AUTH-5 |

## Task Sequencing

```
T-USR-1 ──► T-USR-2 ──► T-USR-3 ──► T-USR-4 ──► T-USR-5 ──┬──► T-USR-6 ──► T-USR-9
                                                            ├──► T-USR-7
                                                            └──► T-USR-8
```

---

## Acceptance Criteria

- [ ] AC-1: Admin can create a user with a valid role; the user appears in `GET /users` immediately (FR-USR-001, FR-USR-004).
- [ ] AC-2: Duplicate email on create returns 409 `EMAIL_CONFLICT` (FR-USR-006).
- [ ] AC-3: `UserResponse` never includes `hashed_password` in any endpoint's output, verified by schema inspection (FR-USR-007).
- [ ] AC-4: Attempting to deactivate or role-change the sole active Admin returns 400 `LAST_ADMIN_LOCKOUT` (FR-USR-005, SC-USR-001).
- [ ] AC-5: A non-Admin calling `GET /users` or `PATCH /users/{other_id}` receives 403 (FR-USR-002, FR-USR-003).
- [ ] AC-6: `PATCH /users/me` updates only `display_name`; a `role_id` or `is_active` field in the body is rejected with 422, not silently ignored (FR-USR-003).
- [ ] AC-7: All 3 seed users can log in immediately after the seed step runs, each receiving the correct role in their JWT (SC-USR-003) — this assertion requires Authentication's login endpoint and is the natural integration test bridging the two modules.

## Dependencies and Prerequisites Recap

- **Hard blocker**: [Roles](../roles/tasks.md) T-ROLE-1/T-ROLE-2 before T-USR-1.
- **Soft dependency**: [Authentication](../authentication/tasks.md) T-AUTH-2 (password hashing utility) before T-USR-4; T-AUTH-4 (`require_permission`) before T-USR-5 can be fully gated (may stub initially).
- **Downstream**: [Leads](../leads/tasks.md) and [Activities](../activities/tasks.md) are blocked on T-USR-1 (FK target for `created_by_user_id`).
