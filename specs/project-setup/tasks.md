# Module Tasks: Project Setup / Foundation

**Module**: `project-setup` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Prerequisites

- [ ] None. This is the first module implemented in the entire project.

---

## Implementation Tasks

| # | Task | Depends On |
|---|---|---|
| T-SETUP-1 | Verify and pin toolchain versions: confirm `node --version` reports `v22.17.1` and `npm --version` reports `10.9.2` on the reference dev machine; write `.nvmrc` (`22.17.1`) and `.python-version` (`3.11`) | None |
| T-SETUP-2 | Scaffold `backend/` directory tree (`app/{models,schemas,services,routers,core/security}/`, `alembic/`, `tests/`) with `__init__.py` placeholders | T-SETUP-1 |
| T-SETUP-3 | Implement `backend/app/config.py` (pydantic-settings `Settings`: `DATABASE_URL`, `JWT_SECRET_KEY`, pagination defaults) | T-SETUP-2 |
| T-SETUP-4 | Implement `backend/app/database.py` (async engine, `AsyncSession` factory, `Base`, `PRAGMA foreign_keys = ON` wiring) | T-SETUP-3 |
| T-SETUP-5 | Implement `backend/app/main.py` (FastAPI app factory, CORS for the frontend dev origin, `GET /health`) | T-SETUP-4 |
| T-SETUP-6 | Initialize Alembic; write the empty `0001_baseline` revision | T-SETUP-4 |
| T-SETUP-7 | Write `backend/.env.example`, `backend/requirements.txt` + `requirements-dev.txt` | T-SETUP-5, T-SETUP-6 |
| T-SETUP-8 | Scaffold `frontend/` directory tree (`src/{components/{layout,ui},features,context,lib,pages,routes}/`) via Vite's React+TS template | T-SETUP-1 |
| T-SETUP-9 | Configure TailwindCSS (`tailwind.config.ts`, base styles) and `@fontsource/inter` | T-SETUP-8 |
| T-SETUP-10 | Implement `frontend/src/lib/` (Axios instance, React Query `QueryClient`) and a placeholder `AppShell` + root route | T-SETUP-8, T-SETUP-9 |
| T-SETUP-11 | Write `frontend/.env.example`, `frontend/package.json` with `engines: {"node": ">=18"}` and dependency versions verified to install cleanly under npm 10.9.2 | T-SETUP-10 |
| T-SETUP-12 | Write root-level `.gitignore` covering both stacks | T-SETUP-7, T-SETUP-11 |
| T-SETUP-13 | Verification pass: fresh clone → backend `alembic upgrade head` succeeds against an empty SQLite file → `uvicorn` starts → `GET /health` returns 200 → frontend `npm install && npm run dev` succeeds with no console errors | T-SETUP-12 |

## Task Sequencing

```
T-SETUP-1 ──┬──► T-SETUP-2 ──► T-SETUP-3 ──► T-SETUP-4 ──┬──► T-SETUP-5 ──┐
            │                                              └──► T-SETUP-6 ──┴──► T-SETUP-7 ──┐
            └──► T-SETUP-8 ──► T-SETUP-9 ──► T-SETUP-10 ──► T-SETUP-11 ──────────────────────┴──► T-SETUP-12 ──► T-SETUP-13
```

---

## Acceptance Criteria

- [ ] AC-1: `node --version` reports `v22.17.1` and `npm --version` reports `10.9.2` in the documented dev environment; `.nvmrc`/`.python-version` files exist and match (FR-SETUP-001).
- [ ] AC-2: `GET /health` returns `200` with a body confirming database connectivity, against a freshly migrated empty SQLite database (FR-SETUP-004, SC-SETUP-003).
- [ ] AC-3: Every directory path referenced by any of the 9 CRM modules' `plan.md` files (e.g., `backend/app/models/`, `frontend/src/features/`) exists at this module's completion (FR-SETUP-005, SC-SETUP-002).
- [ ] AC-4: `cp .env.example .env` (both backend and frontend) followed by the documented start commands results in both dev servers running with zero missing-variable errors (FR-SETUP-006).
- [ ] AC-5: SQLite foreign-key enforcement is verifiably ON (a manual test insert violating a hypothetical FK is rejected) (FR-SETUP-007).
- [ ] AC-6: `alembic upgrade head` against a fresh database applies exactly one revision (`0001_baseline`) and creates zero CRM tables (FR-SETUP-008).
- [ ] AC-7: A fresh clone reaches "both dev servers running" in under 10 minutes following only the documented steps (SC-SETUP-001).

## Dependencies and Prerequisites Recap

- **No blockers** — this module starts the entire project.
- **Downstream**: every one of the 9 CRM modules (Permissions, Roles, Users, Authentication, Accounts, Contacts, Opportunities, Leads, Activities) lists T-SETUP-13 as a hard prerequisite in their own `tasks.md`. The closing [Deployment](../deployment/tasks.md) module also depends on this module's exact folder/toolchain contract.
