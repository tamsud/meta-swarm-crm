# Module Specification: Permissions

**Module**: `permissions` | **Created**: 2026-06-16 | **Status**: Draft

---

## Module Scope & Objectives

Permissions is the foundational, zero-dependency module that defines the fixed catalogue of atomic authorization grants every other module's enforcement logic checks against. Each Permission is identified by a unique code in the form `{module}:{action}` (e.g., `leads:create`, `users:manage-self`).

**In scope**: the seed-time-only catalogue of Permission rows, and a read-only browse/filter API used by the [Roles module](../roles/spec.md) when composing a role.

**Out of scope**: creating, editing, or deleting Permissions through the application — the catalogue is fixed at deployment time via a seed migration. Assigning permissions to a role is the Roles module's responsibility, not this module's.

**Objective**: Give every authorization decision in the system a single, auditable source of truth for "what actions can possibly be permission-gated," preventing ad-hoc or inconsistently-named permission strings from being invented across modules.

---

## User Stories

### User Story 2 (Permissions portion) - Permission Catalogue for RBAC

*(Shared with the [Roles module](../roles/spec.md); this module's portion is the catalogue itself.)*

Administrators composing a custom Role need to browse the full set of available Permissions, grouped by module, to decide what to grant.

**Why this priority**: Without a queryable catalogue, the Roles module's "compose a custom role" UI has nothing to populate its permission checklist with.

**Independent Test**: Call `GET /permissions` and confirm every module in scope (Authentication, Users, Roles, Permissions, Accounts, Contacts, Leads, Opportunities, Activities) has at least one corresponding permission code, and that the catalogue is identical across repeated calls (immutable).

**Acceptance Scenarios**:

1. **Given** the system has been seeded, **When** `GET /permissions` is called, **Then** the full catalogue is returned, each entry showing `code`, `module`, `action`, and `description`.
2. **Given** the catalogue, **When** filtered by `?module=leads`, **Then** only Leads-module permission codes are returned.
3. **Given** any authenticated user, **When** they attempt `POST`, `PATCH`, or `DELETE` against `/permissions`, **Then** the request is rejected (no such endpoints exist — 404/405, not 403, since the operation is not exposed at all).

### Edge Cases

- What happens when a Permission code referenced by a Role no longer exists (e.g., deprecated)? → Cannot occur in v1 — the catalogue is immutable once seeded; removing a code would require a manual migration coordinated with the Roles module's data.
- What happens if two modules accidentally seed a permission with the same code but different meanings? → Prevented by the UNIQUE constraint on `code`; the seed migration is the single authorship point for the entire catalogue, reviewed as one artifact.

---

## Functional Requirements

- **FR-PERM-001**: System MUST maintain a fixed, system-seeded catalogue of Permissions, each identified by a unique code in the form `{module}:{action}`, a human-readable description, and the module it governs.
- **FR-PERM-002**: System MUST allow retrieval of the full Permission catalogue, optionally filtered by module, for use when composing or editing a Role.
- **FR-PERM-003**: The Permission catalogue MUST be read-only via the API in v1 — Permissions are seeded at deployment time and cannot be created, edited, or deleted through the application.

## Key Entities

- **Permission**: A single, atomic grant. Key attributes: `code` (unique, `{module}:{action}` format), `module`, `action`, `description`.

---

## Success Criteria

- **SC-PERM-001**: 100% of permission-restricted API calls across every other module return 403 when made by a caller whose effective permission set does not include the required code — this module's catalogue is the contract every other module's `require_permission(...)` check is written against.
- **SC-PERM-002**: The catalogue contains at minimum one permission code per module in scope, with zero duplicate codes.

---

## Dependencies on Other Modules

| Dependency | Direction | Reason |
|---|---|---|
| None | Permissions has zero module dependencies | It is system-seeded and self-contained |
| [Roles](../roles/spec.md) | **Depended on by** Roles | Role-to-permission assignment validates against and reads from this module's catalogue |
| [Authentication](../authentication/spec.md) | **Depended on by** Authentication (transitively via Roles) | Effective-permission resolution ultimately reads rows from this module's `permissions` table |
| Every other module | **Depended on by** all modules | Each module's own functional requirements reference specific Permission codes from this catalogue (e.g., Leads' FR-LEAD-006 references `leads:manage-own`/`leads:manage-all`) |

**Build order implication**: Permissions has no dependencies and should be the **first** module implemented — every other module either directly or transitively depends on its seed data existing.
