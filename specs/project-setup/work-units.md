# Module Work Units: Project Setup / Foundation

**Module**: `project-setup` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Tasks**: [tasks.md](tasks.md)

---

## Dependency Graph

### Upstream
- **None.** This is the first module in the project.

### Downstream
- Every other module (9 CRM + Deployment) hard-blocks on this module's completion (T-SETUP-13).

### Internal sequence
```
WU-SETUP-1 ──┬──► WU-SETUP-2 ──► WU-SETUP-3 ──► WU-SETUP-4 ──┐
             │                                                 │
             └──► WU-SETUP-5 ──► WU-SETUP-6 ──► WU-SETUP-7 ──┴──► WU-SETUP-8 ──► WU-SETUP-9
```

---

## Work Units

### WU-SETUP-1: Toolchain Pinning
**Tasks**: T-SETUP-1
**Depends on**: None
**Parallelizable with**: None (gate for all subsequent units)

**File scope**:
- `.nvmrc` (new)
- `.python-version` (new)

**Definition of Done**:
- [x] `node --version` reports `v22.17.1` on the dev machine
- [x] `npm --version` reports `10.9.2`
- [x] `.nvmrc` contents = `22.17.1`
- [x] `.python-version` contents = `3.11`

**Success Criteria covered**: SC-SETUP-001

---

### WU-SETUP-2: Backend Scaffold + Core Config
**Tasks**: T-SETUP-2, T-SETUP-3, T-SETUP-4, T-SETUP-5
**Depends on**: WU-SETUP-1
**Parallelizable with**: WU-SETUP-5 (frontend scaffold)

**File scope**:
- `backend/app/__init__.py` (new)
- `backend/app/{models,schemas,services,routers}/__init__.py` (new, all empty)
- `backend/app/core/__init__.py`, `backend/app/core/security/__init__.py` (new)
- `backend/tests/__init__.py` (new)
- `backend/app/config.py` (new — pydantic-settings `Settings`)
- `backend/app/database.py` (new — async engine, `AsyncSession`, `Base`, `PRAGMA foreign_keys=ON`)
- `backend/app/main.py` (new — FastAPI app factory, CORS, `GET /health`)

**Definition of Done**:
- [x] All listed directories exist with `__init__.py` placeholders
- [x] `Settings` exposes `DATABASE_URL`, `JWT_SECRET_KEY`, pagination defaults via env vars
- [x] `database.py` enforces `PRAGMA foreign_keys=ON` on every connection (verified by a unit test)
- [x] `uvicorn backend.app.main:app` starts cleanly
- [x] `GET /health` returns 200 with body confirming DB connectivity

**Success Criteria covered**: SC-SETUP-002, SC-SETUP-003

---

### WU-SETUP-3: Alembic Baseline
**Tasks**: T-SETUP-6
**Depends on**: WU-SETUP-2
**Parallelizable with**: WU-SETUP-5, WU-SETUP-6

**File scope**:
- `backend/alembic.ini` (new)
- `backend/alembic/env.py` (new — wired to `app.database.Base`)
- `backend/alembic/script.py.mako` (new)
- `backend/alembic/versions/0001_baseline.py` (new — empty revision)

**Definition of Done**:
- [x] `alembic upgrade head` against a fresh SQLite file applies exactly one revision (`0001_baseline`)
- [x] Zero CRM tables created by the baseline
- [x] `alembic.ini` `sqlalchemy.url` is read from `Settings`, not hardcoded

**Success Criteria covered**: SC-SETUP-003

---

### WU-SETUP-4: Backend Env + Dependencies
**Tasks**: T-SETUP-7
**Depends on**: WU-SETUP-2, WU-SETUP-3
**Parallelizable with**: WU-SETUP-5, WU-SETUP-6, WU-SETUP-7

**File scope**:
- `backend/.env.example` (new)
- `backend/requirements.txt` (new — pinned)
- `backend/requirements-dev.txt` (new — pinned)

**Definition of Done**:
- [x] `pip install -r requirements.txt -r requirements-dev.txt` succeeds on Python 3.11 with zero conflicts
- [x] `.env.example` lists every variable read by `app/config.py`
- [x] `cp .env.example .env && uvicorn ...` produces zero missing-variable errors

**Success Criteria covered**: SC-SETUP-001

---

### WU-SETUP-5: Frontend Scaffold + Tailwind
**Tasks**: T-SETUP-8, T-SETUP-9
**Depends on**: WU-SETUP-1
**Parallelizable with**: WU-SETUP-2, WU-SETUP-3, WU-SETUP-4

**File scope**:
- `frontend/` (Vite React+TS template scaffold)
- `frontend/src/{components/{layout,ui},features,context,lib,pages,routes}/` (new, with `.gitkeep` where empty)
- `frontend/tailwind.config.ts` (new)
- `frontend/postcss.config.js` (new)
- `frontend/src/index.css` (Tailwind base/components/utilities + `@fontsource/inter`)

**Definition of Done**:
- [x] `npm install` succeeds under npm 10.9.2
- [x] All directories referenced by other modules' `plan.md` exist
- [x] Tailwind classes render in the placeholder page (manual check)
- [x] Inter font loads on first render (Network tab check)

**Success Criteria covered**: SC-SETUP-002

---

### WU-SETUP-6: Frontend Lib + AppShell
**Tasks**: T-SETUP-10
**Depends on**: WU-SETUP-5
**Parallelizable with**: WU-SETUP-3, WU-SETUP-4

**File scope**:
- `frontend/src/lib/api.ts` (new — Axios instance, base URL from env)
- `frontend/src/lib/queryClient.ts` (new — React Query `QueryClient`)
- `frontend/src/components/layout/AppShell.tsx` (new — placeholder shell)
- `frontend/src/routes/index.tsx` (new — root route)
- `frontend/src/App.tsx`, `frontend/src/main.tsx` (modify — wire `QueryClientProvider`, router)

**Definition of Done**:
- [x] `npm run dev` renders AppShell with no console errors
- [x] Axios instance reads `VITE_API_BASE_URL` from env
- [x] React Query DevTools mountable (manual)

**Success Criteria covered**: SC-SETUP-002

---

### WU-SETUP-7: Frontend Env + package.json
**Tasks**: T-SETUP-11
**Depends on**: WU-SETUP-6
**Parallelizable with**: WU-SETUP-4

**File scope**:
- `frontend/.env.example` (new)
- `frontend/package.json` (modify — `engines: {"node": ">=18"}`, pinned deps)
- `frontend/package-lock.json` (commit after clean install)

**Definition of Done**:
- [x] `cp .env.example .env && npm run dev` produces zero missing-variable errors
- [x] `npm install --engine-strict` passes under Node v22.17.1
- [x] Dependency versions are pinned (no `^` or `~` on runtime deps)

**Success Criteria covered**: SC-SETUP-001

---

### WU-SETUP-8: Root Ignore + Cross-Stack Files
**Tasks**: T-SETUP-12
**Depends on**: WU-SETUP-4, WU-SETUP-7

**File scope**:
- `.gitignore` (new — covers Python, Node, IDE, env files, SQLite DB, build artefacts)

**Definition of Done**:
- [x] `git status` after a fresh `pip install` + `npm install` + `uvicorn` start shows zero untracked artefacts
- [x] `.env` (not `.env.example`) is ignored

**Success Criteria covered**: SC-SETUP-002

---

### WU-SETUP-9: End-to-End Verification
**Tasks**: T-SETUP-13
**Depends on**: WU-SETUP-8

**File scope**:
- `README.md` (new or modify — documents the verified steps)

**Definition of Done**:
- [x] Fresh clone → `alembic upgrade head` → `uvicorn` start → `GET /health` 200 → `npm install && npm run dev` clean console — all complete in under 10 minutes
- [x] Manual FK-violation insert is rejected by SQLite

**Success Criteria covered**: SC-SETUP-001, SC-SETUP-003
