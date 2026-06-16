# Module Tasks: Contacts

**Module**: `contacts` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Prerequisites

- [ ] [Project Setup](../project-setup/tasks.md) T-SETUP-13 completed — needs the backend scaffold to exist.
- [ ] [Accounts module](../accounts/tasks.md) T-ACCT-1 (schema) completed — `contacts.account_id` FK target must exist, even though the value is nullable.

---

## Implementation Tasks

| # | Task | Depends On |
|---|---|---|
| T-CONT-1 | Create `contacts` table Alembic migration | Accounts T-ACCT-1 |
| T-CONT-2 | Implement `models/contact.py` | T-CONT-1 |
| T-CONT-3 | Implement `schemas/contact.py` | T-CONT-2 |
| T-CONT-4 | Implement `services/contact_service.py`: email uniqueness, account_id validation, search/sort/paginate | T-CONT-2, T-CONT-3, Accounts read function |
| T-CONT-5 | Implement `routers/contacts.py`: all 5 endpoints | T-CONT-4 |
| T-CONT-6 | Frontend: `/contacts` list page | T-CONT-5, Accounts `GET /accounts` (for filter dropdown) |
| T-CONT-7 | Frontend: `/contacts/:id` detail page (header + ProfileSidebar + TabStrip; History/Emails tabs render empty until Activities exists) | T-CONT-5, Accounts (for account name resolution) |
| T-CONT-8 | Integration tests: email uniqueness 409, account filter, CRUD round trip | T-CONT-5 |

## Task Sequencing

```
T-CONT-1 ──► T-CONT-2 ──► T-CONT-3 ──► T-CONT-4 ──► T-CONT-5 ──┬──► T-CONT-6
                                                                  ├──► T-CONT-7
                                                                  └──► T-CONT-8
```

---

## Acceptance Criteria

- [ ] AC-1: Contact CRUD round trip succeeds, including optional `account_id` linkage (FR-CONT-001, FR-CONT-004).
- [ ] AC-2: Duplicate email on create or update returns 409 `EMAIL_CONFLICT` (FR-CONT-002, SC-CONT-001).
- [ ] AC-3: `GET /contacts?account_id=` returns only contacts linked to that account (FR-CONT-003).
- [ ] AC-4: `GET /contacts?search=` matches partial first/last name or email, case-insensitive (FR-CONT-003).
- [ ] AC-5: The detail page header renders `"{first_name} {last_name}, {account.name}"` correctly when an account is linked, and gracefully (name only) when it is not.

## Dependencies and Prerequisites Recap

- **Hard blocker**: [Accounts](../accounts/tasks.md) T-ACCT-1 before T-CONT-1.
- **Downstream**: [Opportunities](../opportunities/tasks.md), [Activities](../activities/tasks.md), and [Leads](../leads/tasks.md) are all blocked on T-CONT-1 (FK target / conversion match target).
- **Parallelizable**: Contacts and [Opportunities](../opportunities/tasks.md) have no dependency on each other and may be built concurrently once Accounts is ready.
