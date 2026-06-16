# Module Specification: Users

**Module**: `users` | **Created**: 2026-06-16 | **Status**: Draft

---

## Module Scope & Objectives

Users owns the `users` table — every account holder in the system, their hashed credentials, display name, assigned Role, and active/deactivated status. It is the identity record that [Authentication](../authentication/spec.md) verifies against and that [Leads](../leads/spec.md)/[Activities](../activities/spec.md) reference via `created_by_user_id`.

**In scope**: User CRUD (Admin-only for other users; self-service for one's own display name), the "last active Admin" lockout invariant, deactivation (soft, never hard-deleted), and the seed-user bootstrap (admin@crm.local, manager@crm.local, sales@crm.local).

**Out of scope**: password reset flows, email verification, user self-registration (all users are created by an Admin in v1).

**Objective**: Ensure every other module's "who did this" and "who may do this" questions resolve to a real, correctly-roled, active User record, and that the system can never end up with zero usable Admin accounts.

---

## User Stories

### User Story 3 - User Management (Priority: P1)

Administrators can create new users, assign them a role, update their profile and role, and deactivate or reactivate them. Every authenticated user can view and update their own profile (display name) from a self-service profile page.

**Why this priority**: User accounts are the subject of authentication and the carrier of role/permission assignment.

**Independent Test**: Log in as Admin → open Users → create a new user with a role → the new user can log in immediately → Admin deactivates the user → that user's next login attempt is rejected with 401 → Admin reactivates the user → login succeeds again.

**Acceptance Scenarios**:

1. **Given** an Admin on the Users page, **When** they submit a create-user form with email, password, display name, and role, **Then** a new user is created and appears in the list immediately.
2. **Given** an Admin, **When** they update a user's role, **Then** that user's next authenticated request reflects the new role's permissions.
3. **Given** an Admin, **When** they deactivate a user, **Then** that user's next login attempt returns 401.
4. **Given** a non-Admin user, **When** they attempt to access user management pages or APIs for other users, **Then** they receive 403 or are redirected.
5. **Given** any logged-in user, **When** they open their own profile page, **Then** they see their email, display name, and role, and can update their display name.
6. **Given** an Admin attempts to deactivate their own account or reassign their own role away from Admin, **When** doing so would leave zero active Admins, **Then** the system rejects it.

### Edge Cases

- What happens if the last active Admin attempts to deactivate their own account or have their role changed away from Admin? → Rejected; at least one active Admin must always exist.
- What happens when an Admin creates a user with an email that already exists? → Rejected with 409.
- What happens to a deactivated user's previously-issued JWT? → Remains technically valid (signature-wise) until natural expiry, since there is no server-side revocation list in v1; however, every subsequent permission check still passes through `get_current_user`, which re-checks `is_active` on every request, so a deactivated user's *next request* is rejected immediately, not just their next login.

---

## Functional Requirements

- **FR-USR-001**: System MUST allow Admins to create a User with email (required, unique), password (required, write-only), display name (optional), and a Role assignment (required).
- **FR-USR-002**: System MUST allow Admins to update a User's role, display name, and active status, and to deactivate or reactivate a User.
- **FR-USR-003**: System MUST allow any authenticated User to retrieve and update their own profile (display name only); role and active status are Admin-only fields.
- **FR-USR-004**: System MUST allow retrieval of a paginated, searchable, sortable, filterable (by role, active status) list of Users (Admin only).
- **FR-USR-005**: System MUST prevent deactivation of a User, or a role change away from Admin, if doing so would leave zero active Admin users in the system.
- **FR-USR-006**: System MUST enforce email uniqueness across all Users, returning 409 on conflict.
- **FR-USR-007**: System MUST hash all passwords before storage and MUST never return password hashes in any API response.

## Key Entities

- **User**: An individual account holder. Key attributes: email (unique), hashed password, display name, assigned Role (FK), active flag.

---

## Success Criteria

- **SC-USR-001**: At least one active Admin account always exists; 100% of attempts to remove the last active Admin are rejected.
- **SC-USR-002**: Full User CRUD is independently verifiable and correctly permission-gated (create/update = Admin only; self-profile = any authenticated user).
- **SC-USR-003**: All three default seed users (admin@crm.local, manager@crm.local, sales@crm.local) can log in immediately after the seed step, each with the correct role.

---

## Dependencies on Other Modules

| Dependency | Direction | Reason |
|---|---|---|
| [Roles](../roles/spec.md) | Users **depends on** Roles | `users.role_id` is a required FK; Users cannot be created without a valid Role |
| [Authentication](../authentication/spec.md) | **Depended on by** Authentication | Login credential verification and `GET /auth/me` both read from this module's table |
| [Leads](../leads/spec.md) | **Depended on by** Leads | `leads.created_by_user_id` is a nullable FK into this module's table |
| [Activities](../activities/spec.md) | **Depended on by** Activities | `activities.created_by_user_id` is a nullable FK into this module's table |

**Build order implication**: Users must be implemented after Roles (needs a valid `role_id` to assign) and before Authentication, Leads, and Activities (all of which reference Users).
