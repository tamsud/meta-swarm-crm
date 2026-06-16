# Module Plan: Project Setup / Foundation

**Module**: `project-setup` | **Spec**: [spec.md](spec.md)

---

## Module Architecture

This module produces the empty skeleton every other module's four-layer architecture (`models/ → schemas/ → services/ → routers/`) is added into. There is no business logic of its own — only wiring.

```
repo-root/
├── backend/
│   ├── app/
│   │   ├── main.py            → FastAPI app factory, router registration, CORS, /health
│   │   ├── database.py        → async engine, AsyncSession factory, Base, PRAGMA foreign_keys=ON
│   │   ├── config.py          → Settings (DATABASE_URL, JWT_SECRET_KEY, pagination defaults) via pydantic-settings
│   │   ├── core/
│   │   │   └── security/      → empty package; populated by the Authentication module
│   │   ├── models/            → empty package (each CRM module adds its own model file)
│   │   ├── schemas/            → empty package
│   │   ├── services/           → empty package
│   │   └── routers/            → empty package
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/0001_baseline.py   → empty baseline revision
│   ├── tests/
│   │   └── conftest.py        → test DB fixture, AsyncClient fixture (no entity-specific fixtures yet)
│   ├── alembic.ini
│   ├── pyproject.toml / requirements.txt + requirements-dev.txt
│   ├── .python-version        → "3.11"
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── main.tsx, App.tsx
    │   ├── components/{layout,ui}/   → empty, ready for shared components
    │   ├── features/                  → empty, one subfolder added per CRM module
    │   ├── context/                   → empty, AuthContext added by Authentication module
    │   ├── lib/                       → axios instance + React Query client, no module-specific calls yet
    │   ├── pages/                     → empty, placeholder route only
    │   └── routes/                    → empty, route guards added by Authentication module
    ├── package.json            → engines: { "node": ">=18" }, pinned dev versions matching Node v22.17.1/npm 10.9.2
    ├── tailwind.config.ts      → base config, design tokens added incrementally by later modules
    ├── vite.config.ts
    ├── .nvmrc                  → "22.17.1"
    └── .env.example            → VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Components and Responsibilities

| Component | Responsibility |
|---|---|
| `backend/app/main.py` | FastAPI app factory; registers `/health`; registers each CRM module's router as that module adds one (this module registers none yet) |
| `backend/app/database.py` | Creates the async SQLAlchemy engine against `DATABASE_URL` (SQLite dev default), the `AsyncSession` factory, the shared `Base = DeclarativeBase()` every model inherits from, and enables `PRAGMA foreign_keys = ON` on every new connection |
| `backend/app/config.py` | `pydantic-settings`-based `Settings` class reading `.env`; the single source of `DATABASE_URL`, `JWT_SECRET_KEY`, default/max pagination size |
| `backend/alembic/` | Migration tooling, initialized with one empty baseline revision; every CRM module's own migration is a child revision of this baseline |
| `frontend/src/lib/` | The shared Axios instance (no interceptors yet — Authentication module adds them) and the React Query `QueryClient` instance every module's hooks will use |
| `frontend/src/components/layout/AppShell` (skeleton only) | Renders a placeholder `<main>{children}</main>`; the Authentication module later wraps it with `NavSidebar` and route guards |
| Toolchain pin files (`.python-version`, `.nvmrc`, `package.json#engines`) | Make the Node v22.17.1 / npm 10.9.2 / Python 3.11+ requirement machine-checkable, not just documented prose |

## Data Flow Within the Module

```
[Developer clones repo]
   → backend: create venv, pip install -r requirements.txt
   → cp backend/.env.example backend/.env
   → alembic upgrade head   (applies the empty 0001_baseline revision — creates no tables)
   → uvicorn app.main:app --reload
   → GET /health → [database.py: SELECT 1 against the async engine] → 200 {"status": "ok", "database": "connected"}

[Developer starts the frontend]
   → cp frontend/.env.example frontend/.env.local
   → npm install (Node v22.17.1 / npm 10.9.2)
   → npm run dev
   → Vite serves AppShell (empty placeholder) at the dev server URL, no network calls made yet (no modules have pages)
```

There is no persisted business data flow in this module — only the one-time scaffold-creation and the `/health` check's DB connectivity probe.

## Integration Points with Other Modules

| Module | Integration Point |
|---|---|
| Every one of the 9 CRM modules | Each module's first implementation task is "add a migration as a child of `0001_baseline`," "add a model file inside `backend/app/models/`," "add a router file inside `backend/app/routers/` and register it in `main.py`," and on the frontend, "add a feature folder inside `frontend/src/features/`." This module's folder layout is the contract every other module's `plan.md` already assumed when it was written. |
| [Authentication](../authentication/plan.md) | Populates the empty `core/security/` package and the frontend's `context/AuthContext`; wraps `AppShell` with route guards |
| [Deployment](../deployment/plan.md) | Wraps this module's exact `backend/` and `frontend/` directories in Dockerfiles; the docker-compose `DATABASE_URL` must match this module's `config.py` contract |

---

## Architectural Decisions Specific to This Module

- **Empty baseline Alembic revision, not "first module's migration is the baseline"**: keeps the migration history clean — `0001_baseline` is reserved for "the database exists, no CRM tables yet," so each of the 9 modules' own migration is a clean, independently revertible child revision, never entangled with another module's schema.
- **Toolchain versions pinned in machine-readable files, not only in this prose document**: `.nvmrc`, `.python-version`, and `package.json#engines` mean a version mismatch is caught by tooling (`nvm use`, `engine-strict`) rather than discovered only when something subtly breaks later.
- **No business logic, deliberately**: every file this module creates is either empty, a placeholder, or pure infrastructure wiring (DB engine, app factory, Axios instance) — this keeps the module reviewable as "does the skeleton work," not entangled with any CRM feature's correctness.
