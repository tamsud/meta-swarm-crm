# Module Specification: Accounts

**Module**: `accounts` | **Created**: 2026-06-16 | **Status**: Draft

---

## Module Scope & Objectives

Accounts owns the master record of companies/organizations that are current or potential customers. It is the root CRM data entity — [Contacts](../contacts/spec.md) and [Opportunities](../opportunities/spec.md) both reference it, and [Leads](../leads/spec.md) conversion creates or reuses Account rows.

**In scope**: Account CRUD, search by name, and the dependency-aware deletion guard (blocking delete when Contacts or Opportunities still reference the account).

**Out of scope**: any per-record ownership restriction (Accounts are governed by role-level permissions only, unlike Leads/Activities — see [Roles](../roles/spec.md)).

**Objective**: Provide a reliable, searchable parent record for every Contact and Opportunity, with no orphaned-reference risk on deletion.

---

## User Stories

### User Story 4 (Accounts portion) - Account Management (Priority: P2)

A sales rep needs to maintain a master record of the companies they sell to. Without this foundation, no other CRM workflow (Leads conversion, Opportunities, Activities) is possible.

**Why this priority**: All CRM entities depend on Accounts existing first. Depends only on Authentication/RBAC being in place.

**Independent Test**: Create an Account, verify it's searchable and retrievable; attempt to delete it while a Contact/Opportunity references it (blocked); delete it once unreferenced (succeeds).

**Acceptance Scenarios**:

1. **Given** no accounts exist, **When** a user with `accounts:create` permission submits a new account with a name, **Then** the account is created and returned with a system-assigned ID and creation timestamp.
2. **Given** an account has associated contacts or opportunities, **When** a user attempts to delete the account, **Then** the deletion is rejected with a descriptive error listing the dependency counts.
3. **Given** an account has no contacts or opportunities, **When** a user with `accounts:delete` permission deletes it, **Then** the account is permanently removed.
4. **Given** the accounts list, **When** a user searches by partial name, **Then** only matching accounts are returned (case-insensitive).
5. **Given** a Sales Rep, **When** they attempt to delete any account, **Then** the request is rejected with 403 regardless of frontend state.

### Edge Cases

- What happens if an account is referenced by both an open opportunity and has contacts? → Deletion is blocked, listing both dependency counts in one error.
- What happens to a Contact's `account_id` if the account were ever deleted (after dependents are cleared)? → N/A by definition — deletion is blocked while any Contact references it; once a Contact is itself deleted or reassigned, the Account becomes deletable.

---

## Functional Requirements

- **FR-ACCT-001**: System MUST allow creation of an Account with at minimum a name field (required); optional fields include industry, website, phone, and address.
- **FR-ACCT-002**: System MUST allow retrieval of a paginated, searchable (by name, case-insensitive partial match), sortable list of Accounts.
- **FR-ACCT-003**: System MUST allow retrieval, update, and deletion of a single Account by ID.
- **FR-ACCT-004**: System MUST prevent deletion of an Account that has associated Contacts or Opportunities, returning a descriptive error listing both dependency counts.
- **FR-ACCT-005**: Only Roles with `accounts:delete` permission (Admin, Manager by default) MAY delete Accounts; all authenticated Users with `accounts:read` permission may view them.

## Key Entities

- **Account**: A company or organization that is a current or potential customer. Key attributes: name, industry, website, phone, address.

---

## Success Criteria

- **SC-ACCT-001**: Attempting to delete an Account with associated Contacts or Opportunities is blocked in 100% of cases with a human-readable error.
- **SC-ACCT-002**: List endpoint returns paginated results for datasets up to 10,000 records within 3 seconds under normal load.
- **SC-ACCT-003**: Full CRUD is independently verifiable and correctly permission-gated.

---

## Dependencies on Other Modules

| Dependency | Direction | Reason |
|---|---|---|
| [Authentication](../authentication/spec.md), [Roles](../roles/spec.md), [Permissions](../permissions/spec.md) | Accounts **depends on** (for enforcement only) | Every endpoint requires a valid Bearer token and the relevant `accounts:*` permission |
| [Contacts](../contacts/spec.md) | **Depended on by** Contacts | `contacts.account_id` is a nullable FK into this module's table |
| [Opportunities](../opportunities/spec.md) | **Depended on by** Opportunities | `opportunities.account_id` is a required FK into this module's table |
| [Leads](../leads/spec.md) | **Depended on by** Leads | Lead conversion creates or reuses an Account row by case-insensitive name match |

**Build order implication**: Accounts has no CRM-data dependency (only the cross-cutting Authentication/RBAC dependency) and can be built in parallel with [Permissions](../permissions/spec.md) at the very start of implementation.
