# Module Plan: Mock Email

**Module**: `mock-email` | **Spec**: [spec.md](spec.md) | **Tasks**: [tasks.md](tasks.md) | **Work Units**: [work-units.md](work-units.md)

---

## Architecture Overview

Mock Email is a standard CRUD module with its own database table, following the typical CRM module structure:

| Layer | Component | Description |
|-------|-----------|-------------|
| Migration | `00XX_create_mock_emails.py` | Creates `mock_emails` table |
| Model | `mock_email.py` | SQLAlchemy ORM model |
| Schema | `mock_email.py` | Pydantic schemas for API |
| Service | `mock_email_service.py` | Business logic |
| Router | `mock_email.py` | FastAPI endpoints |
| Frontend | `MockEmailPage.tsx`, `MockEmailDetailPage.tsx` | React UI |

---

## Component Responsibilities

### Backend

**`backend/alembic/versions/00XX_create_mock_emails.py`** (new)
- Creates `mock_emails` table with columns:
  - `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
  - `subject` VARCHAR(255) NOT NULL
  - `from_email` VARCHAR(255) NOT NULL
  - `to_email` VARCHAR(255) NOT NULL
  - `body` TEXT NULLABLE
  - `status` VARCHAR(20) NOT NULL DEFAULT 'unread' CHECK (status IN ('unread', 'read'))
  - `created_at` TIMESTAMP NOT NULL DEFAULT now()
- Index on `subject` for search performance
- Index on `created_at` for sort performance

**`backend/alembic/versions/00XX_add_mock_email_permission.py`** (new)
- Adds `mock-email:view` to permissions table
- Assigns to all 3 system roles

**`backend/app/models/mock_email.py`** (new)
- `MockEmail` SQLAlchemy model
- Column definitions matching migration
- No relationships (standalone table)

**`backend/app/schemas/mock_email.py`** (new)
- `MockEmailCreate`: to_email, subject, body (optional)
- `MockEmailListItem`: id, subject, from_email, to_email, preview (truncated body), status, created_at
- `MockEmailDetail`: id, subject, from_email, to_email, body (full), status, created_at

**`backend/app/services/mock_email_service.py`** (new)
- `list_mock_emails(db, sort, search, offset, limit)` → paginated list with preview
- `get_mock_email(db, id)` → full detail, marks as read
- `create_mock_email(db, data)` → creates with from_email="crm@demo.local"
- `mark_as_read(db, id)` → explicit status update
- `clear_mock_emails(db)` → bulk delete all

**`backend/app/routers/mock_email.py`** (new)
- `GET /mock-emails` → paginated list with sort/search
- `GET /mock-emails/{id}` → detail (marks as read)
- `POST /mock-emails` → compose
- `PATCH /mock-emails/{id}/read` → explicit mark-as-read
- `DELETE /mock-emails` → bulk clear
- All endpoints: `require_permission("mock-email:view")`

### Frontend

**`frontend/src/features/mock-email/api.ts`** (new)
- React Query hooks: `useMockEmails(params)`, `useMockEmail(id)`, `useCreateMockEmail()`, `useMarkAsRead()`, `useClearMockEmails()`

**`frontend/src/features/mock-email/types.ts`** (new)
- TypeScript interfaces matching backend schemas

**`frontend/src/pages/admin/MockEmailPage.tsx`** (update — replace placeholder)
- Inbox table with columns: Subject, From, To, Preview, Date, Status
- Column sorting (Subject, Date)
- Subject search input
- Compose button → opens modal
- Clear button → confirmation dialog → bulk delete
- Row click → navigate to detail page
- Unread rows: highlighted background, indigo "Unread" badge
- Read rows: normal background, gray "Read" badge

**`frontend/src/pages/admin/MockEmailDetailPage.tsx`** (new)
- Subject as page heading
- Metadata row: From, To, Date
- Status badge
- Full body text in scrollable card
- Back button returns to inbox

**`frontend/src/features/mock-email/components/ComposeModal.tsx`** (new)
- Form fields: To Email (required), Subject (required), Body (optional)
- Submit creates email and closes modal
- Cancel closes modal

**`frontend/src/routes/index.tsx`** (update)
- Add route: `/admin/mock-email/:id` → `MockEmailDetailPage`

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                 │
│                                                                  │
│  MockEmailPage                    MockEmailDetailPage            │
│  ┌──────────────────────┐        ┌──────────────────────┐       │
│  │ Inbox Table          │        │ Email Detail         │       │
│  │ - Sort/Search        │───────►│ - Full body          │       │
│  │ - Compose button     │        │ - Back button        │       │
│  │ - Clear button       │        └──────────────────────┘       │
│  └──────────────────────┘                                        │
│           │                              │                       │
│           ▼                              ▼                       │
│  GET /mock-emails          GET /mock-emails/{id}                │
│  POST /mock-emails         (marks as read)                      │
│  DELETE /mock-emails                                             │
└───────────────────────────────────────────────────────────────┬──┘
                                                                │
┌───────────────────────────────────────────────────────────────┼──┐
│                         Backend                               ▼  │
│                                                                  │
│  mock_email_router.py                                            │
│    └─ mock_email_service.py                                      │
│         └─ MockEmail model                                       │
│              └─ mock_emails table                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## Integration Points

### Upstream Dependencies

| Module | Required Artifact | Purpose |
|--------|-------------------|---------|
| Authentication | `get_current_user` dependency | JWT validation |
| Permissions | `require_permission()` dependency | Route protection |

### Downstream Dependencies

| Module | Uses Mock Email For |
|--------|---------------------|
| Deployment | Seeds ~20 mock emails as part of demo dataset |

---

## Architectural Decisions Specific to This Module

### ADR-EMAIL-1: Standalone Table vs Activities Extension

**Decision**: Mock Email uses its own `mock_emails` table, not the Activities table.

**Rationale**:
- Activities have different schema (contact_id/opportunity_id links, created_by ownership)
- Mock emails represent system-generated outbound messages, not user activities
- Keeps the Activities table focused on user-logged interactions
- Simpler queries without filtering by type

### ADR-EMAIL-2: Mark-as-Read on Detail View

**Decision**: Viewing email detail automatically marks it as read (side effect).

**Rationale**:
- Matches real email client behavior
- Reduces user friction (no manual "mark as read" step needed)
- Explicit PATCH endpoint still available for batch operations or programmatic use

### ADR-EMAIL-3: Fixed From Email

**Decision**: All composed emails use `from_email = "crm@demo.local"`.

**Rationale**:
- Mock emails represent CRM system communications, not user-to-user messages
- Simplifies compose form (one less field)
- Consistent with existing seed data pattern

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Email not found | GET /mock-emails/{id} returns 404 |
| Invalid compose data | POST /mock-emails returns 422 with validation details |
| No emails to clear | DELETE /mock-emails returns 200 (idempotent) |
| Unauthorized | Returns 401 (JWT invalid/missing) |
| Permission denied | Returns 403 (missing `mock-email:view`) |

---

## Sorting and Search Implementation

**Sort parameter format**: `?sort=field` or `?sort=-field` (prefix `-` for descending)

| Sort Value | SQL Equivalent |
|------------|----------------|
| `subject` | `ORDER BY subject ASC` |
| `-subject` | `ORDER BY subject DESC` |
| `date` | `ORDER BY created_at ASC` |
| `-date` | `ORDER BY created_at DESC` |

**Search parameter**: `?search=term` filters where `subject ILIKE '%term%'`

**Default sort**: `-date` (newest first)
