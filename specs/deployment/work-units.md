# Module Work Units: Dockerization & Seed Data

**Module**: `deployment` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Tasks**: [tasks.md](tasks.md)

---

## Dependency Graph

### Upstream (must be 100% complete — no stubs)
- **Project Setup** WU-SETUP-9
- **Permissions** WU-PERM-1..WU-PERM-5
- **Roles** WU-ROLE-1..WU-ROLE-6
- **Users** WU-USR-1..WU-USR-8
- **Authentication** WU-AUTH-1..WU-AUTH-9
- **Accounts** WU-ACCT-1..WU-ACCT-6
- **Contacts** WU-CONT-1..WU-CONT-6
- **Opportunities** WU-OPP-1..WU-OPP-6
- **Leads** WU-LEAD-1..WU-LEAD-9
- **Activities** WU-ACT-1..WU-ACT-7

### Downstream
- **None.** Final module.

### Internal sequence
```
WU-DEPLOY-1 ─┐
              ├──► WU-DEPLOY-3 ────────────────────────────────────────┐
WU-DEPLOY-2 ─┘                                                          │
WU-DEPLOY-4 ──► WU-DEPLOY-5 ──► WU-DEPLOY-6 ──► WU-DEPLOY-7             │
                                            └──────────────────────────┴──► WU-DEPLOY-8
```

---

## Work Units

### WU-DEPLOY-1: Backend Dockerfile
**Tasks**: T-DEPLOY-1
**Depends on**: All 9 CRM modules' migrations finalised
**Parallelizable with**: WU-DEPLOY-2, WU-DEPLOY-4

**File scope**:
- `backend/Dockerfile` (new — Python 3.11-slim multi-stage if useful)
- `backend/.dockerignore` (new)
- `backend/scripts/entrypoint.sh` (new — `alembic upgrade head && uvicorn ...`)

**Definition of Done**:
- [ ] Build succeeds: `docker build -t crm-backend ./backend`
- [ ] Image runs migrations on container start, then starts uvicorn on port 8000
- [ ] `.dockerignore` excludes `.venv`, `__pycache__`, local SQLite files, `.env`
- [ ] Image size reasonable (Python slim base, layer caching for deps)

**Success Criteria covered**: SC-DEPLOY-001

---

### WU-DEPLOY-2: Frontend Dockerfile
**Tasks**: T-DEPLOY-2
**Depends on**: All 9 CRM modules' frontend pages finalised
**Parallelizable with**: WU-DEPLOY-1, WU-DEPLOY-4

**File scope**:
- `frontend/Dockerfile` (new — multi-stage: Node v22.17.1 build → static-serve runtime, e.g., nginx-alpine)
- `frontend/.dockerignore` (new)
- `frontend/nginx.conf` (new — SPA fallback to `index.html`)

**Definition of Done**:
- [ ] Build succeeds: `docker build -t crm-frontend ./frontend`
- [ ] Production build uses pinned Node v22.17.1
- [ ] Runtime image serves built assets + falls back to `index.html` for client-side routes
- [ ] `.dockerignore` excludes `node_modules`, `.env`

**Success Criteria covered**: SC-DEPLOY-001

---

### WU-DEPLOY-3: docker-compose
**Tasks**: T-DEPLOY-3
**Depends on**: WU-DEPLOY-1, WU-DEPLOY-2

**File scope**:
- `docker-compose.yml` (new)
- `.env.example` (new — top-level, references both backend + frontend vars)

**Definition of Done**:
- [ ] Two services: `backend`, `frontend` on a shared `crm` network
- [ ] Named volume (e.g., `crm_db_data`) mounted to the backend's SQLite file path
- [ ] Backend service waits/healthchecks before frontend serves traffic
- [ ] Env vars wired through and match Project Setup's `.env.example` contracts
- [ ] `docker compose up` from a clean checkout reaches usable state in under 3 minutes

**Success Criteria covered**: SC-DEPLOY-001, SC-DEPLOY-002

---

### WU-DEPLOY-4: Seed Script
**Tasks**: T-DEPLOY-4
**Depends on**: All 9 CRM modules' service layers complete (no stubs — script calls real `create_*` and Leads' `convert_*` functions)
**Parallelizable with**: WU-DEPLOY-1, WU-DEPLOY-2

**File scope**:
- `backend/app/scripts/__init__.py` (new)
- `backend/app/scripts/seed.py` (new — `seed_all()`)

**Definition of Done**:
- [ ] Seeds: 3 demo Users (one per system role), 50+ Accounts, 50+ Contacts, 50+ Opportunities covering ALL 5 stages, 50+ Leads covering ALL 4 statuses (incl. ≥1 real atomically-converted Lead), 50+ Activities covering ALL 3 types with mix of single + dual-linked
- [ ] Each row created via the owning module's real service function (NOT direct SQL inserts)
- [ ] Idempotent: re-running does not double-insert (check-then-skip on natural keys)
- [ ] Completes in under 30 seconds against an empty DB

**Success Criteria covered**: SC-DEPLOY-003, SC-DEPLOY-004

---

### WU-DEPLOY-5: Clear Function
**Tasks**: T-DEPLOY-5
**Depends on**: WU-DEPLOY-4

**File scope**:
- `backend/app/scripts/seed.py` (modify — add `clear_all()`)

**Definition of Done**:
- [ ] Deletes all rows from: `activities`, `leads`, `opportunities`, `contacts`, `accounts` (in FK-respecting order)
- [ ] ALSO deletes `users WHERE email NOT IN (the 3 demo seed emails)` — matches deployment/plan.md:31,56
- [ ] PRESERVES: `permissions` catalogue, `roles` (all 3 system + any custom), the 3 demo Users
- [ ] After `clear_all()`, the 3 demo Users can still log in
- [ ] Runs in a single transaction (rolls back on any error)

**Success Criteria covered**: SC-DEPLOY-004

---

### WU-DEPLOY-6: Seed Endpoints
**Tasks**: T-DEPLOY-6
**Depends on**: WU-DEPLOY-4, WU-DEPLOY-5, Authentication WU-AUTH-3, Permissions WU-PERM-1 (catalogue must already include `seed:manage`)

**File scope**:
- `backend/app/routers/seed.py` (new — `POST /seed`, `DELETE /seed`)
- `backend/app/main.py` (modify — register router)
- (Note: the `seed:manage` permission code is added up-front in Permissions WU-PERM-1's seed migration, per deployment/plan.md:54 — NOT bolted on here in a later migration)

**Definition of Done**:
- [ ] `seed:manage` permission code is part of the Permissions WU-PERM-1 seed catalogue (assigned to Admin role in Roles WU-ROLE-1 seed)
- [ ] `DELETE /seed` gated by `require_permission("seed:manage")` — non-Admin → 403
- [ ] `POST /seed` gated by `require_permission("seed:manage")` (Admin only; document any dev-mode bypass)
- [ ] Endpoints stream/return a summary (per-entity counts created/skipped)
- [ ] Permissions catalogue-consistency test (WU-PERM-5) still passes with `seed:manage` included

**Success Criteria covered**: SC-DEPLOY-003, SC-DEPLOY-004

---

### WU-DEPLOY-7: Frontend Admin Page
**Tasks**: T-DEPLOY-7
**Depends on**: WU-DEPLOY-6

**File scope**:
- `frontend/src/features/admin/SeedPage.tsx` (new)
- `frontend/src/features/admin/api.ts` (new — `useSeed`, `useClear`)
- `frontend/src/routes/index.tsx` (modify — register `/admin/seed` behind `RequirePermission("seed:manage")`)

**Definition of Done**:
- [ ] "Seed demo data" button → `POST /seed` → renders summary panel with per-entity counts
- [ ] "Clear all data" button shows a destructive confirmation dialog (typed-confirmation, e.g., "CLEAR")
- [ ] Visible only to Admin (route + UI both check)
- [ ] Matches mock under `mocks/seed-manager.html`

**Success Criteria covered**: SC-DEPLOY-003

---

### WU-DEPLOY-8: Integration Tests
**Tasks**: T-DEPLOY-8
**Depends on**: WU-DEPLOY-3, WU-DEPLOY-6

**File scope**:
- `backend/tests/test_deployment_integration.py` (new)
- `scripts/test-compose.sh` (new — drives docker compose for the persistence test)

**Definition of Done**:
- [ ] Test (manual or CI-script): `docker compose up` → `POST /seed` → `docker compose restart` → data preserved
- [ ] Test: `docker compose down` (no `-v`) → `up` → data preserved
- [ ] Test: `docker compose down -v` → `up` → DB empty
- [ ] Test: `POST /seed` twice → counts identical (idempotency)
- [ ] Test: `DELETE /seed` → CRM tables empty; permissions/roles/3 demo users intact; demo users still log in
- [ ] Test: seeded Leads include all 4 statuses + ≥1 real converted Lead with valid `converted_opportunity_id`
- [ ] Test: seeded Opportunities cover all 5 stages; Activities cover all 3 types with single + dual-linked mix
- [ ] Test: referential-integrity spot check — every seeded `converted_opportunity_id` references an existing opportunity

**Success Criteria covered**: SC-DEPLOY-001, SC-DEPLOY-002, SC-DEPLOY-003, SC-DEPLOY-004
