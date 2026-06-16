# Module Work Units: Roles

**Module**: `roles` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Tasks**: [tasks.md](tasks.md)

---

## Dependency Graph

### Upstream
- **Project Setup** WU-SETUP-9
- **Permissions** WU-PERM-1 (catalogue schema + seed — FK target for `role_permissions.permission_id`)

### Downstream
- **Users** WU-USR-1 (FK target for `users.role_id`)
- **Authentication** WU-AUTH-3 (role+permission resolution for `get_current_user`)

### Internal sequence
```
WU-ROLE-1 ──► WU-ROLE-2 ──► WU-ROLE-3 ──► WU-ROLE-4 ──┬──► WU-ROLE-5
                                                        └──► WU-ROLE-6
```

---

## Work Units

### WU-ROLE-1: Schema + Seed Migrations
**Tasks**: T-ROLE-1, T-ROLE-2
**Depends on**: Permissions WU-PERM-1 (catalogue must be seeded so the role-permission FK rows are valid)

**File scope**:
- `backend/alembic/versions/0004_create_roles.py` (new — `roles` table + `role_permissions` junction)
- `backend/alembic/versions/0005_seed_system_roles.py` (new — Admin, Manager, Sales Rep with their permission mappings)

**Definition of Done**:
- [ ] `roles` table has `(id, name UNIQUE, description, is_system BOOL)`
- [ ] `role_permissions` has `(role_id FK, permission_id FK)` with composite PK
- [ ] Seed inserts exactly 3 rows with `is_system=true`
- [ ] Admin's permission map = full catalogue; Manager / Sales Rep maps match spec
- [ ] Downgrade reverses cleanly

**Success Criteria covered**: SC-ROLE-001

---

### WU-ROLE-2: Backend ORM + Schemas
**Tasks**: T-ROLE-3, T-ROLE-4
**Depends on**: WU-ROLE-1

**File scope**:
- `backend/app/models/role.py` (new — `Role`, `RolePermission`)
- `backend/app/schemas/role.py` (new — `RoleCreate`, `RoleUpdate`, `RoleResponse` with nested `permissions: list[PermissionResponse]`)

**Definition of Done**:
- [ ] `Role.permissions` relationship returns the joined permission rows
- [ ] `RoleCreate` requires `name` + `permission_ids: list[int]`
- [ ] `RoleResponse` serialises `is_system`, `permission_count`, `user_count`

**Success Criteria covered**: SC-ROLE-001, SC-ROLE-002

---

### WU-ROLE-3: Service Layer + Guards
**Tasks**: T-ROLE-5
**Depends on**: WU-ROLE-2

**File scope**:
- `backend/app/services/role_service.py` (new — `create_role`, `update_role`, `delete_role`, `list_roles`)

**Definition of Done**:
- [ ] `update_role` raises `SYSTEM_ROLE_IMMUTABLE` (400) when the target row has `is_system=true`
- [ ] `delete_role` raises `SYSTEM_ROLE_IMMUTABLE` (400) on system roles
- [ ] `delete_role` raises `ROLE_HAS_USERS` (409) with the user count when ≥1 user references the role
- [ ] `list_roles` computes accurate `permission_count` and `user_count` in a single query (no N+1)

**Success Criteria covered**: SC-ROLE-002

---

### WU-ROLE-4: Router
**Tasks**: T-ROLE-6
**Depends on**: WU-ROLE-3, Authentication WU-AUTH-3 (`require_permission` dependency)

**File scope**:
- `backend/app/routers/roles.py` (new — GET list, GET one, POST, PATCH, DELETE)
- `backend/app/main.py` (modify — register router)

**Definition of Done**:
- [ ] All 5 endpoints gated by `Depends(require_permission("roles:manage"))`
- [ ] Error codes map to HTTP correctly (400 / 409 as above)
- [ ] OpenAPI docs render with the nested `RoleResponse` schema

**Success Criteria covered**: SC-ROLE-001, SC-ROLE-002

---

### WU-ROLE-5: Frontend Admin Page
**Tasks**: T-ROLE-7
**Depends on**: WU-ROLE-4, Permissions WU-PERM-3 (need `GET /permissions` for the permission picker)

**File scope**:
- `frontend/src/features/roles/RolesPage.tsx` (new — list with permission_count / user_count)
- `frontend/src/features/roles/RoleForm.tsx` (new — modal for create/edit)
- `frontend/src/features/roles/RolePermissionEditor.tsx` (new — grouped checkbox picker)
- `frontend/src/features/roles/api.ts` (new — React Query hooks)
- `frontend/src/routes/index.tsx` (modify — register `/admin/roles`)

**Definition of Done**:
- [ ] System roles show a lock icon + disabled edit/delete controls
- [ ] Custom role create → list updates → assign to user (round-trip)
- [ ] Permission editor groups checkboxes by `module`
- [ ] Delete confirmation shows the conflict count when 409 is returned

**Success Criteria covered**: SC-ROLE-002

---

### WU-ROLE-6: Integration Tests
**Tasks**: T-ROLE-8
**Depends on**: WU-ROLE-4

**File scope**:
- `backend/tests/test_roles_integration.py` (new)

**Definition of Done**:
- [ ] Test: PATCH on Admin role name returns 400 `SYSTEM_ROLE_IMMUTABLE`
- [ ] Test: DELETE on Admin role returns 400 `SYSTEM_ROLE_IMMUTABLE`
- [ ] Test: DELETE on role with assigned user returns 409 `ROLE_HAS_USERS` with `user_count` in body
- [ ] Test: Custom role CRUD round trip — create → assign user → exercise the user's permissions → matches exactly the selected subset

**Success Criteria covered**: SC-ROLE-001, SC-ROLE-002
