# Module Work Units: Mock Email

**Module**: `mock-email` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Tasks**: [tasks.md](tasks.md)

---

## Dependency Graph

### Upstream
- **Project Setup** WU-SETUP-9 (backend scaffold, Alembic baseline)
- **Permissions** WU-PERM-1 (permissions table for new code)
- **Roles** WU-ROLE-1 (role_permissions table for assignment)
- **Authentication** WU-AUTH-3 (require_permission dependency)

### Downstream
- **Deployment** (seeds mock email data as part of demo dataset)

### Internal Sequence
```
WU-EMAIL-1 ──► WU-EMAIL-2 ──► WU-EMAIL-3 ──► WU-EMAIL-4 ──► WU-EMAIL-5
```

---

## Work Units

### WU-EMAIL-1: Schema Migration + Permission Seed

**Tasks**: T-EMAIL-1, T-EMAIL-2
**Depends on**: Project Setup WU-SETUP-9, Permissions WU-PERM-1, Roles WU-ROLE-1

**File scope**:
- `backend/alembic/versions/00XX_create_mock_emails.py` (new)
- `backend/alembic/versions/00XX_add_mock_email_permission.py` (new)

**Definition of Done**:
- [ ] `mock_emails` table created with columns: id (UUID PK), subject, from_email, to_email, body, status, created_at
- [ ] `status` has CHECK constraint `IN ('unread', 'read')` and defaults to 'unread'
- [ ] `created_at` defaults to `now()`
- [ ] Indexes on `subject` and `created_at`
- [ ] Permission `('mock-email:view', 'mock-email', 'view', 'View mock email inbox')` added
- [ ] Permission assigned to Admin, Manager, Sales Rep roles
- [ ] `alembic upgrade head` succeeds
- [ ] Both migrations reverse cleanly

**Success Criteria covered**: SC-EMAIL-001 (database foundation)

---

### WU-EMAIL-2: Backend ORM + Schemas + Service

**Tasks**: T-EMAIL-3, T-EMAIL-4
**Depends on**: WU-EMAIL-1

**File scope**:
- `backend/app/models/mock_email.py` (new)
- `backend/app/schemas/mock_email.py` (new)
- `backend/app/services/mock_email_service.py` (new)

**Definition of Done**:
- [ ] `MockEmail` ORM model with all columns
- [ ] `MockEmailCreate` schema: to_email (EmailStr), subject (str), body (optional str)
- [ ] `MockEmailListItem` schema with preview field (body truncated to 80 chars)
- [ ] `MockEmailDetail` schema with full body
- [ ] All schemas have `from_attributes = True`
- [ ] `list_mock_emails()` supports sort (subject, -subject, date, -date), search (subject ILIKE), pagination
- [ ] `get_mock_email()` returns detail and marks as read
- [ ] `create_mock_email()` sets from_email to "crm@demo.local", status to "unread"
- [ ] `mark_as_read()` updates status to "read"
- [ ] `clear_mock_emails()` deletes all and returns count
- [ ] Unit tests cover all service functions

**Success Criteria covered**: SC-EMAIL-001, SC-EMAIL-002

---

### WU-EMAIL-3: Backend Router

**Tasks**: T-EMAIL-5
**Depends on**: WU-EMAIL-2, Authentication WU-AUTH-3

**File scope**:
- `backend/app/routers/mock_email.py` (new)
- `backend/app/main.py` (update — register router)

**Definition of Done**:
- [ ] `GET /mock-emails` — paginated list with sort, search, offset, limit query params
- [ ] `GET /mock-emails/{id}` — detail with mark-as-read side effect, 404 for not found
- [ ] `POST /mock-emails` — compose new email, 422 for validation errors
- [ ] `PATCH /mock-emails/{id}/read` — explicit mark-as-read, 404 for not found
- [ ] `DELETE /mock-emails` — bulk clear, returns delete count
- [ ] All endpoints protected by `require_permission("mock-email:view")`
- [ ] Router registered at `/mock-emails` prefix
- [ ] All endpoints in OpenAPI docs with correct schemas

**Success Criteria covered**: SC-EMAIL-001, SC-EMAIL-003

---

### WU-EMAIL-4: Frontend Pages

**Tasks**: T-EMAIL-6, T-EMAIL-7, T-EMAIL-8
**Depends on**: WU-EMAIL-3

**File scope**:
- `frontend/src/features/mock-email/api.ts` (new)
- `frontend/src/features/mock-email/types.ts` (new)
- `frontend/src/features/mock-email/components/ComposeModal.tsx` (new)
- `frontend/src/pages/admin/MockEmailPage.tsx` (update — replace placeholder)
- `frontend/src/pages/admin/MockEmailDetailPage.tsx` (new)
- `frontend/src/routes/index.tsx` (update — add detail route)
- `frontend/src/routes/config.ts` (update — add MOCK_EMAIL_DETAIL route constant)

**Definition of Done**:
- [ ] TypeScript interfaces match backend schemas
- [ ] React Query hooks: `useMockEmails`, `useMockEmail`, `useCreateMockEmail`, `useMarkAsRead`, `useClearMockEmails`
- [ ] Inbox table with columns: Subject (sortable, searchable), From, To, Preview, Date (sortable), Status
- [ ] Sort indicators show current sort state
- [ ] Subject search filters results
- [ ] Unread rows: `bg-indigo-50/30`, indigo "Unread" badge
- [ ] Read rows: normal background, gray "Read" badge
- [ ] Subject links to detail page `/admin/mock-email/:id`
- [ ] Compose button opens modal with To Email, Subject, Body fields
- [ ] Clear button shows confirmation, then deletes all
- [ ] Detail page shows Subject heading, From/To/Date metadata, Status badge, full Body
- [ ] Detail page has Back button
- [ ] Route `/admin/mock-email/:id` registered
- [ ] Loading and empty states
- [ ] Page titles set correctly

**Success Criteria covered**: SC-EMAIL-002, SC-EMAIL-003

---

### WU-EMAIL-5: Integration Tests

**Tasks**: T-EMAIL-9
**Depends on**: WU-EMAIL-4

**File scope**:
- `backend/tests/test_mock_email_integration.py` (new)

**Definition of Done**:
- [ ] Test: CRUD round trip — create → list → get (marks read) → clear → list (empty)
- [ ] Test: Sort by subject ascending returns alphabetical order
- [ ] Test: Sort by subject descending returns reverse alphabetical order
- [ ] Test: Sort by date ascending returns oldest first
- [ ] Test: Sort by date descending returns newest first
- [ ] Test: Search filters to matching subjects only
- [ ] Test: GET non-existent ID returns 404
- [ ] Test: Unauthorized request returns 401
- [ ] Test: User without `mock-email:view` returns 403
- [ ] All tests pass with `pytest backend/tests/test_mock_email_integration.py`

**Success Criteria covered**: SC-EMAIL-001, SC-EMAIL-002, SC-EMAIL-003

---

## Execution Summary

| WU | Description | Est. Time | Dependencies |
|----|-------------|-----------|--------------|
| WU-EMAIL-1 | Schema migration + permission seed | 30 min | Project Setup, Permissions, Roles |
| WU-EMAIL-2 | Backend ORM + schemas + service | 1.5 hours | WU-EMAIL-1 |
| WU-EMAIL-3 | Backend router | 45 min | WU-EMAIL-2, Authentication |
| WU-EMAIL-4 | Frontend pages | 3 hours | WU-EMAIL-3 |
| WU-EMAIL-5 | Integration tests | 1 hour | WU-EMAIL-4 |

**Total estimated time**: ~7 hours

**Human Checkpoints**:
- After WU-EMAIL-3: Verify API endpoints work via OpenAPI docs
- After WU-EMAIL-4: Visual review of inbox and detail pages against mock
