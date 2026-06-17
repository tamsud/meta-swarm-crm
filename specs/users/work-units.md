# Module Work Units: Users

**Module**: `users` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Tasks**: [tasks.md](tasks.md)

---

## Dependency Graph

### Upstream
- **Project Setup** WU-SETUP-9
- **Roles** WU-ROLE-1 (FK target for `users.role_id`)
- **Authentication** WU-AUTH-2 (`hash_password` / `verify_password` — Users delegates rather than duplicating bcrypt)

### Downstream
- **Authentication** WU-AUTH-3, WU-AUTH-4 (`get_current_user` loads User; login needs Users service)
- **Leads** WU-LEAD-1 (FK target for `leads.created_by_user_id`)
- **Activities** WU-ACT-1 (FK target for `activities.created_by_user_id`)

### Internal sequence
```
WU-USR-1 ──► WU-USR-2 ──► WU-USR-3 ──► WU-USR-4 ──┬──► WU-USR-5 ──► WU-USR-8
                                                    ├──► WU-USR-6
                                                    └──► WU-USR-7
```

---

## Work Units

### WU-USR-1: Schema Migration
**Tasks**: T-USR-1
**Depends on**: Roles WU-ROLE-1 (FK target)

**File scope**:
- `backend/alembic/versions/0007_create_users.py` (new)

**Definition of Done**:
- [x] `users` table: `(id, email UNIQUE, hashed_password, display_name, role_id FK, is_active, created_at, updated_at)`
- [x] Case-insensitive uniqueness on email (functional index on `lower(email)` or check constraint)
- [x] FK `role_id` references `roles(id)` with `ON DELETE RESTRICT`
- [x] Downgrade reverses cleanly

**Success Criteria covered**: SC-USR-002

---

### WU-USR-2: ORM + Schemas
**Tasks**: T-USR-2, T-USR-3
**Depends on**: WU-USR-1

**File scope**:
- `backend/app/models/user.py` (new)
- `backend/app/schemas/user.py` (new — `UserCreate`, `UserUpdate`, `UserSelfUpdate`, `UserResponse`)

**Definition of Done**:
- [x] `UserResponse` never serialises `hashed_password` (verified by schema field inspection in a test)
- [x] `UserSelfUpdate` whitelists only `display_name` (extra fields rejected with 422 via Pydantic `extra="forbid"`)
- [x] `UserCreate` requires `email`, `password`, `role_id`; accepts optional `display_name`
- [x] `UserUpdate` accepts only `role_id`, `is_active`, `display_name` (all optional, extra fields rejected with 422 via Pydantic `extra="forbid"`)

**Success Criteria covered**: SC-USR-002

---

### WU-USR-3: Service Layer
**Tasks**: T-USR-4
**Depends on**: WU-USR-2, Authentication WU-AUTH-2 (`hash_password`)

**File scope**:
- `backend/app/services/user_service.py` (new — `create`, `get`, `list (search/filter/sort)`, `update`, `update_self`, `verify_credentials`)

**Definition of Done**:
- [x] `create_user` raises `EMAIL_CONFLICT` (409) on duplicate email (case-insensitive)
- [x] `create_user` validates `role_id` exists, else 422
- [x] `update_user` validates `role_id` exists (if provided), else 422
- [x] `update_user` raises `LAST_ADMIN_LOCKOUT` (400) if the patch would leave zero active Admins (deactivate the last Admin, or move the last Admin to a non-Admin role)
- [x] `verify_credentials` returns the user only if active + password matches; rejects inactive users with a distinct code
- [x] All password storage goes through `hash_password` — no direct bcrypt calls in this file

**Success Criteria covered**: SC-USR-001, SC-USR-002

---

### WU-USR-4: Router
**Tasks**: T-USR-5
**Depends on**: WU-USR-3, Authentication WU-AUTH-3 (`require_permission`); may stub no-op gates if WU-AUTH-4 is not yet ready

**File scope**:
- `backend/app/routers/users.py` (new — `GET /users`, `POST /users`, `GET /users/{id}`, `PATCH /users/{id}`, `GET /users/me`, `PATCH /users/me` — NO `DELETE` per users/plan.md "Soft deactivation only, no hard delete")
- `backend/app/main.py` (modify — register router)

**Definition of Done**:
- [x] All admin endpoints gated by `require_permission("users:manage")`
- [x] `PATCH /users/me` accepts only `display_name` (extra fields → 422)
- [x] Non-Admin calling `GET /users` returns 403
- [x] Last-admin guard surfaces from service correctly (400 with code)

**Success Criteria covered**: SC-USR-001, SC-USR-002

---

### WU-USR-5: Seed Users Script
**Tasks**: T-USR-6
**Depends on**: WU-USR-3

**File scope**:
- `backend/alembic/versions/0008_seed_demo_users.py` (new — idempotent: skip if email exists) **or** `backend/app/scripts/seed_users.py`

**Definition of Done**:
- [x] 3 demo users seeded (one per system role): Admin / Manager / Sales Rep
- [x] Re-running the script does NOT create duplicates
- [x] Passwords match the documented dev credentials (in `.env.example` or README)

**Success Criteria covered**: SC-USR-003

---

### WU-USR-6: Frontend Admin Page
**Tasks**: T-USR-7
**Depends on**: WU-USR-4, Roles WU-ROLE-4 (`GET /roles` for the role dropdown)

**File scope**:
- `frontend/src/features/users/UsersListPage.tsx` (new)
- `frontend/src/features/users/UserForm.tsx` (new — create/edit modal with role dropdown)
- `frontend/src/features/users/api.ts` (new)
- `frontend/src/routes/index.tsx` (modify — register `/admin/users`)

**Definition of Done**:
- [x] List page paginates + filters by role + search
- [x] Form's role dropdown populated from `GET /roles`
- [x] Deactivate button shows confirmation; surface `LAST_ADMIN_LOCKOUT` error inline

**Success Criteria covered**: SC-USR-001, SC-USR-002

---

### WU-USR-7: Frontend Profile Page
**Tasks**: T-USR-8
**Depends on**: WU-USR-4

**File scope**:
- `frontend/src/features/users/ProfilePage.tsx` (new — `/profile`, display_name only)
- `frontend/src/routes/index.tsx` (modify — register `/profile`)

**Definition of Done**:
- [x] `display_name` editable; `email`, `role`, `is_active` shown read-only
- [x] Save calls `PATCH /users/me` and refreshes AuthContext display name

**Success Criteria covered**: SC-USR-002

---

### WU-USR-8: Integration Tests
**Tasks**: T-USR-9
**Depends on**: WU-USR-4, WU-USR-5, Authentication WU-AUTH-4 (login endpoint for AC-7)

**File scope**:
- `backend/tests/test_users_integration.py` (new)

**Definition of Done**:
- [x] Test: duplicate email → 409 `EMAIL_CONFLICT`
- [x] Test: last-admin deactivation → 400 `LAST_ADMIN_LOCKOUT`
- [x] Test: last-admin role change → 400 `LAST_ADMIN_LOCKOUT`
- [x] Test: deactivated user's login attempt → 401 `ACCOUNT_INACTIVE`
- [x] Test: deactivated user calling protected endpoint (e.g., `GET /users/me`) → 401 `ACCOUNT_INACTIVE`
- [x] Test: all 3 seed users can log in — admin@crm.local → Admin role, manager@crm.local → Manager role, sales@crm.local → Sales Rep role

**Success Criteria covered**: SC-USR-001, SC-USR-002, SC-USR-003
