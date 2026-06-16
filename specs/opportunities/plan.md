# Module Plan: Opportunities

**Module**: `opportunities` | **Spec**: [spec.md](spec.md)

---

## Module Architecture

Standard four-layer module structure, with value/probability validation living in the Pydantic schema layer (not a separate state machine, since stage transitions are non-linear/unrestricted).

```
routers/opportunities.py        → /opportunities CRUD, permission-gated
services/opportunity_service.py → filter/sort/paginate, default-stage assignment
schemas/opportunity.py          → OpportunityCreate, OpportunityUpdate, OpportunityResponse (value/probability validators)
models/opportunity.py           → Opportunity ORM model + OpportunityStage enum
```

## Components and Responsibilities

| Component | Responsibility |
|---|---|
| `models/opportunity.py` | `Opportunity` table (id, title, account_id FK NOT NULL, contact_id FK nullable, stage ENUM default 'prospecting', value NUMERIC CHECK >0, probability SMALLINT CHECK 0-100, expected_close_date, timestamps) |
| `schemas/opportunity.py` | `OpportunityCreate { title, account_id, contact_id?, stage?, value?, probability?, expected_close_date? }` with a Pydantic field validator rejecting `value <= 0` and `probability` outside 0–100; `OpportunityUpdate`, `OpportunityResponse` |
| `services/opportunity_service.py` | Defaults `stage` to `prospecting` when omitted; validates `account_id` exists (Accounts), `contact_id` exists if provided (Contacts); filter by `stage`/`account_id`/`contact_id`; sort by `value`/`expected_close_date`/`created_at` |
| `routers/opportunities.py` | `GET /opportunities`, `POST /opportunities`, `GET /opportunities/{id}`, `PATCH /opportunities/{id}`, `DELETE /opportunities/{id}` |
| Frontend `/opportunities` page | Board (Kanban, 5 columns) / table toggle (session-persisted); filters: stage, account, contact |
| Frontend `/opportunities/:id` detail page | `DetailHeader`, stage/value/probability/close-date display, linked Activities list + "Log activity" button |

## Data Flow Within the Module

```
[User submits OpportunityForm: title, account_id, ...]
   → POST /opportunities
   → [opportunity_service: validate account_id exists — calls Accounts]
   → [opportunity_service: if contact_id provided, validate exists — calls Contacts]
   → [Pydantic schema: reject value<=0, probability outside 0-100 — 422 before reaching the service]
   → [opportunity_service: stage = stage or 'prospecting']
   → INSERT opportunities row → OpportunityResponse

[User changes a deal's stage on the board]
   → PATCH /opportunities/{id} {stage: "proposal"}
   → [opportunity_service: UPDATE stage — no sequence check, any stage to any stage allowed]
   → OpportunityResponse → frontend moves the card to the new column, optimistic update reverted on failure

[Manager filters the pipeline]
   → GET /opportunities?stage=proposal&account_id=&sort_by=value&sort_dir=desc
   → [opportunity_service: WHERE clauses + ORDER BY + LIMIT/OFFSET]
   → PaginatedResponse[OpportunityResponse]
```

## Integration Points with Other Modules

| Module | Integration Point |
|---|---|
| [Accounts](../accounts/plan.md) | `opportunity_service` validates `account_id` on every write; Account detail page's "Opportunities" tab reads `GET /opportunities?account_id=`; this module's delete-guard read is consumed *by* Accounts (Accounts queries this table, not the reverse) |
| [Contacts](../contacts/plan.md) | Same validation pattern for the optional `contact_id`; the Opportunity form's Contact dropdown is scoped to the selected Account via `GET /contacts?account_id=` |
| [Leads](../leads/plan.md) | Leads' conversion transaction performs a direct `INSERT` into `opportunities` (title auto-generated from the lead's name, `account_id`/`contact_id` from the resolved Account/Contact, `stage='prospecting'`) — the third leg of the documented cross-module write exception |
| [Activities](../activities/plan.md) | Activities resolves `opportunity_id` to a display title via this module; the Opportunity detail page reads `GET /activities?opportunity_id=` for its activity list |
| Dashboard (frontend, cross-cutting) | Open Pipeline Value, Win Rate, and Pipeline-by-Stage chart all aggregate over this module's `GET /opportunities` data |

---

## Architectural Decisions Specific to This Module

- **Non-linear stage transitions, enforced nowhere**: unlike Leads' strict state machine, any stage may move to any other stage — reps need to skip or revisit stages in practice, so no transition table exists for this module.
- **Value/probability validation at the Pydantic layer, not the service layer**: these are stateless field-level rules (no "current value" context needed), so they belong in the schema's validators, keeping the service layer focused on FK validation and querying.
