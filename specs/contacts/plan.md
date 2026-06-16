# Module Plan: Contacts

**Module**: `contacts` | **Spec**: [spec.md](spec.md)

---

## Module Architecture

Standard four-layer module structure, with the canonical CRM "Contact, Company" frontend layout as its most distinctive piece.

```
routers/contacts.py        → /contacts CRUD, permission-gated
services/contact_service.py → email uniqueness check, search/sort/paginate, account_id validation
schemas/contact.py          → ContactCreate, ContactUpdate, ContactResponse
models/contact.py           → Contact ORM model
```

## Components and Responsibilities

| Component | Responsibility |
|---|---|
| `models/contact.py` | `Contact` table (id, first_name, last_name, email UNIQUE, phone, job_title, account_id FK nullable, timestamps) |
| `schemas/contact.py` | `ContactCreate { first_name, last_name, email, phone?, job_title?, account_id? }`, `ContactUpdate` (all optional), `ContactResponse` |
| `services/contact_service.py` | Email-uniqueness check (409) on create/update; validates `account_id` exists if provided (calls Accounts module); search across first/last/email; account filter |
| `routers/contacts.py` | `GET /contacts` (incl. `?account_id=`), `POST /contacts`, `GET /contacts/{id}`, `PATCH /contacts/{id}`, `DELETE /contacts/{id}` |
| Frontend `/contacts` list page | Search box, Account filter dropdown (from `GET /accounts`), sortable columns |
| Frontend `/contacts/:id` detail page | `DetailHeader` (title = `"{first_name} {last_name}, {account.name}"`), `ProfileSidebar` (avatar, job title, phone, email, account link), `TabStrip` (Overview / History / Emails) |

## Data Flow Within the Module

```
[User submits ContactForm]
   → POST /contacts
   → [contact_service: SELECT contacts WHERE email = ?] → if found: 409 EMAIL_CONFLICT
   → [contact_service: if account_id provided, validate it exists — calls Accounts module's get-by-id]
   → INSERT contacts row → ContactResponse

[User opens a Contact's detail page]
   → GET /contacts/{id} → ContactResponse
   → [if account_id set] GET /accounts/{account_id} → resolve account.name for the header/sidebar
   → [Overview tab] GET /activities?contact_id={id}&sort_by=activity_date&size=1 → "days since last contact"
   → [History tab] GET /activities?contact_id={id} (full timeline)
   → [Emails tab] GET /mock-email?to={contact.email}
```

## Integration Points with Other Modules

| Module | Integration Point |
|---|---|
| [Accounts](../accounts/plan.md) | `contact_service` validates `account_id` against Accounts' read function; the detail page resolves `account.name` for its header and clickable sidebar link |
| [Opportunities](../opportunities/plan.md) | Opportunity's Contact dropdown is scoped by the selected Account (`GET /contacts?account_id=`); Opportunity detail resolves `contact_id` to a display name via this module |
| [Activities](../activities/plan.md) | The Contact detail page's Overview/History tabs read `GET /activities?contact_id=` from the Activities module; Activities resolves `contact_id` to a display name the same way |
| [Leads](../leads/plan.md) | Leads' conversion transaction performs `SELECT contacts WHERE email = lead.email` and, if no match, an `INSERT` directly into `contacts` — the documented cross-module write exception, identical in shape to the Accounts one |

---

## Architectural Decisions Specific to This Module

- **System-wide (not per-account) email uniqueness**: a person's email identifies them uniquely regardless of which account context they're viewed from, simplifying Lead-conversion matching to a single global lookup.
- **No record-level ownership field**: like Accounts, Contacts has no `created_by_user_id` — purely role-gated.
