# Module Specification: Authentication

**Module**: `authentication` | **Created**: 2026-06-16 | **Status**: Draft

---

## Module Scope & Objectives

Authentication is the stateless identity-verification layer for the entire CRM platform. It owns no business data of its own (it has no dedicated table) — it verifies credentials against the **Users** module and issues short-lived, signed JWT access tokens that every other module's authorization checks rely on.

**In scope**: login, session token issuance/verification, logout (client-side token clearing), the `get_current_user` request dependency, and the `Authorization: Bearer` enforcement contract used by every other module.

**Out of scope**: password reset/forgot-password flows, multi-factor authentication, OAuth2/SAML/SSO, server-side token revocation lists, refresh tokens — none of these are in this platform's v1 scope.

**Objective**: Ensure no protected resource in any other module is reachable without a valid, unexpired, signed token, and that the token carries enough identity information for downstream modules (Roles, Permissions, Users) to authorize the request without a second round trip.

---

## User Stories

### User Story 1 - Authentication & Session Management (Priority: P1)

A user who is not logged in is redirected to `/login`. They enter their email and password. On success the system issues a signed JWT access token, held in memory on the client (never in `localStorage`/`sessionStorage`), and attached as `Authorization: Bearer` on every subsequent API request. Unauthenticated or expired-token requests return `401` and the frontend redirects back to `/login`.

**Why this priority**: Authentication is the entry gate for every other module. Users, Roles, Permissions, and all CRM data depend on knowing *who* is acting before *what* they can do can be evaluated.

**Independent Test**: Visit any protected route while logged out → redirected to `/login`. Submit valid seed credentials → redirected to the dashboard with a token held in memory. Reload the page → session ends (memory-only token), user is redirected to `/login` again. Submit invalid credentials → inline error, no token issued. Click Logout → token cleared, redirected to `/login`.

**Acceptance Scenarios**:

1. **Given** a user visits any protected route, **When** they are not authenticated, **Then** they are redirected to `/login` with the originally requested route preserved for post-login redirect.
2. **Given** a user is on `/login`, **When** they submit valid credentials, **Then** they receive a JWT access token and are redirected to the dashboard (or their originally requested route).
3. **Given** a user submits invalid credentials, **When** login is attempted, **Then** a clear inline error message is shown and no token is issued.
4. **Given** a valid JWT, **When** the token expires (default 60 minutes), **Then** the next API call returns 401 and the frontend clears local auth state and redirects to `/login`.
5. **Given** a logged-in user, **When** they click Logout, **Then** the in-memory token is cleared immediately and they are redirected to `/login`.
6. **Given** a deactivated user account, **When** they attempt to log in with correct credentials, **Then** the login is rejected with a 401 and a message indicating the account is inactive.

### Edge Cases

- What happens when a JWT expires mid-session? → API returns 401; frontend clears token and redirects to `/login`.
- What happens if a user logs in from two browser tabs? → Each tab holds its own in-memory token independently; no shared session state, no conflict.
- What happens if the JWT secret key is rotated? → All previously issued tokens become invalid immediately (signature check fails); all active sessions are forced to re-login. Acceptable for v1 (no graceful key-rotation grace period).

---

## Functional Requirements

- **FR-AUTH-001**: System MUST expose a login operation that accepts email and password and returns a signed JWT access token plus token type on success.
- **FR-AUTH-002**: JWT access tokens MUST expire after a configurable duration (default 60 minutes).
- **FR-AUTH-003**: All protected API endpoints MUST require a valid `Authorization: Bearer` header; requests without one, or with an invalid/expired token, MUST return 401.
- **FR-AUTH-004**: The frontend MUST hold the access token only in memory (React context/state) — never in `localStorage`, `sessionStorage`, or cookies — and MUST attach it to every API request via a request interceptor.
- **FR-AUTH-005**: Unauthenticated frontend route visits MUST redirect to `/login`; successful login MUST redirect back to the originally requested route.
- **FR-AUTH-006**: Deactivated user accounts MUST be rejected at login with 401, even with correct credentials.
- **FR-AUTH-007**: System MUST expose a logout action that, on the client, clears the in-memory token immediately; no server-side token revocation list is required in v1 (tokens are short-lived).
- **FR-AUTH-008**: System MUST expose a `GET /auth/me` operation returning the authenticated user's profile, role, and resolved effective permission codes, for frontend session hydration.

## Key Entities

- **AuthToken (in-memory, frontend only, not persisted)**: `access_token` string, decoded payload (`role`, `email`, `sub`, `exp`).
- **JWT Payload**: `sub` (user id), `email`, `role`, `exp` (Unix timestamp). Defined fully in the Users module's data model — Authentication only consumes and verifies this shape, it does not own the User table.

---

## Success Criteria

- **SC-AUTH-001**: A user with no prior knowledge can log in with a seed credential and reach the dashboard in under 30 seconds.
- **SC-AUTH-002**: JWT access tokens are never present in browser storage (`localStorage`, `sessionStorage`, cookies) — confirmed by inspection.
- **SC-AUTH-003**: 100% of requests with a missing, malformed, or expired token receive 401, with zero exceptions across any endpoint in any other module.

---

## Dependencies on Other Modules

| Dependency | Direction | Reason |
|---|---|---|
| [Users](../users/spec.md) | Authentication **depends on** Users | Login validates credentials against the `users` table; `GET /auth/me` reads the user's profile and role |
| [Roles](../roles/spec.md) | Authentication **depends on** Roles (transitively via Users) | The JWT/session profile surfaces the user's role name; effective permission resolution joins through Roles |
| [Permissions](../permissions/spec.md) | Authentication **depends on** Permissions (transitively) | `GET /auth/me`'s `permissions` array is the resolved set from the user's Role |
| All other modules (Leads, Contacts, Accounts, Opportunities, Activities) | **Depended on by** Authentication's consumers | Every protected endpoint in every other module requires the `Authorization: Bearer` contract this module defines |

**Build order implication**: Authentication cannot be implemented or tested meaningfully until the Users module (and therefore Roles and Permissions) exist with at least the 3 seed users present.
