# Module Specification: Opportunities

**Module**: `opportunities` | **Created**: 2026-06-16 | **Status**: Draft

---

## Module Scope & Objectives

Opportunities owns the record of qualified sales deals actively being pursued — the revenue-tracking core of the CRM. Every Opportunity is required to link to an [Account](../accounts/spec.md) and may optionally link to a [Contact](../contacts/spec.md). [Leads](../leads/spec.md) conversion creates new Opportunity rows, and [Activities](../activities/spec.md) may link to an Opportunity.

**In scope**: Opportunity CRUD, stage management (5-stage non-linear pipeline), value/probability validation, board (Kanban) and flat-table presentation support, filtering by stage/account/contact.

**Out of scope**: any per-record ownership restriction (role-gated only, like Accounts/Contacts); revenue forecasting/reporting beyond what the Dashboard already aggregates from this module's data.

**Objective**: Give sales managers an accurate, filterable view of every deal's stage and value, with validation that prevents nonsensical states (zero/negative value, out-of-range probability) from ever being persisted.

---

## User Stories

### User Story 7 - Opportunity Pipeline Management (Priority: P4)

A sales manager needs to track all active deals, their current stage, and their monetary value to forecast revenue and manage the team's pipeline, viewed either as a Kanban board grouped by stage or as a flat sortable table.

**Why this priority**: Opportunities represent real revenue. Depends on Accounts and Contacts existing.

**Independent Test**: Create opportunities with values and stages, update stages through the pipeline, filter by stage/account/contact, and verify that negative or zero values are rejected.

**Acceptance Scenarios**:

1. **Given** an Account exists, **When** a user creates an Opportunity with a title, stage, and value of $5,000, **Then** the opportunity is saved and returned.
2. **Given** an Opportunity exists, **When** a user submits a value update of $0 or a negative number, **Then** the update is rejected with a clear validation error.
3. **Given** multiple opportunities exist in different stages, **When** a manager filters by stage "proposal", **Then** only opportunities in that stage are returned.
4. **Given** an Opportunity in "negotiation", **When** a user marks it "closed-won", **Then** the stage is updated and the record reflects the final state.
5. **Given** the pipeline board, **When** a user changes a deal's stage using the inline control, **Then** the card moves to the correct column without a full page reload, and the column total updates.

### Edge Cases

- What happens when an opportunity's expected close date is in the past? → Allowed (legacy/backfilled data); no validation error.
- What happens to an Opportunity if its linked Contact is deleted? → `contact_id` is set to NULL (`ON DELETE SET NULL`); the deal survives, shown as having no linked contact.

---

## Functional Requirements

- **FR-OPP-001**: System MUST allow creation of an Opportunity with a title (required) and an associated Account ID (required); optional fields include Contact ID, stage, value in USD, probability (0–100%), and expected close date.
- **FR-OPP-002**: System MUST default new Opportunities to stage "prospecting" if no stage is provided.
- **FR-OPP-003**: System MUST enforce that Opportunity value, when provided, is a number strictly greater than zero.
- **FR-OPP-004**: System MUST allow Opportunity stage updates to any of the five defined stages without enforcing strict sequential progression.
- **FR-OPP-005**: System MUST allow retrieval of a paginated, sortable list of Opportunities, with optional filtering by stage, Account ID, or Contact ID, and offer both a board (grouped-by-stage) and flat-table presentation.
- **FR-OPP-006**: System MUST allow retrieval, update, and deletion of a single Opportunity by ID. Only Roles with `opportunities:delete` permission (Admin, Manager by default) MAY delete Opportunities.

## Key Entities

- **Opportunity**: A qualified sales deal actively being pursued. Key attributes: title, linked Account (required), linked Contact (optional), stage (5 values), value (USD, nullable, >0 if set), probability (0–100, nullable), expected close date (nullable).

---

## Success Criteria

- **SC-OPP-001**: 100% of Opportunity value submissions that are zero or negative are rejected before persistence.
- **SC-OPP-002**: The pipeline board correctly reflects all 5 opportunity stages at all times — records never appear in the wrong column.
- **SC-OPP-003**: Full CRUD and filtering are independently verifiable and correctly permission-gated.

---

## Dependencies on Other Modules

| Dependency | Direction | Reason |
|---|---|---|
| [Accounts](../accounts/spec.md) | Opportunities **depends on** Accounts (required) | `opportunities.account_id` is a required FK |
| [Contacts](../contacts/spec.md) | Opportunities **depends on** Contacts (optional) | `opportunities.contact_id` is a nullable FK |
| [Authentication](../authentication/spec.md), [Roles](../roles/spec.md), [Permissions](../permissions/spec.md) | Opportunities **depends on** (enforcement only) | Standard Bearer + `opportunities:*` permission gating |
| [Leads](../leads/spec.md) | **Depended on by** Leads | Lead conversion creates a new Opportunity row directly |
| [Activities](../activities/spec.md) | **Depended on by** Activities | `activities.opportunity_id` is a nullable FK into this module's table |

**Build order implication**: Opportunities must be built after Accounts (hard dependency) and ideally alongside or after Contacts (soft dependency), and **before** Leads (which depends on it for conversion).
