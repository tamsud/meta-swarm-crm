# Module Specification: Project Setup / Foundation

**Module**: `project-setup` | **Created**: 2026-06-16 | **Status**: Draft

---

## Module Scope & Objectives

Project Setup is the **zeroth module** — it produces no business feature and owns no CRM data, but every one of the 9 CRM modules ([Permissions](../permissions/spec.md) through [Activities](../activities/spec.md)) and the closing [Deployment](../deployment/spec.md) module depends on it existing first. It locks in the technology stack and toolchain versions that earlier architecture docs (`plan.md` files across the other modules) only described as "Assumptions," and produces the actual repository skeleton — folder structure, base app entrypoints, environment configuration, and a working health check — that all subsequent module work is added into.

**In scope**:
- Confirming and locking the technology stack (no longer "assumed," but a hard requirement other modules' implementation must follow): backend Python 3.11+, FastAPI, SQLAlchemy 2.x (async), Pydantic v2, SQLite (dev) with a PostgreSQL-portable schema design; frontend React 18, Vite, TypeScript, TailwindCSS.
- Confirming and locking the toolchain versions the local development environment must use: **Node.js v22.17.1**, **npm 10.9.2** (verified via `node --version` / `npm --version`), Python 3.11+.
- The monorepo folder structure for `backend/` and `frontend/`, matching the layout previously described in each module's `plan.md` (`models/`, `schemas/`, `services/`, `routers/`, `core/security/` for backend; `components/`, `features/`, `context/`, `lib/`, `pages/`, `routes/` for frontend).
- Base app scaffolding: FastAPI app factory with a `/health` endpoint, the async SQLAlchemy engine + session factory + declarative `Base`, Alembic initialization (empty baseline migration), `.env.example` covering `DATABASE_URL`/`JWT_SECRET_KEY`/pagination defaults; the Vite + React + TypeScript + TailwindCSS frontend skeleton with an empty `AppShell` and a placeholder route.
- Environment configuration conventions (`.env` for backend, `.env.local` for frontend Vite vars), `.gitignore` covering both stacks.

**Out of scope**: any CRM business logic, any of the 9 modules' tables/routes/pages (those are each module's own responsibility once this module's scaffold exists), Docker/containerization and seed data (that is the closing [Deployment module](../deployment/spec.md)'s responsibility).

**Objective**: Ensure that the moment any of the 9 CRM modules' implementation starts, the engineer opens a repository that already builds, already runs (`/health` returns 200, the frontend dev server renders an empty shell), and already has the exact folder each new file belongs in — with zero ambiguity about stack or toolchain version.

---

## User Stories

### User Story 0 - Locked-In Foundation (Priority: P0 — blocks everything)

A developer picking up the first CRM module (Permissions) needs a repository that already runs end-to-end empty, on the exact toolchain versions the team has standardized on, so that the first line of module-specific code they write is business logic, not scaffolding.

**Why this priority**: Every other module's `tasks.md` lists this module as a hard prerequisite. Without it, "implement Permissions" silently also means "first invent a folder structure and hope it matches what Roles expects next sprint."

**Independent Test**: Clone the repo at this module's completion commit. Run `node --version` (expect `v22.17.1`) and `npm --version` (expect `10.9.2`). Start the backend (`uvicorn app.main:app`) and call `GET /health` (expect `200 {"status": "ok"}`). Start the frontend (`npm run dev`) and confirm the Vite dev server serves an empty `AppShell` with no console errors. Run `alembic upgrade head` against a fresh SQLite file and confirm it completes with zero migrations beyond the baseline (no CRM tables exist yet — that's correct, they belong to the other 9 modules).

**Acceptance Scenarios**:

1. **Given** a fresh clone of the repository, **When** a developer runs the documented setup commands, **Then** both the backend and frontend dev servers start without error.
2. **Given** the running backend, **When** `GET /health` is called, **Then** it returns `200` with a JSON body confirming the service and database connectivity are healthy.
3. **Given** the toolchain check, **When** `node --version` and `npm --version` are run, **Then** they report `v22.17.1` and `10.9.2` respectively (or the project's `.nvmrc`/`engines` field pins exactly these, with a clear error if a developer's installed version mismatches).
4. **Given** the folder structure, **When** any of the 9 CRM modules' implementation begins, **Then** every file path referenced in that module's `plan.md` (e.g., `backend/app/models/permission.py`) already has a valid, existing parent directory to be created in.
5. **Given** `.env.example`, **When** a developer copies it to `.env`, **Then** the application starts successfully with only placeholder values replaced (no missing required variables).

### Edge Cases

- What happens if a developer has a different Node/npm version installed? → The frontend's `package.json` `engines` field should specify `"node": ">=18"` per the original frontend spec's compatibility note, but the canonical, tested version for this project is locked at Node v22.17.1 / npm 10.9.2; a version mismatch should produce a clear warning (via `engine-strict` or a documented manual check), not a silent, possibly-broken install.
- What happens if SQLite's `PRAGMA foreign_keys = ON` is forgotten when wiring the DB engine? → Every other module's FK constraints (e.g., Accounts' deletion guard, Leads' `created_by_user_id`) silently stop being enforced at the DB level; this module's `database.py` must enable it per-connection as part of the baseline scaffold, not leave it to be discovered later by a CRM module's bug report.
- What happens if the backend and frontend disagree on the API base URL during local development? → `.env.example` for the frontend pins `VITE_API_BASE_URL=http://localhost:8000/api/v1`, matching the backend's documented port and base path from the very first commit.

---

## Functional Requirements

- **FR-SETUP-001**: The repository MUST use Python 3.11+ for the backend and Node.js v22.17.1 / npm 10.9.2 for the frontend toolchain, with both versions verifiable via `python --version`, `node --version`, `npm --version`, and pinned in version files (`.python-version`, `.nvmrc`, `package.json#engines`).
- **FR-SETUP-002**: The backend MUST be scaffolded with FastAPI, SQLAlchemy 2.x (async), Pydantic v2, and SQLite as the development database, with the schema designed to remain PostgreSQL-portable (per the conventions already documented in each of the 9 modules' `plan.md` files).
- **FR-SETUP-003**: The frontend MUST be scaffolded with React 18, Vite, TypeScript, and TailwindCSS, matching the component/page conventions already documented in each module's `plan.md`.
- **FR-SETUP-004**: The backend MUST expose a `GET /health` endpoint that verifies database connectivity and returns `200` when healthy.
- **FR-SETUP-005**: The repository MUST provide a monorepo folder structure under `backend/app/{models,schemas,services,routers,core/security}/` and `frontend/src/{components,features,context,lib,pages,routes}/`, with every directory referenced by any of the 9 CRM modules' `plan.md` files present (even if initially empty aside from an `__init__.py`/`index.ts` placeholder).
- **FR-SETUP-006**: The repository MUST provide `.env.example` files for both backend (`DATABASE_URL`, `JWT_SECRET_KEY`, pagination defaults) and frontend (`VITE_API_BASE_URL`), and a root-level `.gitignore` covering both stacks' build artifacts, dependency directories, and environment files.
- **FR-SETUP-007**: The backend's database engine wiring MUST enable `PRAGMA foreign_keys = ON` per connection for SQLite, so that every other module's foreign-key and CHECK constraints are enforced from the first migration onward.
- **FR-SETUP-008**: Alembic MUST be initialized with an empty baseline migration before any of the 9 CRM modules add their own schema migrations, so that migration history has a single, clean starting point.

## Key Entities

*(None — this module owns no business data. It owns only configuration and scaffold files: `.env.example`, `alembic.ini`, `pyproject.toml`/`requirements.txt`, `package.json`, `tailwind.config.ts`, `vite.config.ts`.)*

---

## Success Criteria

- **SC-SETUP-001**: A developer can go from `git clone` to both dev servers running, on a machine with Node v22.17.1 / npm 10.9.2 and Python 3.11+ installed, in under 10 minutes following only the documented setup steps.
- **SC-SETUP-002**: Zero folder-structure rework is required by any of the 9 CRM modules — every path their `plan.md` references already exists at this module's completion.
- **SC-SETUP-003**: `GET /health` returns 200 on a freshly migrated, empty database.

---

## Dependencies on Other Modules

| Dependency | Direction | Reason |
|---|---|---|
| None | Project Setup has zero dependencies on other modules | It is the foundation everything else is built on |
| [Permissions](../permissions/spec.md), [Roles](../roles/spec.md), [Accounts](../accounts/spec.md), [Users](../users/spec.md), [Authentication](../authentication/spec.md), [Contacts](../contacts/spec.md), [Opportunities](../opportunities/spec.md), [Leads](../leads/spec.md), [Activities](../activities/spec.md) | **Depended on by** all 9 | Every module's `tasks.md` lists this module's completion as the first prerequisite — none of their migrations, models, or frontend pages have anywhere to go without this module's scaffold |
| [Deployment](../deployment/spec.md) | **Depended on by** Deployment | Dockerfiles wrap this module's exact backend/frontend scaffold and toolchain versions |

**Build order implication**: Project Setup is implemented **first, before any other module**, with no exceptions.
