# Module Specification: Leads

**Module**: `leads` | **Created**: 2026-06-16 | **Status**: Draft

---

## Module Scope & Objectives

Leads owns the top-of-funnel record of unqualified potential customer inquiries, their progression through a strict status state machine, and the atomic conversion operation that creates an [Opportunity](../opportunities/spec.md) (and, as needed, an [Account](../accounts/spec.md)/[Contact](../contacts/spec.md)) from a qualified Lead. Leads is the most cross-cutting module in the system — it depends on Accounts, Contacts, Opportunities, and [Users](../users/spec.md).

**In scope**: Lead CRUD, the 4-state status machine (`new → contacted → qualified → lost`, with `lost` terminal), the atomic conversion transaction, and record-level ownership scoping (`manage-own` vs `manage-all`).

**Out of scope**: lead scoring/qualification automation, duplicate-lead detection beyond the explicit non-uniqueness of Lead email (a person may submit multiple enquiries).

**Objective**: Provide a reliable, auditable funnel from first inquiry to qualified deal, with conversion guaranteed to be all-or-nothing and never reachable in an invalid status.

---

## User Stories

### User Story 5 - Lead Capture & Status Progression (Priority: P2)

A sales rep receives enquiries from potential customers who haven't been qualified yet. They need to capture these leads and track progression through outreach stages.

**Why this priority**: Leads are the top of the sales funnel. Depends on Accounts/Contacts/Opportunities existing as conversion targets, and on RBAC for Sales Rep ownership scoping.

**Independent Test**: Create leads, change their statuses through valid transitions, attempt invalid transitions and confirm rejection, retrieve leads filtered/searched by status/name/company.

**Acceptance Scenarios**:

1. **Given** no leads exist, **When** a user submits a lead with a name and email, **Then** the lead is created with a default status of "new" and `created_by` set to the submitting user.
2. **Given** a lead with status "new", **When** a user updates the status to "contacted", **Then** the transition is accepted and saved.
3. **Given** a lead with status "contacted", **When** a user updates the status back to "new", **Then** the update is rejected with a clear error describing valid transitions.
4. **Given** a lead with status "qualified", **When** a user updates the status to "lost", **Then** the transition is accepted.
5. **Given** a lead with status "lost", **When** a user attempts any status change, **Then** the update is rejected.
6. **Given** a Sales Rep, **When** they attempt to edit or delete a lead created by a different Sales Rep, **Then** the request is rejected with 403.
7. **Given** a Manager or Admin, **When** they edit any lead regardless of creator, **Then** the request succeeds.

### User Story 6 - Lead-to-Opportunity Conversion (Priority: P3)

Once a lead is qualified, a sales rep converts it into an active sales Opportunity in a single atomic action.

**Why this priority**: Conversion is the critical handoff from lead generation to active selling, and depends on Leads, Accounts, Contacts, and Opportunities all being defined.

**Independent Test**: Convert a qualified lead and verify an Opportunity is created, and that corresponding Contact/Account records are either created or reused if they already exist.

**Acceptance Scenarios**:

1. **Given** a lead with status "qualified", **When** a user triggers conversion, **Then** a new Opportunity is created, the lead's company becomes an Account (or reuses an existing one), and the lead's personal data becomes a Contact.
2. **Given** a lead with status "new" or "contacted", **When** a user attempts conversion, **Then** the request is rejected with an error indicating the lead must be qualified first.
3. **Given** a lead whose company name matches an existing Account (case-insensitive), **When** conversion occurs, **Then** the existing Account is reused and no duplicate is created.
4. **Given** a lead that has already been converted, **When** conversion is attempted again, **Then** the request is rejected with a 400 error whose detail includes the existing `converted_opportunity_id`.

### Edge Cases

- What happens when a lead is converted but the associated contact email already exists as a Contact record? → The existing Contact is reused; no duplicate created.
- What happens when a lead's company name matches an existing Account case-insensitively but with different capitalization? → Treated as the same Account; reused, not duplicated.

---

## Functional Requirements

- **FR-LEAD-001**: System MUST allow creation of a Lead with first name, last name, and email (all required); optional fields include phone, company name, lead source, and notes. Lead email addresses are NOT required to be unique.
- **FR-LEAD-002**: System MUST assign a default status of "new" to all newly created Leads and MUST record the creating User as `created_by`.
- **FR-LEAD-003**: System MUST enforce the following valid Lead status transitions only: `new → contacted`; `contacted → qualified`; `new`, `contacted`, or `qualified` → `lost`. All other transitions (including any transition away from `lost`) MUST be rejected with a descriptive error.
- **FR-LEAD-004**: System MUST allow retrieval of a paginated, searchable (name/email/company), sortable list of Leads, with optional filtering by status.
- **FR-LEAD-005**: System MUST allow retrieval, update, and deletion of a single Lead by ID, subject to ownership restriction: Users holding only `leads:manage-own` (Sales Rep default) may update/delete only Leads where `created_by` equals their own User ID; Users holding `leads:manage-all` (Admin/Manager default) may act on any Lead.
- **FR-LEAD-006**: System MUST provide a dedicated Lead conversion operation that: requires status "qualified" (rejects otherwise); rejects conversion if already converted, returning the existing `converted_opportunity_id` in the error body; creates a new Opportunity; creates or reuses an Account by case-insensitive company-name match; creates or reuses a Contact by email match — all within a single atomic transaction.

## Key Entities

- **Lead**: An unqualified potential customer inquiry. Key attributes: first name, last name, email (not unique), phone, company, status (4-value state machine), source, notes, `converted_opportunity_id`, `created_by` (User FK).

---

## Success Criteria

- **SC-LEAD-001**: 100% of Lead status transitions that violate the defined state machine are rejected; no invalid state is ever persisted.
- **SC-LEAD-002**: A qualified Lead can be converted to an Opportunity, Contact, and Account in a single operation without the caller making additional API calls.
- **SC-LEAD-003**: 100% of ownership-violating update/delete attempts by a Sales Rep on a non-owned Lead are rejected with 403.

---

## Dependencies on Other Modules

| Dependency | Direction | Reason |
|---|---|---|
| [Accounts](../accounts/spec.md) | Leads **depends on** Accounts | Conversion creates/reuses an Account row |
| [Contacts](../contacts/spec.md) | Leads **depends on** Contacts | Conversion creates/reuses a Contact row |
| [Opportunities](../opportunities/spec.md) | Leads **depends on** Opportunities | Conversion creates a new Opportunity row |
| [Users](../users/spec.md) | Leads **depends on** Users | `created_by` FK; ownership-scoping logic compares against `current_user.id` |
| [Roles](../roles/spec.md), [Permissions](../permissions/spec.md) | Leads **depends on** (enforcement) | `leads:manage-own` vs `leads:manage-all` permission distinction |

**Build order implication**: Leads is the most cross-cutting CRM data module and should be built **last** among the data modules — only after Accounts, Contacts, Opportunities, and Users are all stable.
