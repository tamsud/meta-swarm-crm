# Module Work Units: Accounts

**Module**: `accounts` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Tasks**: [tasks.md](tasks.md)

---

## Dependency Graph

### Upstream
- **Project Setup** WU-SETUP-9
- **Permissions** WU-PERM-1 (catalogue must include `accounts:*` codes before WU-ACCT-3 is gated; can be stubbed in parallel)

### Downstream
- **Contacts** WU-CONT-1 (FK target: `contacts.account_id`)
- **Opportunities** WU-OPP-1 (FK target: `opportunities.account_id`)
- **Leads** WU-LEAD-5 (conversion needs `find_or_create_by_name`)

### Internal sequence
```
WU-ACCT-1 ──► WU-ACCT-2 ──► WU-ACCT-3 ──┬──► WU-ACCT-4
                                          ├──► WU-ACCT-5
                                          └──► WU-ACCT-6 (after Contacts or Opportunities exists)
```

---

## Work Units

### WU-ACCT-1: Schema Migration
**Tasks**: T-ACCT-1
**Depends on**: Project Setup WU-SETUP-9
**Parallelizable with**: Permissions WU-PERM-1, Auth utilities (WU-AUTH-1, WU-AUTH-2)

**File scope**:
- `backend/alembic/versions/0006_create_accounts.py` (new)

**Definition of Done**:
- [ ] `accounts` table created with `(id, name, industry, website, phone, address, created_at, updated_at)`
- [ ] Functional index on `lower(name)` for case-insensitive search
- [ ] Downgrade reverses cleanly

**Success Criteria covered**: SC-ACCT-002

---

### WU-ACCT-2: ORM + Schemas + Service
**Tasks**: T-ACCT-2, T-ACCT-3, T-ACCT-4
**Depends on**: WU-ACCT-1

**File scope**:
- `backend/app/models/account.py` (new)
- `backend/app/schemas/account.py` (new — `AccountCreate { name, industry?, website?, phone?, address? }`, `AccountUpdate` (all optional), `AccountResponse`)
- `backend/app/services/account_service.py` (new — `create`, `get`, `list (search/sort/paginate)`, `update`, `delete (with dependency guard)`, `find_or_create_by_name`)

**Definition of Done**:
- [ ] `list_accounts` uses the `lower(name)` index for `search` filter (verified via `EXPLAIN`)
- [ ] `delete_account` counts dependent contacts + opportunities and raises `ACCOUNT_HAS_DEPENDENTS` (409) with both counts in the error payload
- [ ] `find_or_create_by_name(name)` is case-insensitive and atomic (Leads conversion contract)
- [ ] Pagination defaults to `Settings.DEFAULT_PAGE_SIZE`

**Success Criteria covered**: SC-ACCT-001, SC-ACCT-002

---

### WU-ACCT-3: Router
**Tasks**: T-ACCT-5
**Depends on**: WU-ACCT-2, Authentication WU-AUTH-3 (`require_permission` available)

**File scope**:
- `backend/app/routers/accounts.py` (new — GET list, GET one, POST, PATCH, DELETE)
- `backend/app/main.py` (modify — register router)

**Definition of Done**:
- [ ] Each endpoint gated by `require_permission("accounts:{action}")` matching the seeded catalogue
- [ ] `DELETE` returns 403 for users without `accounts:delete` regardless of frontend state
- [ ] Search/sort/paginate query params validated by Pydantic at the boundary

**Success Criteria covered**: SC-ACCT-003

---

### WU-ACCT-4: Frontend List + Form
**Tasks**: T-ACCT-6
**Depends on**: WU-ACCT-3, Authentication WU-AUTH-8 (AuthContext for `hasPermission`)

**File scope**:
- `frontend/src/features/accounts/AccountsListPage.tsx` (new)
- `frontend/src/features/accounts/AccountForm.tsx` (new — create/edit modal)
- `frontend/src/features/accounts/api.ts` (new)
- `frontend/src/routes/index.tsx` (modify — register `/accounts`)

**Definition of Done**:
- [ ] List page paginates and search-filters via URL params (sorting deferred — backend doesn't support it yet)
- [ ] Delete button visible only when `hasPermission("accounts:delete")`
- [ ] 409 `ACCOUNT_HAS_DEPENDENTS` surfaces both counts in a toast/dialog
- [ ] Loading + empty states match the mock under `mocks/accounts.html`

**Success Criteria covered**: SC-ACCT-002, SC-ACCT-003

---

### WU-ACCT-5: Frontend Detail Page
**Tasks**: T-ACCT-7
**Depends on**: WU-ACCT-3

**File scope**:
- `frontend/src/features/accounts/AccountDetailPage.tsx` (new)
- `frontend/src/features/accounts/AccountContactsTab.tsx` (new — renders empty until Contacts ships)
- `frontend/src/features/accounts/AccountOpportunitiesTab.tsx` (new — renders empty until Opportunities ships)
- `frontend/src/routes/index.tsx` (modify — register `/accounts/:id`)

**Definition of Done**:
- [ ] Detail page renders account fields + tab strip
- [ ] Tabs render gracefully when their feature module is not yet wired in
- [ ] After Contacts/Opportunities ship, tabs render lists with no further refactor

**Success Criteria covered**: SC-ACCT-003

---

### WU-ACCT-6: Integration Tests
**Tasks**: T-ACCT-8
**Depends on**: WU-ACCT-3, Contacts WU-CONT-1 **or** Opportunities WU-OPP-1 (need a real dependent for delete-blocked test)

**File scope**:
- `backend/tests/test_accounts_integration.py` (new)

**Definition of Done**:
- [ ] CRUD round trip test passes (create → list → patch → get → delete)
- [ ] `GET /accounts?search=acme` returns only matches (case-insensitive)
- [ ] Delete-blocked-by-dependents: create account → create contact → DELETE → 409 with both counts
- [ ] Sales Rep DELETE returns 403

**Success Criteria covered**: SC-ACCT-001, SC-ACCT-002, SC-ACCT-003
