# Module Plan: Dockerization & Seed Data

**Module**: `deployment` | **Spec**: [spec.md](spec.md)

---

## Module Architecture

Two independent concerns sharing one module: container packaging (no business logic) and seed-data generation (calls every other module's real service layer — never raw SQL — so seeded data is exactly as valid as user-created data).

```
repo-root/
├── docker-compose.yml          → backend + frontend services, named volume for SQLite file
├── backend/
│   ├── Dockerfile               → python:3.11-slim base, installs requirements.txt, runs alembic + uvicorn
│   └── app/
│       └── scripts/
│           └── seed.py          → seed_all() / clear_all() — the module's only real code
└── frontend/
    └── Dockerfile                → node:22.17.1 build stage → nginx (or `serve`) runtime stage
```

## Components and Responsibilities

| Component | Responsibility |
|---|---|
| `backend/Dockerfile` | Multi-stage build: install Python 3.11 + dependencies, copy `app/`, run `alembic upgrade head` then `uvicorn app.main:app --host 0.0.0.0` as the container entrypoint |
| `frontend/Dockerfile` | Stage 1 (Node v22.17.1): `npm ci && npm run build`. Stage 2: copy the built static assets into an nginx (or `serve`) image, expose the configured port |
| `docker-compose.yml` | Defines `backend` and `frontend` services, a named volume (e.g., `crm_db_data`) mounted at the SQLite file's directory inside the backend container, environment variables matching `.env.example` from [Project Setup](../project-setup/plan.md), and a network letting the frontend reach the backend by service name |
| `backend/app/scripts/seed.py` — `seed_all()` | Calls, in dependency order, each module's own service-layer `create_*` function: seed 3 demo Users (via Users' service) → 50+ Accounts (Accounts' service) → 50+ Contacts linked to those Accounts (Contacts' service) → 50+ Opportunities across all 5 stages (Opportunities' service) → 50+ Leads across all 4 statuses incl. ≥1 converted via the real `convert` operation (Leads' service) → 50+ Activities across all 3 types (Activities' service) |
| `backend/app/scripts/seed.py` — `clear_all()` | Deletes rows from `activities`, `leads`, `opportunities`, `contacts`, `accounts`, and non-seed `users` (preserving the 3 demo Users, the system Roles, and the entire Permissions catalogue) |
| Frontend `/admin/seed` page (extends the page already specified in each CRM module's own frontend notes) | "Seed demo data" button → `POST /seed`; "Clear all data" button (Admin only, confirmation dialog) → `DELETE /seed` |

## Data Flow Within the Module

```
[docker compose up]
   → backend container: alembic upgrade head (applies 0001_baseline + all 9 modules' migrations, in their authored dependency order)
   → backend container: uvicorn starts, binds to the named volume's SQLite file path
   → frontend container: serves the pre-built static bundle, configured to call the backend service by its compose network name

[POST /seed — seed_all()]
   → BEGIN (logically — each module's own service call manages its own transaction boundary)
   → Users.service.create_user() × 3 (admin/manager/sales, idempotent: skip if email exists)
   → Accounts.service.create_account() × 50+ (idempotent: skip if name already seeded, tracked by a deterministic seed-tag prefix or exact name match)
   → Contacts.service.create_contact() × 50+ (each linked to a seeded Account; idempotent on email)
   → Opportunities.service.create_opportunity() × 50+ (spread across all 5 stages, linked to seeded Accounts/Contacts)
   → Leads.service.create_lead() × 50+ (spread across new/contacted/qualified/lost)
   → Leads.service.convert_lead() × N (promote a few "qualified" seeded Leads through the real conversion transaction, producing real, reused-or-created Accounts/Contacts/Opportunities)
   → Activities.service.create_activity() × 50+ (spread across call/email/meeting, linked to seeded Contacts/Opportunities)
   → 200 {created: {users: 3, accounts: 53, contacts: 58, opportunities: 54, leads: 50, activities: 60}} (illustrative counts ≥ 50 per required entity)

[DELETE /seed — clear_all()]
   → require_permission("seed:manage") [Admin only]
   → DELETE FROM activities; DELETE FROM leads; DELETE FROM opportunities; DELETE FROM contacts; DELETE FROM accounts;
   → DELETE FROM users WHERE email NOT IN (the 3 demo seed emails)
   → 204
```

## Integration Points with Other Modules

| Module | Integration Point |
|---|---|
| [Project Setup](../project-setup/plan.md) | Both Dockerfiles build directly on top of that module's `backend/`/`frontend/` directory contracts and pinned toolchain versions (Python 3.11, Node v22.17.1) |
| [Users](../users/plan.md) | `seed_all()` calls Users' own create function for the 3 demo accounts — never inserts directly into `users` |
| [Accounts](../accounts/plan.md), [Contacts](../contacts/plan.md), [Opportunities](../opportunities/plan.md) | Same pattern — every seeded row is created through that module's real validated service function |
| [Leads](../leads/plan.md) | `seed_all()` additionally exercises the real `convert_lead()` transaction for at least a few seeded Leads, so the seeded dataset includes genuine, atomically-created converted Opportunities — not hand-faked ones |
| [Activities](../activities/plan.md) | Same create-through-service pattern, ensuring every seeded Activity satisfies the link-required constraint exactly as a real one would |
| [Permissions](../permissions/plan.md) / [Roles](../roles/plan.md) | `clear_all()` explicitly excludes these two modules' tables — the catalogue and system roles are infrastructure, not demo data, and must survive a "Clear all data" click |

---

## Architectural Decisions Specific to This Module

- **Seed data is created through real service-layer calls, never raw SQL inserts**: guarantees every seeded record is exactly as valid as a user-created one (state machines respected, FK validation run, uniqueness constraints honored) — and means the seed script doubles as a high-volume integration smoke test of every other module's service layer.
- **Named Docker volume, not a bind mount**: a bind mount couples the container to the host filesystem layout; a named volume is portable across machines and is the documented mechanism for "survives `down`, destroyed only by `down -v`."
- **`clear_all()` explicitly whitelists what it does NOT touch** (Permissions, Roles, the 3 demo Users) rather than only deleting an explicit list of "seeded" tables — this keeps the function safe by construction even if a 10th CRM module is added later and someone forgets to update this module's docs (worth flagging as a maintenance risk to revisit if/when that happens).
