# Module Tasks: Authentication

**Module**: `authentication` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Prerequisites

- [ ] [Project Setup](../project-setup/tasks.md) T-SETUP-13 completed — needs the backend scaffold (`core/security/` package) to exist.
- [ ] [Users module](../users/tasks.md) schema and service layer exist (at minimum: `users` table with `hashed_password`, `role_id`, `is_active`) — Authentication has nothing to verify credentials against otherwise.
- [ ] [Roles module](../roles/tasks.md) and [Permissions module](../permissions/tasks.md) seed data exists — `GET /auth/me`'s permission resolution requires the `role_permissions` join to return real data.

This module **cannot start implementation** before Users has at least a minimal schema migration applied. It may be scaffolded (file skeletons, JWT utility functions, unit tests for token issuance/verification in isolation) in parallel with Users, but integration testing requires Users to be functional.

---

## Implementation Tasks

| # | Task | Depends On |
|---|---|---|
| T-AUTH-1 | Implement `core/security/jwt.py`: token issuance (`create_access_token`) and verification (`decode_access_token`) using HS256, configurable secret + expiry via environment variables | None (pure utility, unit-testable standalone) |
| T-AUTH-2 | Implement `core/security/passwords.py`: `hash_password`, `verify_password` using bcrypt cost ≥ 12 | None |
| T-AUTH-3 | Implement `core/security/dependencies.py`: `get_current_user` (decode token → load User → load Role → load effective Permissions) | T-AUTH-1, Users schema, Roles schema, Permissions schema |
| T-AUTH-4 | Implement `core/security/dependencies.py`: `require_permission(code)` dependency factory | T-AUTH-3 |
| T-AUTH-5 | Implement `routers/auth.py`: `POST /auth/login` (delegates to Users service for credential check, returns 401 on failure/inactive, issues JWT on success) | T-AUTH-1, T-AUTH-2, Users service |
| T-AUTH-6 | Implement `routers/auth.py`: `GET /auth/me` (returns profile + role + permissions via `get_current_user`) | T-AUTH-3 |
| T-AUTH-7 | Retrofit `Depends(get_current_user)` + `Depends(require_permission(...))` onto every existing route in every other module | T-AUTH-3, T-AUTH-4, all other modules' routers must already exist |
| T-AUTH-8 | Frontend: `AuthContext` (token/user/permissions state, `login()`, `logout()`, `hasPermission()`) | T-AUTH-5, T-AUTH-6 |
| T-AUTH-9 | Frontend: Axios request interceptor (attach Bearer token) + response interceptor (401 → clear context + redirect to `/login`) | T-AUTH-8 |
| T-AUTH-10 | Frontend: `/login` page (two-panel responsive layout), `RequireAuth` and `RequirePermission` route guard components | T-AUTH-8, T-AUTH-9 |
| T-AUTH-11 | Integration tests: full login → protected-call → logout round trip; expired-token rejection; deactivated-user login rejection | T-AUTH-5 through T-AUTH-10 |

## Task Sequencing

```
T-AUTH-1, T-AUTH-2 ─┐
                     ├──► T-AUTH-3 ──► T-AUTH-4 ──► T-AUTH-7 (retrofit, last — needs every other module's routes to exist)
                     │
                     └──► T-AUTH-5, T-AUTH-6 ──► T-AUTH-8 ──► T-AUTH-9 ──► T-AUTH-10 ──► T-AUTH-11
```

T-AUTH-7 is intentionally sequenced **last** among the backend tasks — it touches every other module's route definitions, so it should run once those modules' routers are stable, to avoid repeated rework as new endpoints are added elsewhere.

---

## Acceptance Criteria

- [ ] AC-1: Seed users (once Users module provides them) can log in and receive a JWT with the correct `role` claim (FR-AUTH-001).
- [ ] AC-2: A request to any protected endpoint without an `Authorization` header returns 401 (FR-AUTH-003).
- [ ] AC-3: A request with an expired token returns 401, and the frontend clears state and redirects to `/login` (FR-AUTH-002, FR-AUTH-004).
- [ ] AC-4: A deactivated user's login attempt with correct credentials returns 401 with code `ACCOUNT_INACTIVE` (FR-AUTH-006).
- [ ] AC-5: `GET /auth/me` returns the correct role name and a non-empty, correctly-scoped `permissions` array for each of the 3 seed users (FR-AUTH-008).
- [ ] AC-6: Browser devtools inspection confirms the access token is never present in `localStorage`, `sessionStorage`, or cookies (SC-AUTH-002).
- [ ] AC-7: Logout clears the token immediately and subsequent protected requests from that browser session return 401 (FR-AUTH-007).

## Dependencies and Prerequisites Recap

- **Hard blocker**: [Users](../users/tasks.md) T-USR-1 (schema) and T-USR-3 (credential-check service function) must complete before T-AUTH-5.
- **Hard blocker**: [Roles](../roles/tasks.md) and [Permissions](../permissions/tasks.md) seed migrations must complete before T-AUTH-3/T-AUTH-6 can return meaningful permission data.
- **Soft blocker**: T-AUTH-7 (retrofit) is most efficient once Accounts/Contacts/Leads/Opportunities/Activities routers exist, to avoid touching the same files twice.
