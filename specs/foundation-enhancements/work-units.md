# Module Work Units: Foundation Enhancements

**Module**: `foundation-enhancements` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Tasks**: [tasks.md](tasks.md)

---

## Dependency Graph

### Upstream
- **Project Setup** (complete) — FastAPI app, folder structure exist
- **Permissions** WU-PERM-3 (complete) — `/permissions` router to update
- **Roles** WU-ROLE-4 (complete) — `/roles` router to update

### Downstream
- All future CRM modules — must follow envelope pattern
- **Deployment** — extends dev Docker and seed script

### Internal Sequence
```
WU-FE-1 ──► WU-FE-2 ──┬──► WU-FE-6
                       │
WU-FE-3 ──────────────┤
                       │
WU-FE-4 ──────────────┤
                       │
WU-FE-5 ──────────────┘
```

---

## Work Units

### WU-FE-1: Response Envelope Schemas + Middleware
**Tasks**: T-FE-1, T-FE-2
**Depends on**: Project Setup (complete)

**File scope**:
- `backend/app/schemas/response.py` (new)
- `backend/app/schemas/__init__.py` (modify)
- `backend/app/middleware/__init__.py` (new)
- `backend/app/middleware/response_envelope.py` (new)
- `backend/app/main.py` (modify — register middleware)

**Definition of Done**:
- [ ] `ApiResponse[T]` generic with `success: Literal[True]`, `data: T`
- [ ] `PaginatedResponse[T]` with `meta: PaginatedMeta` containing `count`, `total`, `offset`, `limit`
- [ ] `ErrorResponse` with `success: Literal[False]`, `error: ApiError`
- [ ] Middleware wraps all 2xx responses in success envelope
- [ ] Middleware catches `AppException` and returns error envelope with correct status code
- [ ] Middleware catches `RequestValidationError` and returns 422 with `VALIDATION_ERROR` code
- [ ] Middleware catches unhandled exceptions and returns 500 with `INTERNAL_ERROR` code (wraps 5xx in envelope per FR-FE-003)
- [ ] Middleware skips `/health`, `/docs`, `/openapi.json` endpoints
- [ ] Middleware registered in `main.py`

**Success Criteria covered**: SC-FE-001 (partial)

---

### WU-FE-2: Update Routers + Envelope Tests
**Tasks**: T-FE-3, T-FE-11
**Depends on**: WU-FE-1

**File scope**:
- `backend/app/routers/permissions.py` (modify)
- `backend/app/routers/roles.py` (modify)
- `backend/tests/test_response_envelope.py` (new)
- `backend/tests/test_permissions_router.py` (modify — update assertions)
- `backend/tests/test_roles_integration.py` (modify — update assertions)

**Definition of Done**:
- [ ] `permissions.py` returns raw `list[PermissionResponse]`, no manual wrapping
- [ ] `roles.py` returns raw data; `_map_exception_to_http` removed; raises `AppException` directly
- [ ] List endpoints return data + total count for pagination meta
- [ ] Existing router tests updated to expect envelope structure
- [ ] New envelope tests verify: success single, success list with meta, AppException error, validation error
- [ ] Test verifies empty list returns `{"success": true, "data": [], "meta": {"count": 0, ...}}`
- [ ] Test verifies unhandled exception returns `{"success": false, "error": {"code": "INTERNAL_ERROR", ...}}` with 500 status
- [ ] Test verifies `/health` is NOT wrapped

**Success Criteria covered**: SC-FE-001

---

### WU-FE-3: Development Docker Setup
**Tasks**: T-FE-4, T-FE-5, T-FE-6
**Depends on**: Project Setup (complete)

**File scope**:
- `backend/Dockerfile` (new)
- `frontend/Dockerfile` (new)
- `docker-compose.yml` (new)

**Definition of Done**:
- [ ] `backend/Dockerfile`: Python 3.11+, installs deps, runs migrations on start, uvicorn with --reload
- [ ] `frontend/Dockerfile`: Node 22, installs deps, runs `npm run dev -- --host 0.0.0.0`
- [ ] `docker-compose.yml`: defines both services, exposes ports 8000 and 5173
- [ ] Source directories mounted as volumes for live reload
- [ ] `docker compose up` starts both services successfully
- [ ] `GET /health` returns 200 from containerized backend
- [ ] Frontend dev server accessible and shows app shell
- [ ] **Verify backend auto-reload**: Modify a `.py` file → uvicorn logs show reload → endpoint reflects change
- [ ] **Verify frontend HMR**: Modify a `.tsx` file → browser updates without full page reload

**Success Criteria covered**: SC-FE-002

---

### WU-FE-4: Documentation + Organization
**Tasks**: T-FE-7, T-FE-8, T-FE-9
**Depends on**: None (parallel with other WUs)

**File scope**:
- `README.md` (new)
- `backend/README.md` (new)
- `frontend/README.md` (modify)
- `mocks/*` → `specs/mocks/*` (move)
- `CLAUDE.md` (modify)

**Definition of Done**:
- [ ] Root `README.md`: project name, description, tech stack, Docker quick start, native quick start, links to sub-READMEs
- [ ] `backend/README.md`: setup, env vars (`.env.example` reference), migrations, server start, API docs link
- [ ] `frontend/README.md`: setup, env vars, folder structure, dev server start (replaces Vite boilerplate)
- [ ] `mocks/` moved to `specs/mocks/` using `git mv`
- [ ] `CLAUDE.md` reference updated from `mocks/` to `specs/mocks/`
- [ ] All files in `specs/mocks/` accessible after move

**Success Criteria covered**: SC-FE-003

---

### WU-FE-5: Basic Seed Script
**Tasks**: T-FE-10
**Depends on**: WU-FE-1, Permissions, Roles (complete)

**File scope**:
- `backend/app/seed.py` (new)

**Definition of Done**:
- [ ] Script creates 3-5 custom roles with varied permission sets
- [ ] Idempotent — checks for existing data before inserting
- [ ] Runnable via `python -m app.seed` from backend directory
- [ ] Outputs summary: "Created X roles, skipped Y (already exist)"
- [ ] Works against freshly migrated empty database
- [ ] Created roles have valid, resolvable permission associations

**Success Criteria covered**: SC-FE-004

---

### WU-FE-6: Final Integration Verification
**Tasks**: (no new tasks — verification of all WUs)
**Depends on**: WU-FE-1, WU-FE-2, WU-FE-3, WU-FE-4, WU-FE-5

**File scope**: None (verification only)

**Definition of Done**:
- [ ] `docker compose up` from clean checkout — both services start
- [ ] `GET /health` returns `{"status": "ok", ...}` (not wrapped — excluded)
- [ ] `GET /permissions` returns `{"success": true, "data": [...], "meta": {...}}`
- [ ] `GET /roles` returns `{"success": true, "data": [...], "meta": {...}}`
- [ ] `POST /roles` with invalid data returns `{"success": false, "error": {"code": "VALIDATION_ERROR", ...}}`
- [ ] `PATCH /roles/1` returns `{"success": false, "error": {"code": "SYSTEM_ROLE_IMMUTABLE", ...}}`
- [ ] Seed script runs successfully inside Docker container
- [ ] All READMEs render correctly in GitHub/viewer

**Success Criteria covered**: SC-FE-001, SC-FE-002, SC-FE-003, SC-FE-004

---

## Execution Summary

| WU | Description | Est. Time | Dependencies |
|----|-------------|-----------|--------------|
| WU-FE-1 | Response Envelope Schemas + Middleware | 45 min | None |
| WU-FE-2 | Update Routers + Envelope Tests | 45 min | WU-FE-1 |
| WU-FE-3 | Development Docker Setup | 30 min | None (parallel) |
| WU-FE-4 | Documentation + Organization | 30 min | None (parallel) |
| WU-FE-5 | Basic Seed Script | 20 min | WU-FE-1 |
| WU-FE-6 | Final Integration Verification | 15 min | All |

**Total estimated time**: ~3 hours

**Parallelization opportunity**: WU-FE-3 and WU-FE-4 can run in parallel with WU-FE-1/WU-FE-2 sequence.
