# Implementation Plan: Contacts Module

**Module**: `contacts`  
**Work Unit Count**: 6 (WU-CONT-1 through WU-CONT-6)  
**Status**: approved
**Estimated Total Time**: 8-12 hours

---

## Upstream Dependencies (Must be Complete)

| Module | Work Unit | Status | Provides |
|--------|-----------|--------|----------|
| Project Setup | WU-SETUP-9 | Required | Backend scaffold, database config |
| Accounts | WU-ACCT-1 | Required | `accounts` table (FK target for `account_id`) |
| Accounts | WU-ACCT-2 | Required | `account_service.get_account()` for validation |
| Accounts | WU-ACCT-3 | Required | `GET /accounts` endpoint (for filter dropdown) |
| Authentication | WU-AUTH-3 | Required | `require_permission()` decorator |

---

## Work Unit Details

### WU-CONT-1: Schema Migration

**ID:** WU-CONT-1  
**Description:** Create the `contacts` table with Alembic migration  
**Tasks Covered:** T-CONT-1  
**Depends On:** Accounts WU-ACCT-1 (must exist before FK can reference it)  
**Estimated Time:** 30-45 minutes

**File Scope:**
| File | Action |
|------|--------|
| `backend/alembic/versions/0009_create_contacts.py` | CREATE |

**Definition of Done:**
- [ ] `contacts` table created with columns: `id`, `first_name`, `last_name`, `email`, `phone`, `job_title`, `account_id`, `created_at`, `updated_at`
- [ ] `email` column marked NOT NULL
- [ ] `first_name` and `last_name` columns marked NOT NULL
- [ ] FK constraint on `account_id` referencing `accounts(id)` with `ON DELETE SET NULL`
- [ ] Case-insensitive uniqueness on email via functional index on `lower(email)` with UNIQUE constraint
- [ ] Functional index on `lower(email)` for efficient case-insensitive lookups
- [ ] Downgrade function reverses cleanly (drops index, drops table)
- [ ] Migration tested with `alembic upgrade head` and `alembic downgrade -1`

**Reference Pattern:**
- `backend/alembic/versions/0006_create_accounts.py` - follows same structure

---

### WU-CONT-2: ORM + Schemas + Service

**ID:** WU-CONT-2  
**Description:** Implement Contact model, Pydantic schemas, and service layer with business logic  
**Tasks Covered:** T-CONT-2, T-CONT-3, T-CONT-4  
**Depends On:** WU-CONT-1, Accounts WU-ACCT-2  
**Estimated Time:** 2-3 hours

**File Scope:**
| File | Action |
|------|--------|
| `backend/app/models/contact.py` | CREATE |
| `backend/app/models/__init__.py` | UPDATE (add Contact import) |
| `backend/app/schemas/contact.py` | CREATE |
| `backend/app/schemas/__init__.py` | UPDATE (add Contact schema imports) |
| `backend/app/services/contact_service.py` | CREATE |
| `backend/app/services/__init__.py` | UPDATE (add contact_service import) |
| `backend/app/exceptions.py` | UPDATE (add Contact exceptions) |

**Definition of Done:**
- [ ] `Contact` model with SQLAlchemy 2.0 `Mapped` type hints matching migration schema
- [ ] `Contact` model has `__table_args__` with functional index for case-insensitive email
- [ ] `ContactCreate` schema: `first_name` (required), `last_name` (required), `email` (required), `phone` (optional), `job_title` (optional), `account_id` (optional)
- [ ] `ContactUpdate` schema: all fields optional
- [ ] `ContactResponse` schema: all fields with `ConfigDict(from_attributes=True)`
- [ ] `ContactNotFoundError` exception (404, `CONTACT_NOT_FOUND`)
- [ ] `ContactEmailConflictError` exception (409, `EMAIL_CONFLICT`)
- [ ] `create_contact()` - validates email uniqueness (case-insensitive), validates `account_id` if provided (calls `account_service.get_account`), raises 409 on duplicate email, raises 422 on invalid account_id
- [ ] `get_contact()` - raises `ContactNotFoundError` if not found
- [ ] `list_contacts()` - supports `search` (partial match on first_name, last_name, email, case-insensitive), `account_id` filter, `sort` (field and direction), pagination (`offset`, `limit`), returns tuple `(list[Contact], total_count)`
- [ ] `update_contact()` - validates email uniqueness if email changed, validates `account_id` if changed
- [ ] `delete_contact()` - raises `ContactNotFoundError` if not found
- [ ] `find_by_email()` - returns Contact or None (case-insensitive) - used by Leads conversion

**Reference Patterns:**
- `backend/app/models/account.py` - ORM model structure
- `backend/app/schemas/account.py` - schema structure
- `backend/app/services/account_service.py` - service function signatures, exception handling

---

### WU-CONT-3: Router

**ID:** WU-CONT-3  
**Description:** Implement REST API endpoints for Contacts CRUD  
**Tasks Covered:** T-CONT-5  
**Depends On:** WU-CONT-2, Authentication WU-AUTH-3  
**Estimated Time:** 1-1.5 hours

**File Scope:**
| File | Action |
|------|--------|
| `backend/app/routers/contacts.py` | CREATE |
| `backend/app/routers/__init__.py` | UPDATE (add contacts import) |
| `backend/app/main.py` | UPDATE (register contacts router) |

**Definition of Done:**
- [ ] `GET /contacts` - list with pagination, search, account_id filter - requires `contacts:read`
- [ ] `GET /contacts/{id}` - single contact - requires `contacts:read`
- [ ] `POST /contacts` - create contact - requires `contacts:create` - returns 201
- [ ] `PATCH /contacts/{id}` - update contact - requires `contacts:update`
- [ ] `DELETE /contacts/{id}` - delete contact - requires `contacts:delete` - returns 204
- [ ] Query params validated at boundary: `search` (max 256 chars), `account_id` (positive int), `sort` (field name with optional `-` prefix for descending), `offset` (>= 0), `limit` (1-1000)
- [ ] Response envelope format matches existing routers (success, data, meta for list)
- [ ] Router registered in `main.py` with `app.include_router(contacts.router)`

**Required Permissions (already seeded in 0003_seed_permissions.py):**
- `contacts:create`
- `contacts:read`
- `contacts:update`
- `contacts:delete`

**Reference Pattern:**
- `backend/app/routers/accounts.py` - endpoint structure, permission gating

---

### WU-CONT-4: Frontend List Page

**ID:** WU-CONT-4  
**Description:** Implement Contacts list page with search, account filter, and CRUD form  
**Tasks Covered:** T-CONT-6  
**Depends On:** WU-CONT-3, Accounts WU-ACCT-3 (for filter dropdown)  
**Estimated Time:** 2-3 hours

**File Scope:**
| File | Action |
|------|--------|
| `frontend/src/features/contacts/api.ts` | CREATE |
| `frontend/src/features/contacts/types.ts` | CREATE |
| `frontend/src/features/contacts/ContactsListPage.tsx` | CREATE |
| `frontend/src/features/contacts/ContactForm.tsx` | CREATE |
| `frontend/src/pages/ContactsPage.tsx` | UPDATE (replace placeholder with ContactsListPage) |
| `frontend/src/routes/index.tsx` | UPDATE (if needed for route) |

**Definition of Done:**
- [ ] API client functions: `listContacts()`, `getContact()`, `createContact()`, `updateContact()`, `deleteContact()`
- [ ] TypeScript types: `Contact`, `ContactCreate`, `ContactUpdate`, `ContactsListResponse`, `ContactResponse`
- [ ] List page displays contacts in table (Name, Email, Phone, Account columns)
- [ ] Name column links to contact detail page
- [ ] Account column shows linked account name with link, or dash if none
- [ ] List supports pagination via URL params (`?offset=X&limit=Y`)
- [ ] List supports search filter via URL param (`?search=X`) - searches name/email
- [ ] Account filter dropdown sourced from `GET /accounts` API
- [ ] "New Contact" button opens modal form
- [ ] Form has fields: first_name (required), last_name (required), email (required), phone, job_title, account dropdown
- [ ] Account dropdown populated from `GET /accounts` API
- [ ] Form validates required fields client-side
- [ ] 409 `EMAIL_CONFLICT` error surfaces inline on email field
- [ ] Edit button opens form pre-filled with contact data
- [ ] Delete button visible only when `hasPermission("contacts:delete")`
- [ ] Delete shows confirmation dialog
- [ ] Loading state shows spinner
- [ ] Empty state shows appropriate message

**Reference Patterns:**
- `frontend/src/features/accounts/AccountsListPage.tsx` - list page structure
- `frontend/src/features/accounts/AccountForm.tsx` - form structure
- `frontend/src/features/accounts/api.ts` - API client functions
- `frontend/src/features/accounts/types.ts` - type definitions

---

### WU-CONT-5: Frontend Detail Page

**ID:** WU-CONT-5  
**Description:** Implement Contact detail page with profile sidebar and tabs  
**Tasks Covered:** T-CONT-7  
**Depends On:** WU-CONT-3, Accounts WU-ACCT-3 (for account name resolution)  
**Estimated Time:** 1.5-2 hours

**File Scope:**
| File | Action |
|------|--------|
| `frontend/src/features/contacts/ContactDetailPage.tsx` | CREATE |
| `frontend/src/features/contacts/ContactHistoryTab.tsx` | CREATE (placeholder) |
| `frontend/src/features/contacts/ContactEmailsTab.tsx` | CREATE (placeholder) |
| `frontend/src/routes/index.tsx` | UPDATE (add `/contacts/:id` route) |
| `frontend/src/routes/config.ts` | UPDATE (add `CONTACT_DETAIL` route constant) |

**Definition of Done:**
- [ ] Detail page renders at `/contacts/:id`
- [ ] Header renders `"{first_name} {last_name}, {account.name}"` when account linked
- [ ] Header renders name-only gracefully when no account linked
- [ ] Profile sidebar shows: avatar placeholder, job title, email (clickable mailto:), phone (clickable tel:), linked account (clickable link to account detail)
- [ ] Edit button opens ContactForm in edit mode
- [ ] Tab strip with Overview, History, Emails tabs
- [ ] Overview tab shows contact info fields
- [ ] History tab shows "Coming soon - Activities module" placeholder (wired in by WU-ACT-6)
- [ ] Emails tab shows "Coming soon - Activities module" placeholder (wired in by WU-ACT-6)
- [ ] Tab components designed for extensibility - downstream modules update tab files directly
- [ ] Back button returns to contacts list
- [ ] 404 handling for non-existent contact ID

**Reference Pattern:**
- `frontend/src/features/accounts/AccountDetailPage.tsx` - detail page structure, tabs

---

### WU-CONT-6: Integration Tests

**ID:** WU-CONT-6  
**Description:** Integration tests verifying Contacts API behavior  
**Tasks Covered:** T-CONT-8  
**Depends On:** WU-CONT-3  
**Estimated Time:** 1-1.5 hours

**File Scope:**
| File | Action |
|------|--------|
| `backend/tests/test_contacts_integration.py` | CREATE |

**Definition of Done:**
- [ ] Test fixture creates in-memory SQLite DB with seeded permissions and admin user
- [ ] CRUD round-trip test: create contact, read it, verify fields match
- [ ] CRUD with `account_id`: create contact linked to account, verify account_id persisted
- [ ] CRUD without `account_id`: create contact with null account, verify works
- [ ] Duplicate email on create returns 409 `EMAIL_CONFLICT`
- [ ] Duplicate email on update returns 409 `EMAIL_CONFLICT`
- [ ] Case-insensitive email check: create with "Test@Example.com", try "test@example.com" → 409
- [ ] Invalid `account_id` on create returns 422
- [ ] `GET /contacts?account_id=X` returns only contacts with that account
- [ ] `GET /contacts?search=partial` matches partial first name, last name, and email (case-insensitive)
- [ ] `GET /contacts/{id}` for non-existent ID returns 404 `CONTACT_NOT_FOUND`
- [ ] Pagination: create 5 contacts, request limit=2, verify count/total in meta
- [ ] Sorting: verify sort by name ascending/descending returns correct order
- [ ] Delete contact returns 204 and subsequent GET returns 404

**Reference Pattern:**
- `backend/tests/test_roles_integration.py` - test structure, fixture setup

---

## Execution Sequence Diagram

```
                    ┌─────────────┐
                    │  WU-CONT-1  │
                    │  Migration  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  WU-CONT-2  │
                    │ ORM+Schema  │
                    │  +Service   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  WU-CONT-3  │
                    │   Router    │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
  ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
  │  WU-CONT-4  │   │  WU-CONT-5  │   │  WU-CONT-6  │
  │  List Page  │   │ Detail Page │   │   Tests     │
  └─────────────┘   └─────────────┘   └─────────────┘
```

**Parallelization Notes:**
- WU-CONT-1, WU-CONT-2, WU-CONT-3 must execute sequentially
- WU-CONT-4, WU-CONT-5, WU-CONT-6 can execute in parallel after WU-CONT-3

---

## Human Checkpoint Locations

| After WU | Checkpoint Type | Purpose |
|----------|-----------------|---------|
| WU-CONT-1 | **Migration Review** | Verify schema before building dependent code |
| WU-CONT-3 | **API Review** | Validate endpoints work before frontend development |
| WU-CONT-4 | **UI Review** | Review list page UX before detail page |
| WU-CONT-6 | **Final Review** | Full module verification before marking complete |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Email uniqueness edge cases (unicode, whitespace) | Medium | Medium | Trim whitespace in service layer, normalize case |
| FK constraint failure if Accounts migration not run | Low | High | Verify WU-ACCT-1 complete before starting |
| SQLite vs PostgreSQL index syntax differences | Medium | Medium | Test migration on both DBs if production uses PostgreSQL |
| Account dropdown performance with many accounts | Low | Low | Defer to future optimization (pagination on dropdown) |
| Contact deletion affects downstream modules | Low | High | Future modules must handle NULL `contact_id` gracefully |

---

## Success Criteria Mapping

| Success Criteria | Verified By |
|------------------|-------------|
| SC-CONT-001: 100% duplicate-email submissions rejected | WU-CONT-6 tests |
| SC-CONT-002: Full CRUD, search, account-filter independently verifiable | WU-CONT-6 tests, WU-CONT-4 manual testing |

---

## Downstream Modules Unblocked

After Contacts module completion, these modules can begin:
- **Opportunities** (WU-OPP-1) - uses `contacts.id` as FK target
- **Activities** (WU-ACT-1) - uses `contacts.id` as FK target  
- **Leads** (WU-LEAD-5) - uses `find_by_email()` for conversion
