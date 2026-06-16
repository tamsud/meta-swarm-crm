# Module Tasks: Foundation Enhancements

**Module**: `foundation-enhancements` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Prerequisites

| Prerequisite | Status | Notes |
|---|---|---|
| Project Setup complete | ✅ | FastAPI app, folder structure, health endpoint exist |
| Permissions module complete | ✅ | `/permissions` router exists to update |
| Roles module complete | ✅ | `/roles` router exists to update |

---

## Task List

### T-FE-1: Create API Response Envelope Schemas

**Description**: Define Pydantic schemas for the standardized response envelope.

**Files**:
- `backend/app/schemas/response.py` (new)
- `backend/app/schemas/__init__.py` (modify — export new schemas)

**Acceptance Criteria**:
- [ ] `ApiResponse[T]` generic schema with `success: bool`, `data: T`
- [ ] `PaginatedMeta` schema with `count`, `total`, `offset`, `limit`
- [ ] `PaginatedResponse[T]` schema with `success`, `data: list[T]`, `meta: PaginatedMeta`
- [ ] `ApiError` schema with `code`, `message`, and optional extra fields
- [ ] `ErrorResponse` schema with `success: Literal[False]`, `error: ApiError`

**Estimated effort**: Small

---

### T-FE-2: Create Response Envelope Middleware

**Description**: Implement FastAPI middleware that wraps all responses in the envelope and handles exceptions uniformly.

**Files**:
- `backend/app/middleware/__init__.py` (new)
- `backend/app/middleware/response_envelope.py` (new)
- `backend/app/main.py` (modify — register middleware)

**Acceptance Criteria**:
- [ ] Middleware wraps successful responses in `{"success": true, "data": ...}`
- [ ] Middleware catches `AppException` and formats as `{"success": false, "error": ...}`
- [ ] Middleware catches `RequestValidationError` and formats as validation error envelope
- [ ] Middleware catches unhandled exceptions and formats as 500 error envelope
- [ ] Middleware preserves original status codes
- [ ] Middleware skips wrapping for `/health` and `/docs` endpoints

**Estimated effort**: Medium

---

### T-FE-3: Update Existing Routers for Envelope

**Description**: Simplify existing routers to return raw data, letting middleware handle wrapping.

**Files**:
- `backend/app/routers/permissions.py` (modify)
- `backend/app/routers/roles.py` (modify)

**Acceptance Criteria**:
- [ ] Routers return raw data/lists, not manually wrapped responses
- [ ] `_map_exception_to_http` helper removed from roles.py (middleware handles it)
- [ ] Exception handling simplified — just raise `AppException`, don't convert to `HTTPException`
- [ ] List endpoints return tuple `(data, total)` or similar for pagination meta
- [ ] All existing tests still pass after refactor

**Estimated effort**: Medium

---

### T-FE-4: Create Backend Dockerfile

**Description**: Create a development Dockerfile for the backend service.

**Files**:
- `backend/Dockerfile` (new)

**Acceptance Criteria**:
- [ ] Uses Python 3.11+ base image
- [ ] Installs dependencies from `requirements.txt`
- [ ] Sets working directory to `/app`
- [ ] Runs Alembic migrations on startup
- [ ] Starts uvicorn with `--reload` for live reload
- [ ] Exposes port 8000

**Estimated effort**: Small

---

### T-FE-5: Create Frontend Dockerfile

**Description**: Create a development Dockerfile for the frontend service.

**Files**:
- `frontend/Dockerfile` (new)

**Acceptance Criteria**:
- [ ] Uses Node 22 base image
- [ ] Installs dependencies with npm
- [ ] Sets working directory to `/app`
- [ ] Runs `npm run dev` with `--host 0.0.0.0` for Docker accessibility
- [ ] Exposes Vite dev server port (5173)

**Estimated effort**: Small

---

### T-FE-6: Create docker-compose.yml

**Description**: Create docker-compose file to orchestrate both services.

**Files**:
- `docker-compose.yml` (new)

**Acceptance Criteria**:
- [ ] Defines `backend` service using `backend/Dockerfile`
- [ ] Defines `frontend` service using `frontend/Dockerfile`
- [ ] Backend exposes port 8000
- [ ] Frontend exposes port 5173
- [ ] Source directories mounted as volumes for live reload
- [ ] Frontend depends on backend (startup order)
- [ ] Environment variables configurable via `.env` file
- [ ] `docker compose up` starts both services successfully

**Estimated effort**: Small

---

### T-FE-7: Create Root README

**Description**: Create comprehensive project README at repository root.

**Files**:
- `README.md` (new)

**Acceptance Criteria**:
- [ ] Project name and description
- [ ] Tech stack overview (backend + frontend)
- [ ] Quick start with Docker (`docker compose up`)
- [ ] Quick start without Docker (native setup)
- [ ] Link to `backend/README.md` and `frontend/README.md`
- [ ] Link to API documentation (`/docs`)
- [ ] Project structure overview
- [ ] Contributing guidelines placeholder

**Estimated effort**: Small

---

### T-FE-8: Create/Update Backend and Frontend READMEs

**Description**: Create backend README and update frontend README with project-specific content.

**Files**:
- `backend/README.md` (new)
- `frontend/README.md` (modify — replace Vite boilerplate)

**Acceptance Criteria**:
- [ ] Backend README: setup instructions, env vars, migrations, running server, API docs
- [ ] Frontend README: setup instructions, env vars, folder structure, running dev server
- [ ] Both reference the root README for project overview
- [ ] Both include Docker and native setup instructions

**Estimated effort**: Small

---

### T-FE-9: Move Mocks Folder

**Description**: Relocate `mocks/` folder under `specs/` for better organization.

**Files**:
- `mocks/*` → `specs/mocks/*` (move)
- `CLAUDE.md` (modify — update reference)

**Acceptance Criteria**:
- [ ] All files moved from `mocks/` to `specs/mocks/`
- [ ] `mocks/` folder deleted from root
- [ ] `CLAUDE.md` reference updated from `mocks/` to `specs/mocks/`
- [ ] Git history preserved (use `git mv`)

**Estimated effort**: Small

---

### T-FE-10: Create Basic Seed Script

**Description**: Create idempotent seed script for minimal test data.

**Files**:
- `backend/app/seed.py` (new)

**Acceptance Criteria**:
- [ ] Seeds 3-5 custom roles with various permission combinations
- [ ] Idempotent — running twice doesn't create duplicates
- [ ] Runnable via `python -m app.seed`
- [ ] Outputs summary of created/skipped records
- [ ] Works against empty database (post-migration)

**Estimated effort**: Small

---

### T-FE-11: Integration Tests for Envelope

**Description**: Add tests verifying the envelope structure for all response types.

**Files**:
- `backend/tests/test_response_envelope.py` (new)

**Acceptance Criteria**:
- [ ] Test: successful GET returns `{"success": true, "data": ...}`
- [ ] Test: successful POST returns `{"success": true, "data": ...}`
- [ ] Test: list endpoint returns `{"success": true, "data": [...], "meta": {...}}`
- [ ] Test: AppException returns `{"success": false, "error": {"code": ..., "message": ...}}`
- [ ] Test: validation error returns `{"success": false, "error": {"code": "VALIDATION_ERROR", ...}}`
- [ ] Test: `/health` endpoint NOT wrapped in envelope

**Estimated effort**: Medium

---

## Task Sequencing

```
T-FE-1 (Schemas) ──► T-FE-2 (Middleware) ──► T-FE-3 (Update Routers) ──► T-FE-11 (Tests)
                                                                              │
T-FE-4 (Backend Dockerfile) ──┐                                               │
T-FE-5 (Frontend Dockerfile) ─┼──► T-FE-6 (docker-compose) ───────────────────┤
                              │                                               │
T-FE-7 (Root README) ─────────┼──► T-FE-8 (Backend/Frontend READMEs) ─────────┤
                              │                                               │
T-FE-9 (Move Mocks) ──────────┘                                               │
                                                                              │
T-FE-10 (Seed Script) ────────────────────────────────────────────────────────┘
```

**Parallelizable groups**:
- T-FE-4, T-FE-5, T-FE-7, T-FE-9 can run in parallel (independent files)
- T-FE-1 must complete before T-FE-2
- T-FE-2 must complete before T-FE-3
- T-FE-3 must complete before T-FE-11

---

## Estimated Total Effort

| Category | Tasks | Effort |
|---|---|---|
| API Envelope | T-FE-1, T-FE-2, T-FE-3, T-FE-11 | Medium |
| Docker | T-FE-4, T-FE-5, T-FE-6 | Small |
| Documentation | T-FE-7, T-FE-8 | Small |
| Organization | T-FE-9 | Small |
| Seed Data | T-FE-10 | Small |

**Overall**: Medium complexity, ~2-3 hours implementation time
