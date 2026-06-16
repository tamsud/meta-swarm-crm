# Module Plan: Leads

**Module**: `leads` | **Spec**: [spec.md](spec.md)

---

## Module Architecture

Standard four-layer structure, plus two pieces of business logic dense enough to warrant their own internal components: the status state machine and the conversion transaction.

```
routers/leads.py        → /leads CRUD + POST /leads/{id}/convert
services/lead_service.py → state machine validation, ownership filter, conversion orchestration
schemas/lead.py          → LeadCreate, LeadUpdate, LeadResponse
models/lead.py           → Lead ORM model + LeadStatus enum
```

## Components and Responsibilities

| Component | Responsibility |
|---|---|
| `models/lead.py` | `Lead` table (id, first_name, last_name, email, phone, company, status ENUM default 'new', source, notes, converted_opportunity_id FK nullable, created_by_user_id FK nullable, timestamps) |
| `schemas/lead.py` | `LeadCreate`, `LeadUpdate`, `LeadResponse` |
| `services/lead_service.py` — state machine | `VALID_TRANSITIONS = {new: [contacted, lost], contacted: [qualified, lost], qualified: [lost], lost: []}`; validates any `status` field in an update against this table before persisting |
| `services/lead_service.py` — ownership filter | On update/delete, checks caller's effective permissions: if `leads:manage-all` present, no filter; elif `leads:manage-own` present, require `lead.created_by_user_id == current_user.id` else 403 |
| `services/lead_service.py` — conversion orchestration | Single DB transaction: validate status == qualified and not already converted → find-or-create Account → find-or-create Contact → create Opportunity → update Lead.converted_opportunity_id → commit |
| `routers/leads.py` | `GET /leads`, `POST /leads`, `GET /leads/{id}`, `PATCH /leads/{id}`, `DELETE /leads/{id}`, `POST /leads/{id}/convert` |
| Frontend `/leads` page | Status filter tabs, search, `LeadStatusControl` (valid-transitions-only), Convert button + Converted badge |

## Data Flow Within the Module

```
[User creates a Lead]
   → POST /leads → [lead_service: status='new', created_by_user_id=current_user.id] → INSERT → LeadResponse

[User attempts a status change]
   → PATCH /leads/{id} {status: "qualified"}
   → [lead_service: ownership check] → [lead_service: VALID_TRANSITIONS[current.status] must contain "qualified"]
   → if not: 400 INVALID_LEAD_TRANSITION (detail names the rejected transition)
   → else: UPDATE leads SET status → LeadResponse

[User triggers conversion]
   → POST /leads/{id}/convert
   → BEGIN TRANSACTION
   → [lead_service: load lead; assert status == 'qualified' else 400 LEAD_NOT_QUALIFIED]
   → [lead_service: assert converted_opportunity_id IS NULL else 400 LEAD_ALREADY_CONVERTED (include existing id)]
   → [calls into Accounts: find-by-name-ci(lead.company) or create]
   → [calls into Contacts: find-by-email(lead.email) or create]
   → [calls into Opportunities: create(title=..., account_id=, contact_id=, stage='prospecting')]
   → [UPDATE leads SET converted_opportunity_id = opportunity.id]
   → COMMIT (or ROLLBACK entirely on any step's failure)
   → 201 OpportunityResponse
```

## Integration Points with Other Modules

| Module | Integration Point |
|---|---|
| [Accounts](../accounts/plan.md) | Conversion calls Accounts' "find by case-insensitive name or create" function, inside the Leads-owned transaction (the documented cross-module write exception) |
| [Contacts](../contacts/plan.md) | Conversion calls Contacts' "find by email or create" function, same transaction |
| [Opportunities](../opportunities/plan.md) | Conversion calls Opportunities' "create" function, same transaction; the returned `OpportunityResponse` is what the conversion endpoint sends back to the caller |
| [Users](../users/plan.md) | `created_by_user_id` is set from `current_user.id` on create; ownership-filter logic compares against it on every update/delete |
| [Roles](../roles/plan.md) / [Permissions](../permissions/plan.md) | `leads:manage-own` and `leads:manage-all` are permission codes from the catalogue, bundled differently into the Sales Rep vs. Admin/Manager system roles |

---

## Architectural Decisions Specific to This Module

- **Conversion as a single Leads-owned transaction, not 3 separate API calls**: guarantees all-or-nothing semantics (SC-LEAD-002); the alternative (frontend orchestrating 3 calls) risks partial state on a mid-sequence failure.
- **State machine as a static lookup table in the service layer**: simpler and more testable than DB triggers or CHECK constraints, and produces a human-readable rejection message naming the invalid transition.
- **Ownership check colocated with permission check, not a separate middleware layer**: because "own vs all" is data-dependent (requires loading the target row first), it cannot be resolved purely from the JWT claims the way `require_permission` can — it is necessarily a two-step check inside the service function.
