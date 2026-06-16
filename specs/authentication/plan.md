# Module Plan: Authentication

**Module**: `authentication` | **Spec**: [spec.md](spec.md)

---

## Module Architecture

Authentication is a **cross-cutting infrastructure layer**, not a CRUD module — it has no router resource of its own beyond `login` and `me`, and no owned database table. It is implemented as shared `core/security` infrastructure consumed by every other module's router.

```
┌─────────────────────────────────────────────────────────────┐
│                     core/security/                            │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐│
│  │ jwt.py       │  │ passwords.py  │  │ dependencies.py        ││
│  │ issue/verify │  │ hash/verify   │  │ get_current_user        ││
│  │ HS256 tokens │  │ bcrypt        │  │ require_permission(...) ││
│  └─────────────┘  └──────────────┘  └───────────────────────┘│
└─────────────────────────────────────────────────────────────┘
        ▲                                          ▲
        │ used by                                  │ used by
┌───────────────┐                          ┌──────────────────────┐
│ routers/auth.py│                          │ every other module's   │
│ POST /login    │                          │ router (as a FastAPI    │
│ GET  /me       │                          │ dependency on each route)│
└───────────────┘                          └──────────────────────┘
```

## Components and Responsibilities

| Component | Responsibility |
|---|---|
| `core/security/jwt.py` | Issue HS256-signed tokens with `{sub, email, role, exp}` claims; verify signature + expiry on every request |
| `core/security/passwords.py` | Hash passwords with bcrypt (cost ≥ 12) at user-creation time (owned by Users module); verify a plaintext password against a stored hash at login time |
| `core/security/dependencies.py` | `get_current_user`: decode the Bearer token, load the User + Role + effective Permissions from the database, attach to the request context. `require_permission(code)`: FastAPI dependency that 403s if `code` is not in the current request's effective permission set |
| `routers/auth.py` | `POST /auth/login` (delegates credential check to the Users module's service), `GET /auth/me` (returns the resolved profile from `get_current_user`) |
| Frontend `AuthContext` | Holds `{ token, user, permissions }` in memory; exposes `login()`, `logout()`, `hasPermission(code)` |
| Frontend Axios interceptor | Attaches `Authorization: Bearer <token>` to every outgoing request; on a 401 response, clears `AuthContext` and redirects to `/login` |
| Frontend route guards (`RequireAuth`, `RequirePermission`) | Wrap protected routes; consult `AuthContext` before rendering |

## Data Flow Within the Module

```
[Browser: login form]
   → POST /auth/login {email, password}
   → [Users service: SELECT user WHERE email; verify bcrypt hash; check is_active]
   → [Roles: load assigned Role] → [Permissions: load Role's permission codes]
   → core/security/jwt.py issues JWT {sub: user.id, email, role: role.name, exp}
   → 200 {access_token, token_type, expires_in}
[Browser: AuthContext stores token in memory; fetches GET /auth/me to hydrate user+permissions]
   → every subsequent request: Authorization: Bearer <token>
   → [core/security/dependencies.py: get_current_user]
        decode JWT → verify signature/exp → load User by sub → load Role → load effective Permissions
   → [require_permission(code) dependency, applied per-route by the target module] → 200 | 401 | 403
```

There is no Authentication-owned table, so there is no "data flow within the module" in the persistence sense beyond the above request-time resolution chain, which reads (never writes) the Users/Roles/Permissions tables on every request.

## Integration Points with Other Modules

| Module | Integration Point |
|---|---|
| [Users](../users/plan.md) | `POST /auth/login` calls into the Users service's credential-verification function; `GET /auth/me` calls the Users service's "get own profile" function |
| [Roles](../roles/plan.md) | `get_current_user` joins through `users.role_id` to load the assigned Role |
| [Permissions](../permissions/plan.md) | `get_current_user` joins through `role_permissions` to compute the effective permission set, embedded in `GET /auth/me`'s response and used by every `require_permission(...)` check |
| Every CRM module (Leads, Contacts, Accounts, Opportunities, Activities) | Every protected route in every module declares `Depends(get_current_user)` and `Depends(require_permission("{module}:{action}"))` from this module's `core/security` package — this is the only integration point; Authentication never imports CRM module code |

---

## Architectural Decisions Specific to This Module

- **Stateless verification, no session table**: A JWT's signature and `exp` claim are the entire trust mechanism; there is no server-side session record to revoke. Accepted tradeoff: a compromised token remains valid until natural expiry (mitigated by the short 60-minute default).
- **In-memory-only client storage**: Chosen over `localStorage` specifically to reduce XSS-based token theft risk, at the cost of losing the session on page reload.
