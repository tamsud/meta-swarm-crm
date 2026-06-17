# Module Specification: Mock Email

**Module**: `mock-email` | **Created**: 2026-06-17 | **Status**: Draft

---

## Module Scope & Objectives

Mock Email provides a simulated email outbox for demonstration and testing purposes. It displays emails that the CRM "sent" to contacts — allowing users to see what outbound communications would look like without actually sending real emails. This is a development/demo utility, not a production email system.

**In scope**: Email inbox list view with sorting and search, email detail view, compose new mock email, bulk clear, read/unread status tracking.

**Out of scope**: Actual email sending via SMTP/API, email templates, attachments, reply/forward functionality, email threading, contact linking.

**Objective**: Provide a realistic email inbox experience for demos and testing, populated with seed data that shows typical CRM email communications (welcome emails, proposals, follow-ups).

---

## User Stories

### User Story 10 - Mock Email Inbox (Priority: P7)

An admin or demo user needs to view simulated outbound emails to understand what communications the CRM would send to contacts, verify email content during testing, and demonstrate the platform's communication capabilities.

**Why this priority**: Mock Email is a demo utility with no dependencies from other modules. It can be built at any point after Authentication is complete.

**Independent Test**: View the inbox list, sort by date and subject, search by subject, click to view detail (marks as read), compose a new email, clear all emails.

**Acceptance Scenarios**:

1. **Given** mock emails exist, **When** a user visits `/admin/mock-email`, **Then** a paginated list displays showing Subject, From, To, Preview, Date, and Status columns.
2. **Given** an unread email, **When** a user clicks on its subject to view the detail, **Then** the email status changes to "read" and the detail page displays the full email body.
3. **Given** the inbox, **When** a user clicks the "Compose" button and fills out the form, **Then** a new mock email is created with status "unread".
4. **Given** emails exist, **When** a user clicks "Clear", **Then** all mock emails are deleted after confirmation.
5. **Given** the inbox, **When** a user clicks the Date column header, **Then** emails are sorted by date (toggle ascending/descending).
6. **Given** the inbox, **When** a user types in the Subject search field, **Then** only emails with matching subjects are displayed.

### Edge Cases

- What happens when there are no emails? → Empty state message displayed.
- What happens when search returns no results? → Empty state with "No emails match your search".
- What happens when composing without a required field? → Validation error displayed.

---

## Functional Requirements

- **FR-EMAIL-001**: System MUST store mock emails with fields: id (UUID), subject (required), from_email (required), to_email (required), body (optional), status (default: "unread"), created_at (default: now).
- **FR-EMAIL-002**: System MUST provide a paginated list endpoint `GET /mock-emails` with optional query parameters: `sort` (subject, -subject, date, -date), `search` (subject contains), `offset`, `limit`.
- **FR-EMAIL-003**: System MUST provide a detail endpoint `GET /mock-emails/{id}` that returns the full email and marks it as "read" as a side effect.
- **FR-EMAIL-004**: System MUST provide a compose endpoint `POST /mock-emails` accepting `{to_email, subject, body?}`. The `from_email` field MUST default to "crm@demo.local".
- **FR-EMAIL-005**: System MUST provide an explicit mark-as-read endpoint `PATCH /mock-emails/{id}/read` for marking without viewing detail.
- **FR-EMAIL-006**: System MUST provide a bulk clear endpoint `DELETE /mock-emails` that deletes all mock emails.
- **FR-EMAIL-007**: List response MUST include truncated body preview (first 80 characters) for the Preview column.
- **FR-EMAIL-008**: Status field MUST be one of: "unread" (indigo badge, highlighted row background) or "read" (gray badge, normal row background).
- **FR-EMAIL-009**: Detail page MUST display: Subject (heading), From/To/Date (metadata row), Status badge, full Body text (in scrollable area), Back button.

## Key Entities

- **MockEmail**: A simulated outbound email record. Key attributes: id (UUID), subject, from_email, to_email, body (nullable), status ("unread"/"read"), created_at.

---

## Success Criteria

- **SC-EMAIL-001**: All CRUD operations (list, detail, compose, clear) function correctly and return appropriate HTTP status codes.
- **SC-EMAIL-002**: Viewing an email detail automatically transitions its status from "unread" to "read".
- **SC-EMAIL-003**: List sorting and search work correctly with results reflecting the applied filters.

---

## Dependencies on Other Modules

| Dependency | Direction | Reason |
|---|---|---|
| [Authentication](../authentication/spec.md) | Mock Email **depends on** (enforcement only) | Bearer token required for all endpoints |
| [Permissions](../permissions/spec.md) | Mock Email **depends on** (enforcement only) | `mock-email:view` permission gating |
| [Deployment](../deployment/spec.md) | **Depended on by** Deployment | Deployment seed script populates mock emails |

**Build order implication**: Mock Email can be built any time after Authentication is complete. The Deployment module will seed mock email data as part of its 50+ record demo dataset.

---

## UI Reference

Mock: `specs/mocks/Mail Inbox _ CRM.html`

---

## Permission Notes

**Permission code**: `mock-email:view`

**Naming convention note**: This introduces a hyphenated module name in the permissions catalogue. All existing module names are single words (accounts, contacts, leads, etc.). This is an intentional exception for readability. Alternative considered: `mockemail:view` — rejected for reduced readability.

**Role assignment**: All 3 system roles (Admin, Manager, Sales Rep) receive `mock-email:view` to enable demo access for any logged-in user. The feature appears in the Admin section of navigation but is accessible to all roles for demonstration purposes.
