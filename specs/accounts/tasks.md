# Module Tasks: Accounts

**Module**: `accounts` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Prerequisites

- [ ] [Project Setup](../project-setup/tasks.md) T-SETUP-13 completed — needs the backend scaffold to exist. No other CRM-data dependency — Accounts otherwise has none. Authentication's `require_permission` dependency should exist before T-ACCT-5 is fully gated, but routes can be stubbed/built in parallel.

---

## Implementation Tasks

| # | Task | Depends On |
|---|---|---|
| T-ACCT-1 | Create `accounts` table Alembic migration | Backend project scaffolding |
| T-ACCT-2 | Implement `models/account.py` | T-ACCT-1 |
| T-ACCT-3 | Implement `schemas/account.py` | T-ACCT-2 |
| T-ACCT-4 | Implement `services/account_service.py`: CRUD, search/sort/paginate, delete-dependency guard | T-ACCT-2, T-ACCT-3 |
| T-ACCT-5 | Implement `routers/accounts.py`: all 5 endpoints | T-ACCT-4, Permissions catalogue must include `accounts:*` codes |
| T-ACCT-6 | Frontend: `/accounts` list page + `AccountForm` | T-ACCT-5 |
| T-ACCT-7 | Frontend: `/accounts/:id` detail page (Contacts/Opportunities tabs — can render empty until those modules exist) | T-ACCT-5 |
| T-ACCT-8 | Integration tests: CRUD round trip, search, delete-blocked-by-dependents (requires Contacts and/or Opportunities to exist to create a real dependent) | T-ACCT-5, Contacts T-CONT-1 or Opportunities T-OPP-1 |

## Task Sequencing

```
T-ACCT-1 ──► T-ACCT-2 ──► T-ACCT-3 ──► T-ACCT-4 ──► T-ACCT-5 ──┬──► T-ACCT-6
                                                                 └──► T-ACCT-7
T-ACCT-8 runs after Contacts or Opportunities has at least a working create endpoint
```

---

## Acceptance Criteria

- [ ] AC-1: Account create/read/update/delete all function correctly with proper permission gating (FR-ACCT-001, FR-ACCT-003, FR-ACCT-005).
- [ ] AC-2: `GET /accounts?search=acme` returns only matching accounts, case-insensitive (FR-ACCT-002).
- [ ] AC-3: Deleting an account with ≥1 dependent Contact or Opportunity returns 409 with both counts named in the message (FR-ACCT-004, SC-ACCT-001).
- [ ] AC-4: A Sales Rep's `DELETE /accounts/{id}` call returns 403 regardless of frontend state (FR-ACCT-005).
- [ ] AC-5: 10,000-record dataset paginates within 3 seconds (SC-ACCT-002) — defer full-scale verification to the cross-module performance check in Sprint 6 equivalent, but the query plan (indexed `lower(name)`) should be validated at this module's implementation time.

## Dependencies and Prerequisites Recap

- **No hard blocker** — Accounts can start immediately alongside [Permissions](../permissions/tasks.md).
- **Downstream**: [Contacts](../contacts/tasks.md) and [Opportunities](../opportunities/tasks.md) are blocked on T-ACCT-1 (FK target). [Leads](../leads/tasks.md)'s conversion logic is blocked on T-ACCT-4 (needs the case-insensitive name-match query function).
