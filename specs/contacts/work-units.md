# Module Work Units: Contacts

**Module**: `contacts` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Tasks**: [tasks.md](tasks.md)

---

## Dependency Graph

### Upstream
- **Project Setup** WU-SETUP-9
- **Accounts** WU-ACCT-1 (FK target — `contacts.account_id` is nullable but still needs the FK row to exist)

### Downstream
- **Opportunities** WU-OPP-1 (FK target: `opportunities.contact_id`)
- **Activities** WU-ACT-1 (FK target: `activities.contact_id`)
- **Leads** WU-LEAD-5 (conversion needs `find_by_email`)

### Internal sequence
```
WU-CONT-1 ──► WU-CONT-2 ──► WU-CONT-3 ──┬──► WU-CONT-4
                                          ├──► WU-CONT-5
                                          └──► WU-CONT-6
```

---

## Work Units

### WU-CONT-1: Schema Migration
**Tasks**: T-CONT-1
**Depends on**: Accounts WU-ACCT-1

**File scope**:
- `backend/alembic/versions/0009_create_contacts.py` (new)

**Definition of Done**:
- [ ] `contacts` table: `(id, first_name, last_name, email UNIQUE, phone, job_title, account_id FK nullable, created_at, updated_at)`
- [ ] FK to `accounts(id)` with `ON DELETE RESTRICT` (Accounts dependency-guard enforces this)
- [ ] Case-insensitive uniqueness on email (functional index on `lower(email)`)
- [ ] Downgrade reverses cleanly

**Success Criteria covered**: SC-CONT-001

---

### WU-CONT-2: ORM + Schemas + Service
**Tasks**: T-CONT-2, T-CONT-3, T-CONT-4
**Depends on**: WU-CONT-1, Accounts WU-ACCT-2 (read function for account validation)

**File scope**:
- `backend/app/models/contact.py` (new)
- `backend/app/schemas/contact.py` (new — `ContactCreate { first_name, last_name, email, phone?, job_title?, account_id? }`, `ContactUpdate`, `ContactResponse`)
- `backend/app/services/contact_service.py` (new — `create`, `get`, `list (search/sort/paginate, filter by account_id)`, `update`, `delete`, `find_by_email`)

**Definition of Done**:
- [ ] Duplicate email on create/update → `EMAIL_CONFLICT` (409) — case-insensitive
- [ ] `account_id`, if provided, validated to exist → 422 otherwise
- [ ] `list_contacts(search=...)` matches partial first/last/email, case-insensitive
- [ ] `find_by_email(email)` returns the contact or None — used by Leads conversion

**Success Criteria covered**: SC-CONT-001, SC-CONT-002

---

### WU-CONT-3: Router
**Tasks**: T-CONT-5
**Depends on**: WU-CONT-2, Authentication WU-AUTH-3

**File scope**:
- `backend/app/routers/contacts.py` (new — GET list, GET one, POST, PATCH, DELETE)
- `backend/app/main.py` (modify — register router)

**Definition of Done**:
- [ ] Each endpoint gated by `require_permission("contacts:{action}")` matching catalogue
- [ ] Query params (`search`, `account_id`, sort, page) validated at boundary

**Success Criteria covered**: SC-CONT-002

---

### WU-CONT-4: Frontend List Page
**Tasks**: T-CONT-6
**Depends on**: WU-CONT-3, Accounts WU-ACCT-3 (`GET /accounts` for filter dropdown)

**File scope**:
- `frontend/src/features/contacts/ContactsListPage.tsx` (new)
- `frontend/src/features/contacts/ContactForm.tsx` (new — create/edit modal)
- `frontend/src/features/contacts/api.ts` (new)
- `frontend/src/routes/index.tsx` (modify — register `/contacts`)

**Definition of Done**:
- [ ] List filters by account (dropdown sourced from `GET /accounts`)
- [ ] Search input drives `?search=` query param
- [ ] 409 `EMAIL_CONFLICT` surfaces inline on the email field

**Success Criteria covered**: SC-CONT-002

---

### WU-CONT-5: Frontend Detail Page
**Tasks**: T-CONT-7
**Depends on**: WU-CONT-3, Accounts WU-ACCT-3 (account name resolution)

**File scope**:
- `frontend/src/features/contacts/ContactDetailPage.tsx` (new — header + ProfileSidebar + TabStrip)
- `frontend/src/features/contacts/ContactHistoryTab.tsx` (new — renders empty until Activities ships)
- `frontend/src/features/contacts/ContactEmailsTab.tsx` (new — renders empty until Activities ships)
- `frontend/src/routes/index.tsx` (modify — register `/contacts/:id`)

**Definition of Done**:
- [ ] Header renders `"{first_name} {last_name}, {account.name}"` when account linked
- [ ] Header renders name-only gracefully when no account
- [ ] History / Emails tabs render empty states until Activities WU-ACT-6 wires them in

**Success Criteria covered**: SC-CONT-002

---

### WU-CONT-6: Integration Tests
**Tasks**: T-CONT-8
**Depends on**: WU-CONT-3

**File scope**:
- `backend/tests/test_contacts_integration.py` (new)

**Definition of Done**:
- [ ] CRUD round-trip test passes (with and without `account_id`)
- [ ] Duplicate email on create → 409
- [ ] Duplicate email on update → 409
- [ ] `GET /contacts?account_id=X` returns only matching rows
- [ ] `GET /contacts?search=` matches partial name + email, case-insensitive

**Success Criteria covered**: SC-CONT-001, SC-CONT-002
