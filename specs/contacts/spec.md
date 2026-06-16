# Module Specification: Contacts

**Module**: `contacts` | **Created**: 2026-06-16 | **Status**: Draft

---

## Module Scope & Objectives

Contacts owns the master record of individual people associated with an [Account](../accounts/spec.md) — the primary point of human interaction in the sales process. [Opportunities](../opportunities/spec.md) and [Activities](../activities/spec.md) both optionally reference a Contact, and [Leads](../leads/spec.md) conversion creates or reuses Contact rows.

**In scope**: Contact CRUD, system-wide email uniqueness enforcement, search/filter (by name/email, by Account), and the CRM-pattern detail page layout (header + profile sidebar + tabs).

**Out of scope**: any per-record ownership restriction (governed by role-level permissions only, like Accounts).

**Objective**: Provide a reliable, de-duplicated (by email) address book entry point that every downstream engagement record (Opportunity, Activity) can link to.

---

## User Stories

### User Story 4 (Contacts portion) - Contact Management (Priority: P2)

A sales rep needs to maintain individuals they deal with at each Account.

**Why this priority**: Opportunities and Activities reference Contacts; Lead conversion creates them. Depends on Accounts existing (optional FK) and on Authentication/RBAC.

**Independent Test**: Create a Contact linked to an Account, update it, verify retrieval; attempt to create a second Contact with the same email (rejected); search by partial name/email.

**Acceptance Scenarios**:

1. **Given** an account exists, **When** a user creates a contact with that account's ID, **Then** the contact is saved and retrievable, showing the linked account.
2. **Given** a contact exists, **When** a user updates the contact's phone number, **Then** the updated record is returned and the change is persisted.
3. **Given** a contact with a given email already exists, **When** a user attempts to create or update another contact to use that same email, **Then** the request is rejected with 409.
4. **Given** the contacts list, **When** a user applies the account filter, **Then** only contacts belonging to that account are shown.

### Edge Cases

- What happens when a contact's email conflicts with an existing contact's email? → Rejected with `409 EMAIL_CONFLICT`.
- What happens when a Contact's linked Account is deleted? → Cannot occur — Accounts blocks its own deletion while Contacts reference it (see [Accounts module](../accounts/spec.md) FR-ACCT-004). If a Contact's `account_id` is explicitly cleared first, the Contact survives with `account_id = null` (`ON DELETE SET NULL` is the schema-level safety net, not the primary path).

---

## Functional Requirements

- **FR-CONT-001**: System MUST allow creation of a Contact with first name, last name, and email (all required); optional fields include phone, job title, and account association.
- **FR-CONT-002**: System MUST enforce email uniqueness across all Contacts, returning 409 on conflict.
- **FR-CONT-003**: System MUST allow retrieval of a paginated, searchable (by name/email, case-insensitive partial match), sortable list of Contacts, with optional filtering by Account ID.
- **FR-CONT-004**: System MUST allow retrieval, update, and deletion of a single Contact by ID.

## Key Entities

- **Contact**: An individual person associated with an Account. Key attributes: first name, last name, email (unique), phone, job title, linked Account (nullable).

---

## Success Criteria

- **SC-CONT-001**: 100% of duplicate-email Contact submissions are rejected before persistence.
- **SC-CONT-002**: Full CRUD, search, and account-filter are independently verifiable.

---

## Dependencies on Other Modules

| Dependency | Direction | Reason |
|---|---|---|
| [Accounts](../accounts/spec.md) | Contacts **depends on** Accounts (optional) | `contacts.account_id` is a nullable FK |
| [Authentication](../authentication/spec.md), [Roles](../roles/spec.md), [Permissions](../permissions/spec.md) | Contacts **depends on** (enforcement only) | Standard Bearer + `contacts:*` permission gating |
| [Opportunities](../opportunities/spec.md) | **Depended on by** Opportunities | `opportunities.contact_id` is a nullable FK into this module's table |
| [Activities](../activities/spec.md) | **Depended on by** Activities | `activities.contact_id` is a nullable FK into this module's table |
| [Leads](../leads/spec.md) | **Depended on by** Leads | Lead conversion creates or reuses a Contact row by email match |

**Build order implication**: Contacts should be built immediately after Accounts (its only CRM-data dependency, and only an optional one) — it can proceed in parallel with Opportunities since neither blocks the other.
