# Module Specification: Activities

**Module**: `activities` | **Created**: 2026-06-16 | **Status**: Draft

---

## Module Scope & Objectives

Activities owns the logged-interaction history (calls, emails, meetings) between the sales team and customers. Every Activity must link to at least one of a [Contact](../contacts/spec.md) or an [Opportunity](../opportunities/spec.md), and records its creating [User](../users/spec.md) for ownership scoping — the same pattern as [Leads](../leads/spec.md).

**In scope**: Activity CRUD, the link-required validation (at least one of `contact_id`/`opportunity_id`), type/contact/opportunity filtering, and record-level ownership scoping (`manage-own` vs `manage-all`).

**Out of scope**: actual email sending (handled by the platform's separate Mock Email utility, not part of this module's 9-module scope), calendar/meeting invite integration.

**Objective**: Provide a complete, queryable engagement history per Contact and per Opportunity, with no orphaned (unlinked) activity ever persisted.

---

## User Stories

### User Story 8 - Activity Logging (Priority: P5)

Sales reps must log every interaction against a Contact or Opportunity so the team has a complete history of customer engagement, viewable as a unified timeline.

**Why this priority**: Activity history is essential for team handoffs and accountability, but is only useful once Contacts and Opportunities exist. Depends on RBAC for Sales Rep ownership scoping.

**Independent Test**: Log activities of all three types linked to a Contact, log activities linked to an Opportunity, attempt to log an activity with no linked entity and confirm rejection, retrieve activity history filtered by type or linked record.

**Acceptance Scenarios**:

1. **Given** a Contact exists, **When** a user logs a "call" activity with a subject and date, **Then** the activity is saved and linked to that Contact with `created_by` set to the logging user.
2. **Given** an Opportunity exists, **When** a user logs a "meeting" activity linked to that Opportunity, **Then** the activity is saved with the opportunity link.
3. **Given** no contact or opportunity ID is provided, **When** a user attempts to log an activity, **Then** the request is rejected with an error stating that at least one linked entity is required.
4. **Given** multiple activities exist, **When** a user filters activities by type "email", **Then** only email activities are returned.
5. **Given** a Sales Rep, **When** they attempt to edit or delete an activity logged by a different user, **Then** the request is rejected with 403.

### Edge Cases

- What happens when an activity is linked to both a contact and an opportunity simultaneously? → Allowed and supported.
- What happens when an Activity's linked Contact or Opportunity is deleted while the other link is still set? → The deleted side's FK is set to NULL (`ON DELETE SET NULL`); the Activity survives as long as at least one link remains, or even with both NULL after the fact (the CHECK constraint is enforced at write-time, not retroactively re-validated on a cascading FK nullification).

---

## Functional Requirements

- **FR-ACT-001**: System MUST allow creation of an Activity with type (call, email, or meeting — required), subject (required), and at least one of: Contact ID or Opportunity ID. The creating User is recorded as `created_by`.
- **FR-ACT-002**: System MUST reject Activity creation if neither a valid Contact ID nor a valid Opportunity ID is provided.
- **FR-ACT-003**: System MUST allow an Activity to be simultaneously linked to both a Contact and an Opportunity.
- **FR-ACT-004**: System MUST allow optional fields on Activities: notes, and activity date (defaults to time of creation if omitted).
- **FR-ACT-005**: System MUST allow retrieval of a paginated, sortable list of Activities, with optional filtering by type, Contact ID, or Opportunity ID.
- **FR-ACT-006**: System MUST allow retrieval, update, and deletion of a single Activity by ID, subject to the same ownership restriction pattern as Leads (`activities:manage-own` vs `activities:manage-all`).

## Key Entities

- **Activity**: A logged interaction. Key attributes: type (call/email/meeting), subject, notes, activity date (defaults to now), linked Contact (nullable), linked Opportunity (nullable, at least one required), `created_by` (User FK).

---

## Success Criteria

- **SC-ACT-001**: 100% of Activity submissions without a valid linked Contact or Opportunity are rejected; no orphaned activity can be saved.
- **SC-ACT-002**: 100% of ownership-violating update/delete attempts by a Sales Rep on a non-owned Activity are rejected with 403.

---

## Dependencies on Other Modules

| Dependency | Direction | Reason |
|---|---|---|
| [Contacts](../contacts/spec.md) | Activities **depends on** Contacts (optional, link-required-in-combination) | `activities.contact_id` is a nullable FK |
| [Opportunities](../opportunities/spec.md) | Activities **depends on** Opportunities (optional, link-required-in-combination) | `activities.opportunity_id` is a nullable FK |
| [Users](../users/spec.md) | Activities **depends on** Users | `created_by` FK; ownership-scoping logic |
| [Roles](../roles/spec.md), [Permissions](../permissions/spec.md) | Activities **depends on** (enforcement) | `activities:manage-own` vs `activities:manage-all` |

**Build order implication**: Activities is the last module that can be fully built — it requires Contacts, Opportunities, and Users all to exist first. It has no module depending on it in return (terminal/leaf module).
