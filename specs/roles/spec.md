# Module Specification: Roles

**Module**: `roles` | **Created**: 2026-06-16 | **Status**: Draft

---

## Module Scope & Objectives

Roles is a named bundle of [Permissions](../permissions/spec.md), assignable to [Users](../users/spec.md). The system ships with three protected, non-deletable **system roles** — Admin, Manager, Sales Rep — that reproduce the reference CRM's original hardcoded RBAC behavior exactly. Admins may additionally define **custom roles** composed of any subset of the permission catalogue, without code changes.

**In scope**: Role CRUD (create/update/delete for custom roles; read for all roles), permission-set assignment to a role, protection of system roles from deletion/rename, and the "role has users" deletion guard.

**Out of scope**: Permission *catalogue* management (that is the [Permissions module](../permissions/spec.md)'s responsibility — Roles only consumes the catalogue), per-record/per-resource ownership rules (handled inside the Leads/Activities modules via `manage-own`/`manage-all` permission codes that Roles merely bundles).

**Objective**: Make authorization rules data-driven and Admin-configurable, while preserving 100% behavioral parity with the original three-role reference design as the default, unconfigurable-away baseline.

---

## User Stories

### User Story 2 - Role-Based Access Control via Roles & Permissions (Priority: P1)

*(Shared with the [Permissions module](../permissions/spec.md); this module's portion focuses on Role composition and assignment.)*

The system ships with three system-defined roles — **Admin**, **Manager**, **Sales Rep** — each composed of a set of granular permissions. Administrators can compose additional custom roles by selecting permissions from the catalogue, without code changes.

**Why this priority**: Roles must exist before User records can be meaningfully assigned an authorization identity, and before any CRM module can enforce who may act on its data.

**Independent Test**: As Admin, create a new custom role with a subset of permissions, assign it to a test user, and confirm that user's access matches exactly the selected permissions — no more, no less.

**Acceptance Scenarios**:

1. **Given** an Admin, **When** they create a custom role with a chosen subset of permissions and assign it to a user, **Then** that user's subsequent requests are authorized strictly according to the selected permissions.
2. **Given** a system-defined role (Admin, Manager, Sales Rep), **When** an Admin attempts to delete or rename it, **Then** the operation is rejected — system roles are immutable in name and cannot be removed.
3. **Given** a Role (system or custom) currently assigned to one or more Users, **When** an Admin attempts to delete it, **Then** the deletion is rejected with a descriptive error listing the affected user count.
4. **Given** the Roles list page, **When** an Admin views it, **Then** each row shows the permission count and user count for that role.

### Edge Cases

- What happens when an Admin attempts to remove all permissions from the "Admin" system role? → Rejected; system role permission sets are immutable, same as their names (`SYSTEM_ROLE_IMMUTABLE`).
- What happens when two Admins simultaneously edit the same custom role's permission set? → Last write wins; no optimistic-locking conflict detection in v1.
- What happens when a custom role ends up with zero permissions? → Allowed (a deliberately restrictive role is valid); such a user retains only the implicit `users:manage-self` self-profile capability.

---

## Functional Requirements

- **FR-ROLE-001**: System MUST ship exactly three system-defined Roles: Admin, Manager, Sales Rep, each pre-populated with a fixed permission set (per [Permissions module](../permissions/spec.md) catalogue). System-defined roles cannot be deleted and their names cannot be changed.
- **FR-ROLE-002**: System MUST allow Admins to create, read, update, and delete custom Roles, each composed of a chosen subset of Permissions from the catalogue.
- **FR-ROLE-003**: System MUST prevent deletion of any Role (system or custom) that is currently assigned to one or more Users, returning a descriptive error with the affected user count.
- **FR-ROLE-004**: System MUST allow retrieval of a paginated list of Roles, including the count of Users and Permissions associated with each.

## Key Entities

- **Role**: A named bundle of Permissions assignable to Users. Key attributes: name (unique), description, system-defined flag (`is_system`), associated Permissions (via the `role_permissions` join, owned jointly with the Permissions module).

---

## Success Criteria

- **SC-ROLE-001**: All three default role types (Admin, Manager, Sales Rep) can be exercised end-to-end without any manual database changes.
- **SC-ROLE-002**: A new custom Role with an arbitrary Permission subset, once assigned to a User, produces access behavior that matches exactly the selected Permissions — no more, no less.

---

## Dependencies on Other Modules

| Dependency | Direction | Reason |
|---|---|---|
| [Permissions](../permissions/spec.md) | Roles **depends on** Permissions | A Role's permission set is a chosen subset of the Permissions catalogue; Role creation/update validates every `permission_id` against it |
| [Users](../users/spec.md) | **Depended on by** Users | `users.role_id` is a required foreign key into this module's `roles` table; Users cannot be created without a valid Role to assign |
| [Authentication](../authentication/spec.md) | **Depended on by** Authentication | Every request's effective-permission resolution joins through this module's `role_permissions` table |

**Build order implication**: Roles must be implemented after Permissions (it consumes the catalogue) and before Users (Users requires a valid `role_id` to exist).
