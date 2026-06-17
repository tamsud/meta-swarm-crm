# Module Work Units: Permissions

**Module**: `permissions` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Tasks**: [tasks.md](tasks.md)

---

## Dependency Graph

### Upstream
- **Project Setup** WU-SETUP-9 (backend scaffold + Alembic baseline)

### Downstream
- **Roles** WU-ROLE-1 (FK target: `role_permissions.permission_id`)
- **Authentication** WU-AUTH-3 (`get_current_user` joins through `role_permissions`)
- Every router across every module (each `require_permission("...")` literal must exist in the seeded catalogue — enforced by WU-PERM-5)

### Internal sequence
```
WU-PERM-1 ──► WU-PERM-2 ──► WU-PERM-3 ──► WU-PERM-4
                                              │
WU-PERM-5 (runs last, after every other module's routers exist)
```

---

## Work Units

### WU-PERM-1: Schema + Seed Migrations
**Tasks**: T-PERM-1, T-PERM-2
**Depends on**: Project Setup WU-SETUP-9
**Parallelizable with**: Accounts WU-ACCT-1, Auth utilities (WU-AUTH-1, WU-AUTH-2)

**File scope**:
- `backend/alembic/versions/0002_create_permissions.py` (new)
- `backend/alembic/versions/0003_seed_permissions.py` (new — one row per `{module}:{action}` across all 9 modules)

**Definition of Done**:
- [x] `alembic upgrade head` creates the `permissions` table with `(code, module, action, description)` columns and a UNIQUE constraint on `code`
- [x] Seed migration inserts every `{module}:{action}` code referenced anywhere in this project's specs
- [x] No duplicate `code` values after seed (DB UNIQUE blocks them)
- [x] `alembic downgrade base` reverses both migrations cleanly

**Success Criteria covered**: SC-PERM-002

---

### WU-PERM-2: Backend ORM + Schemas + Service
**Tasks**: T-PERM-3, T-PERM-4, T-PERM-5
**Depends on**: WU-PERM-1

**File scope**:
- `backend/app/models/permission.py` (new)
- `backend/app/schemas/permission.py` (new — `PermissionResponse` only; no Create/Update/Delete schemas)
- `backend/app/services/permission_service.py` (new — `list_permissions(module: str | None)`)

**Definition of Done**:
- [x] `Permission` ORM model maps cleanly to the migrated table
- [x] Only `PermissionResponse` exists — schema-level proof the catalogue is read-only
- [x] `list_permissions(module="leads")` returns only Leads-module rows; `list_permissions(None)` returns all
- [x] Unit tests cover both filtered and unfiltered paths

**Success Criteria covered**: SC-PERM-001

---

### WU-PERM-3: Read-Only Router
**Tasks**: T-PERM-6
**Depends on**: WU-PERM-2

**File scope**:
- `backend/app/routers/permissions.py` (new — `GET /permissions` with optional `module` query param)
- `backend/app/main.py` (modify — register router)

**Definition of Done**:
- [x] `GET /permissions` returns non-empty catalogue
- [x] `GET /permissions?module=leads` filters correctly
- [x] Route-table inspection (e.g., `app.routes`) shows zero `POST`/`PATCH`/`DELETE` handlers for `/permissions`
- [x] Test asserts the route-table inspection programmatically (not a runtime 404 check)

**Success Criteria covered**: SC-PERM-001, SC-PERM-002

---

### WU-PERM-4: Frontend Admin Page
**Tasks**: T-PERM-7
**Depends on**: WU-PERM-3, Authentication WU-AUTH-8 (AuthContext for `hasPermission`)

**File scope**:
- `frontend/src/features/permissions/PermissionsPage.tsx` (new — read-only table grouped by `module`)
- `frontend/src/features/permissions/api.ts` (new — React Query hook for `GET /permissions`)
- `frontend/src/routes/index.tsx` (modify — register `/admin/permissions`)

**Definition of Done**:
- [x] `/admin/permissions` renders one row per permission, grouped by module
- [x] No "Create / Edit / Delete" UI controls present anywhere
- [x] Route is guarded by `RequirePermission("roles:manage")` (catalogue is admin-visible)

**Success Criteria covered**: SC-PERM-001

---

### WU-PERM-5: Catalogue Consistency Test
**Tasks**: T-PERM-8
**Depends on**: All other modules' routers exist (Accounts, Roles, Users, Auth, Contacts, Opportunities, Leads, Activities, Deployment)

**File scope**:
- `backend/tests/test_permission_catalogue_consistency.py` (new)

**Definition of Done**:
- [ ] Test parses every `require_permission("...")` literal in `backend/app/routers/**/*.py`
- [ ] Asserts every extracted code exists in `seed_permissions.py`'s insert list
- [ ] Test fails loudly with the offending code + file:line if mismatch found
- [ ] Test is wired into the default `pytest` run (not opt-in)

**Success Criteria covered**: SC-PERM-001, SC-PERM-002
