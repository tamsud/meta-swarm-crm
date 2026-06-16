# Module Plan: Accounts

**Module**: `accounts` | **Spec**: [spec.md](spec.md)

---

## Module Architecture

Standard four-layer module structure — the simplest CRM data module (no state machine, no cross-module write transactions of its own, only a read-side dependency check on delete).

```
routers/accounts.py        → /accounts CRUD, permission-gated
services/account_service.py → search/sort/paginate, pre-delete dependency check
schemas/account.py          → AccountCreate, AccountUpdate, AccountResponse
models/account.py           → Account ORM model
```

## Components and Responsibilities

| Component | Responsibility |
|---|---|
| `models/account.py` | `Account` table (id, name, industry, website, phone, address, timestamps) |
| `schemas/account.py` | `AccountCreate { name, industry?, website?, phone?, address? }`, `AccountUpdate` (all optional), `AccountResponse` |
| `services/account_service.py` | List with `search`/`sort_by`/`sort_dir`/pagination; on delete, runs `SELECT COUNT(*) FROM contacts WHERE account_id = ?` and `SELECT COUNT(*) FROM opportunities WHERE account_id = ?` before allowing the delete |
| `routers/accounts.py` | `GET /accounts`, `POST /accounts`, `GET /accounts/{id}`, `PATCH /accounts/{id}`, `DELETE /accounts/{id}` — gated by `accounts:read`/`create`/`update`/`delete` respectively |
| Frontend `/accounts` list page | Search toolbar, sortable columns, "New Account" button, delete action visible only with `accounts:delete` |
| Frontend `/accounts/:id` detail page | `DetailHeader` + two tabs: Contacts (`GET /contacts?account_id=`), Opportunities (`GET /opportunities?account_id=`) |

## Data Flow Within the Module

```
[User submits AccountForm: name + optional fields]
   → POST /accounts → [account_service: INSERT] → AccountResponse

[User searches/sorts the list]
   → GET /accounts?search=acme&sort_by=name&sort_dir=asc&page=1&size=20
   → [account_service: WHERE lower(name) LIKE lower('%acme%') ORDER BY name ASC LIMIT 20 OFFSET 0]
   → PaginatedResponse[AccountResponse]

[User attempts delete]
   → DELETE /accounts/{id}
   → [account_service: dependent_contacts = COUNT(contacts WHERE account_id=id)]
   → [account_service: dependent_opps = COUNT(opportunities WHERE account_id=id)]
   → if dependent_contacts > 0 OR dependent_opps > 0:
        409 {"detail": "Cannot delete account: has N contact(s) and M opportunity(ies)", "code": "ACCOUNT_HAS_DEPENDENTS"}
   → else: DELETE accounts row → 204
```

## Integration Points with Other Modules

| Module | Integration Point |
|---|---|
| [Contacts](../contacts/plan.md) | Contacts' detail page resolves `account_id` to an account name via this module's `GET /accounts/{id}`; this module's delete-guard reads the `contacts` table directly (read-only cross-module query) |
| [Opportunities](../opportunities/plan.md) | Same pattern as Contacts — FK target + delete-guard read + Opportunity's Account dropdown sources `GET /accounts` |
| [Leads](../leads/plan.md) | Leads' conversion transaction performs a case-insensitive `SELECT ... WHERE lower(name) = lower(?)` against this module's table and, if no match, an `INSERT` directly into `accounts` — the one documented cross-module write exception |

---

## Architectural Decisions Specific to This Module

- **Pre-delete count query over relying on FK `RESTRICT` exceptions**: produces a precise, human-readable dependency count instead of a generic `IntegrityError`.
- **No record-level ownership field**: unlike Leads/Activities, Accounts has no `created_by_user_id` — access is governed purely by role-level `accounts:*` permissions, since no business requirement scopes Account visibility/editability to its creator.
