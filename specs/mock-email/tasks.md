# Module Tasks: Mock Email

**Module**: `mock-email` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Work Units**: [work-units.md](work-units.md)

---

## Task Overview

Mock Email is a standard CRUD module with its own database table. Tasks follow the typical backend-first, then frontend pattern.

---

## Tasks

### T-EMAIL-1: Create Mock Emails Table Migration

**Description**: Create the database migration for the `mock_emails` table.

**Acceptance Criteria**:
- [ ] Migration creates `mock_emails` table with columns: id (UUID PK), subject, from_email, to_email, body, status, created_at
- [ ] `status` column has CHECK constraint: `status IN ('unread', 'read')`
- [ ] `status` defaults to 'unread'
- [ ] `created_at` defaults to `now()`
- [ ] Index on `subject` for search performance
- [ ] Index on `created_at` for sort performance
- [ ] `alembic upgrade head` succeeds
- [ ] `alembic downgrade` reverses cleanly

**Prerequisites**: Project Setup complete (WU-SETUP-9)

---

### T-EMAIL-2: Add Mock Email Permission

**Description**: Add `mock-email:view` permission to the catalogue and assign to all roles.

**Acceptance Criteria**:
- [ ] Migration adds `('mock-email:view', 'mock-email', 'view', 'View mock email inbox')` to permissions
- [ ] Migration assigns `mock-email:view` to Admin, Manager, and Sales Rep roles
- [ ] `alembic upgrade head` succeeds
- [ ] `alembic downgrade` reverses cleanly

**Prerequisites**: T-EMAIL-1, Permissions WU-PERM-1, Roles WU-ROLE-1

---

### T-EMAIL-3: Create ORM Model and Schemas

**Description**: Define the SQLAlchemy model and Pydantic schemas for mock emails.

**Acceptance Criteria**:
- [ ] `MockEmail` model in `backend/app/models/mock_email.py`
- [ ] Model columns match migration exactly
- [ ] `MockEmailCreate` schema: to_email (EmailStr), subject (str), body (str, optional)
- [ ] `MockEmailListItem` schema: id, subject, from_email, to_email, preview (str), status, created_at
- [ ] `MockEmailDetail` schema: id, subject, from_email, to_email, body, status, created_at
- [ ] All schemas have `from_attributes = True`

**Prerequisites**: T-EMAIL-1

---

### T-EMAIL-4: Create Service Layer

**Description**: Implement the mock email service with all business logic.

**Acceptance Criteria**:
- [ ] `list_mock_emails(db, sort, search, offset, limit)`:
  - Supports sort by subject (asc/desc) and date (asc/desc)
  - Supports search by subject (case-insensitive contains)
  - Returns paginated results with preview (truncated body to 80 chars)
  - Returns total count for pagination meta
- [ ] `get_mock_email(db, id)`:
  - Returns full email detail
  - Marks email as "read" if currently "unread"
  - Raises 404 if not found
- [ ] `create_mock_email(db, data)`:
  - Sets from_email to "crm@demo.local"
  - Sets status to "unread"
  - Returns created email
- [ ] `mark_as_read(db, id)`:
  - Updates status to "read"
  - Raises 404 if not found
- [ ] `clear_mock_emails(db)`:
  - Deletes all mock emails
  - Returns count of deleted emails
- [ ] Unit tests cover all service functions

**Prerequisites**: T-EMAIL-3

---

### T-EMAIL-5: Create Router

**Description**: Implement the API endpoints for mock email operations.

**Acceptance Criteria**:
- [ ] `GET /mock-emails` endpoint:
  - Query params: sort, search, offset, limit
  - Returns paginated list with meta (total, offset, limit)
  - Protected by `require_permission("mock-email:view")`
- [ ] `GET /mock-emails/{id}` endpoint:
  - Returns full email detail
  - Marks as read as side effect
  - Returns 404 if not found
- [ ] `POST /mock-emails` endpoint:
  - Accepts MockEmailCreate body
  - Returns created email
  - Returns 422 for validation errors
- [ ] `PATCH /mock-emails/{id}/read` endpoint:
  - Marks email as read
  - Returns updated email
  - Returns 404 if not found
- [ ] `DELETE /mock-emails` endpoint:
  - Deletes all mock emails
  - Returns count of deleted emails
- [ ] Router registered in main.py at `/mock-emails` prefix
- [ ] All endpoints appear in OpenAPI docs

**Prerequisites**: T-EMAIL-4

---

### T-EMAIL-6: Create Frontend Types and API

**Description**: Set up TypeScript types and React Query hooks for mock email.

**Acceptance Criteria**:
- [ ] TypeScript interfaces match backend schemas
- [ ] `useMockEmails(params)` hook for list with sort/search/pagination
- [ ] `useMockEmail(id)` hook for detail
- [ ] `useCreateMockEmail()` mutation hook
- [ ] `useMarkAsRead()` mutation hook
- [ ] `useClearMockEmails()` mutation hook

**Prerequisites**: T-EMAIL-5 (backend must exist for type alignment)

---

### T-EMAIL-7: Create Mock Email Inbox Page

**Description**: Replace the placeholder MockEmailPage with the full inbox implementation.

**Acceptance Criteria**:
- [ ] Table displays: Subject, From, To, Preview, Date, Status columns
- [ ] Subject column: sortable, searchable (search icon in header)
- [ ] Date column: sortable
- [ ] Sort indicators show current sort state
- [ ] Search input filters by subject
- [ ] Unread rows: highlighted background (`bg-indigo-50/30`), indigo "Unread" badge
- [ ] Read rows: normal background, gray "Read" badge
- [ ] Subject is clickable link to detail page
- [ ] Compose button opens compose modal
- [ ] Clear button shows confirmation dialog, then clears all emails
- [ ] Pagination controls at bottom of table
- [ ] Empty state when no emails
- [ ] Loading state shows skeleton
- [ ] Page title "Mail Inbox | CRM"

**Prerequisites**: T-EMAIL-6

---

### T-EMAIL-8: Create Compose Modal and Detail Page

**Description**: Implement the compose form modal and email detail page.

**Acceptance Criteria**:
- [ ] `ComposeModal`:
  - Form fields: To Email (required, email validation), Subject (required), Body (optional, textarea)
  - Submit creates email, closes modal, refreshes list
  - Cancel closes modal
  - Loading state on submit
  - Validation errors displayed inline
- [ ] `MockEmailDetailPage`:
  - Route: `/admin/mock-email/:id`
  - Subject as page heading
  - Metadata row: From, To, Date (formatted)
  - Status badge (updates to "Read" on view)
  - Full body text in scrollable card
  - Back button returns to inbox
  - 404 handling for invalid ID
  - Loading state
- [ ] Route added to `frontend/src/routes/index.tsx`

**Prerequisites**: T-EMAIL-7

---

### T-EMAIL-9: Integration Tests

**Description**: End-to-end tests for mock email functionality.

**Acceptance Criteria**:
- [ ] Test: CRUD round trip — create → list (appears) → get (marks read) → clear → list (empty)
- [ ] Test: Sort by subject ascending and descending
- [ ] Test: Sort by date ascending and descending
- [ ] Test: Search by subject returns matching results only
- [ ] Test: GET /mock-emails/{id} for non-existent ID returns 404
- [ ] Test: Unauthorized request returns 401
- [ ] Test: User without `mock-email:view` permission returns 403

**Prerequisites**: T-EMAIL-8

---

## Task Dependencies

```
T-EMAIL-1 (migration)
    │
    ├─────────────────┐
    ▼                 ▼
T-EMAIL-2         T-EMAIL-3
(permission)      (model/schema)
    │                 │
    └────────┬────────┘
             ▼
         T-EMAIL-4
         (service)
             │
             ▼
         T-EMAIL-5
         (router)
             │
             ▼
         T-EMAIL-6
         (frontend types/api)
             │
             ▼
         T-EMAIL-7
         (inbox page)
             │
             ▼
         T-EMAIL-8
         (compose + detail)
             │
             ▼
         T-EMAIL-9
         (integration tests)
```
