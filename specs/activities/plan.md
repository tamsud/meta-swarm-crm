# Module Plan: Activities

**Module**: `activities` | **Spec**: [spec.md](spec.md)

---

## Module Architecture

Standard four-layer structure, with the link-required validation enforced redundantly at both the schema/service layer (primary, human-readable error) and the database (CHECK constraint, safety net) — and the same ownership-scoping pattern as Leads.

```
routers/activities.py        → /activities CRUD, permission-gated
services/activity_service.py → link-required validation, ownership filter, filter/sort/paginate
schemas/activity.py          → ActivityCreate, ActivityUpdate, ActivityResponse
models/activity.py           → Activity ORM model + ActivityType enum
```

## Components and Responsibilities

| Component | Responsibility |
|---|---|
| `models/activity.py` | `Activity` table (id, type ENUM, subject, notes, activity_date default now(), contact_id FK nullable, opportunity_id FK nullable, created_by_user_id FK nullable, timestamps); table-level `CHECK (contact_id IS NOT NULL OR opportunity_id IS NOT NULL)` |
| `schemas/activity.py` | `ActivityCreate { type, subject, notes?, activity_date?, contact_id?, opportunity_id? }` with a Pydantic model validator rejecting the case where both link fields are null; `ActivityUpdate`, `ActivityResponse` |
| `services/activity_service.py` — link validation | Pydantic validator is the primary enforcement (produces `ACTIVITY_NO_LINK` 400 before any DB write); the DB CHECK constraint is the safety net for any future direct-DB-write code path |
| `services/activity_service.py` — ownership filter | Identical pattern to Leads: `activities:manage-all` → no filter; `activities:manage-own` → `created_by_user_id == current_user.id` required, else 403 |
| `routers/activities.py` | `GET /activities`, `POST /activities`, `GET /activities/{id}`, `PATCH /activities/{id}`, `DELETE /activities/{id}` |
| Frontend `/activities` page | Unified timeline, type/contact/opportunity filters, type icons (phone/envelope/calendar) |
| Frontend Contact detail "History" tab, Opportunity detail activity list | Both consume `GET /activities?contact_id=` / `?opportunity_id=` from this module |

## Data Flow Within the Module

```
[User submits ActivityForm]
   → POST /activities
   → [Pydantic validator: contact_id is None AND opportunity_id is None?] → if true: 400 ACTIVITY_NO_LINK (no DB call made)
   → [activity_service: if contact_id provided, validate exists — calls Contacts]
   → [activity_service: if opportunity_id provided, validate exists — calls Opportunities]
   → [activity_service: created_by_user_id = current_user.id; activity_date = activity_date or now()]
   → INSERT activities row → ActivityResponse

[Contact detail page "History" tab loads]
   → GET /activities?contact_id={id}&sort_by=activity_date&sort_dir=desc
   → [activity_service: WHERE contact_id = ? ORDER BY activity_date DESC]
   → PaginatedResponse[ActivityResponse] → rendered as ActivityTimeline
```

## Integration Points with Other Modules

| Module | Integration Point |
|---|---|
| [Contacts](../contacts/plan.md) | `activity_service` validates `contact_id` exists; Contact detail page's Overview ("days since last contact") and History tabs both read from this module |
| [Opportunities](../opportunities/plan.md) | Same pattern for `opportunity_id`; Opportunity detail page's activity list reads from this module |
| [Users](../users/plan.md) | `created_by_user_id` set from `current_user.id`; ownership-filter logic compares against it |
| [Roles](../roles/plan.md) / [Permissions](../permissions/plan.md) | `activities:manage-own` / `activities:manage-all` permission codes |
| Dashboard (frontend, cross-cutting) | The "5 most recent activities" feed reads `GET /activities?sort_by=activity_date&sort_dir=desc&size=5` |

---

## Architectural Decisions Specific to This Module

- **Belt-and-suspenders link validation**: Pydantic validator (primary, friendly error) + DB CHECK constraint (safety net) — identical pattern to the reference implementation's original Activity entity, carried over unchanged since the requirement is unchanged.
- **Ownership scoping implemented identically to Leads**: deliberately duplicated logic (not abstracted into a shared "ownable resource" base class in this documentation) to keep each module's service layer independently readable; a future refactor could extract a shared mixin once both modules' behavior has stabilized in production.
