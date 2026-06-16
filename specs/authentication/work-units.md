# Module Work Units: Authentication

**Module**: `authentication` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Tasks**: [tasks.md](tasks.md)

---

## Dependency Graph

### Upstream
- **Project Setup** WU-SETUP-9 (`core/security/` package scaffolded)
- **Users** WU-USR-1, WU-USR-3 (schema + `verify_credentials` service)
- **Roles** WU-ROLE-1, **Permissions** WU-PERM-1 (seed data for permission resolution)

### Downstream
- Every other module's router (each one consumes `require_permission` and `get_current_user`)
- WU-AUTH-5 (retrofit) touches every existing router file in the system

### Internal sequence
```
WU-AUTH-1 ─┐
WU-AUTH-2 ─┴─► WU-AUTH-3 ──► WU-AUTH-4 ──► WU-AUTH-5 (retrofit, runs last)
                  │
                  └─► WU-AUTH-6 ──► WU-AUTH-7 ──► WU-AUTH-8 ──► WU-AUTH-9
```

---

## Work Units

### WU-AUTH-1: JWT Utility
**Tasks**: T-AUTH-1
**Depends on**: Project Setup WU-SETUP-9 only — pure utility
**Parallelizable with**: WU-AUTH-2, Permissions WU-PERM-1, Accounts WU-ACCT-1

**File scope**:
- `backend/app/core/security/jwt.py` (new — `create_access_token`, `decode_access_token`)
- `backend/tests/test_jwt.py` (new)

**Definition of Done**:
- [ ] HS256 with `JWT_SECRET_KEY` from `Settings`
- [ ] Configurable expiry (default per spec) via env var
- [ ] `decode_access_token` raises distinct error for expired vs malformed vs signature-invalid
- [ ] Standalone unit tests pass with no DB dependency

**Success Criteria covered**: SC-AUTH-003

---

### WU-AUTH-2: Password Utility
**Tasks**: T-AUTH-2
**Depends on**: Project Setup WU-SETUP-9 only
**Parallelizable with**: WU-AUTH-1

**File scope**:
- `backend/app/core/security/passwords.py` (new — `hash_password`, `verify_password`)
- `backend/tests/test_passwords.py` (new)

**Definition of Done**:
- [ ] bcrypt cost ≥ 12 (asserted in a test by inspecting the hash's cost field)
- [ ] `verify_password` is constant-time (bcrypt's default)
- [ ] Unit tests cover correct / incorrect / malformed-hash cases

**Success Criteria covered**: SC-AUTH-001

---

### WU-AUTH-3: Current-User Dependency
**Tasks**: T-AUTH-3, T-AUTH-4
**Depends on**: WU-AUTH-1, Users WU-USR-1, Roles WU-ROLE-1, Permissions WU-PERM-1

**File scope**:
- `backend/app/core/security/dependencies.py` (new — `get_current_user`, `require_permission(code)`)

**Definition of Done**:
- [ ] `get_current_user` decodes the token → loads User → loads Role → resolves effective Permissions in a single query (no N+1)
- [ ] Returns 401 on missing/invalid/expired token
- [ ] Returns 401 `ACCOUNT_INACTIVE` if the user row has `is_active=false`
- [ ] `require_permission("code")` returns a dependency factory; raises 403 when the resolved permission set doesn't include the code

**Success Criteria covered**: SC-AUTH-003

---

### WU-AUTH-4: Auth Router (login + me)
**Tasks**: T-AUTH-5, T-AUTH-6
**Depends on**: WU-AUTH-1, WU-AUTH-2, WU-AUTH-3, Users WU-USR-3

**File scope**:
- `backend/app/routers/auth.py` (new — `POST /auth/login`, `GET /auth/me`)
- `backend/app/main.py` (modify — register router)

**Definition of Done**:
- [ ] `POST /auth/login` returns JWT on success, 401 (`INVALID_CREDENTIALS`) on bad password, 401 (`ACCOUNT_INACTIVE`) when deactivated
- [ ] JWT claim `role` matches the user's role name
- [ ] `GET /auth/me` returns `{user, role, permissions: [codes]}` non-empty for seed users
- [ ] Token NEVER appears in the response cookie (response carries it in JSON body only)

**Success Criteria covered**: SC-AUTH-001, SC-AUTH-003

---

### WU-AUTH-5: Retrofit Permission Gates
**Tasks**: T-AUTH-7
**Depends on**: WU-AUTH-3, AND every other module's routers existing (Accounts, Roles, Users, Permissions, Contacts, Opportunities, Leads, Activities). Run **after** those modules' routers stabilise to avoid touching the same files twice.

**File scope** (modify only):
- `backend/app/routers/accounts.py`
- `backend/app/routers/contacts.py`
- `backend/app/routers/opportunities.py`
- `backend/app/routers/leads.py`
- `backend/app/routers/activities.py`
- `backend/app/routers/users.py`
- `backend/app/routers/roles.py`
- `backend/app/routers/permissions.py`

**Definition of Done**:
- [ ] Every protected endpoint has `Depends(get_current_user)` and (where applicable) `Depends(require_permission("..."))`
- [ ] Permissions module catalogue-consistency test (WU-PERM-5) passes
- [ ] Existing integration tests still pass after the retrofit (no regressions)

**Success Criteria covered**: SC-AUTH-003

---

### WU-AUTH-6: Frontend AuthContext
**Tasks**: T-AUTH-8
**Depends on**: WU-AUTH-4

**File scope**:
- `frontend/src/context/AuthContext.tsx` (new — in-memory token + user + permissions state)
- `frontend/src/context/useAuth.ts` (new — `useAuth`, `usePermission`)

**Definition of Done**:
- [ ] Token stored only in React state (NEVER `localStorage`, `sessionStorage`, or cookies — verified by grep + manual devtools inspection)
- [ ] `login(email, password)` calls `POST /auth/login`, then `GET /auth/me`, then populates context
- [ ] `logout()` clears state immediately
- [ ] `hasPermission(code)` returns true iff `code` in current user's permission set

**Success Criteria covered**: SC-AUTH-002

---

### WU-AUTH-7: Frontend Axios Interceptors
**Tasks**: T-AUTH-9
**Depends on**: WU-AUTH-6, Project Setup WU-SETUP-6 (`lib/api.ts`)

**File scope**:
- `frontend/src/lib/api.ts` (modify — request + response interceptors)

**Definition of Done**:
- [ ] Request interceptor attaches `Authorization: Bearer <token>` when AuthContext has one
- [ ] Response interceptor catches 401 → clears AuthContext → redirects to `/login`
- [ ] Interceptors do NOT redirect on `/auth/login`'s own 401 (login form must show inline error)

**Success Criteria covered**: SC-AUTH-003

---

### WU-AUTH-8: Login Page + Route Guards
**Tasks**: T-AUTH-10
**Depends on**: WU-AUTH-6, WU-AUTH-7

**File scope**:
- `frontend/src/pages/LoginPage.tsx` (new — two-panel responsive)
- `frontend/src/routes/RequireAuth.tsx` (new)
- `frontend/src/routes/RequirePermission.tsx` (new)
- `frontend/src/routes/index.tsx` (modify — register `/login`, wrap protected routes)

**Definition of Done**:
- [ ] `/login` renders without auth; redirects to dashboard after successful login
- [ ] `RequireAuth` redirects to `/login` when no token
- [ ] `RequirePermission(code)` renders a 403 page (not blank) when authenticated but missing permission
- [ ] Login page matches mock under `mocks/login.html`

**Success Criteria covered**: SC-AUTH-001

---

### WU-AUTH-9: Integration Tests
**Tasks**: T-AUTH-11
**Depends on**: WU-AUTH-4 through WU-AUTH-8

**File scope**:
- `backend/tests/test_auth_integration.py` (new)
- `frontend/src/__tests__/auth.spec.tsx` (new — basic flow)

**Definition of Done**:
- [ ] Backend: login → protected call → logout → protected call returns 401
- [ ] Backend: expired token returns 401
- [ ] Backend: deactivated user login returns 401 `ACCOUNT_INACTIVE`
- [ ] Frontend: devtools inspection (or equivalent test) confirms token NOT in localStorage/sessionStorage/cookies
- [ ] Frontend: 401 response triggers redirect to `/login`

**Success Criteria covered**: SC-AUTH-001, SC-AUTH-002, SC-AUTH-003
