# Module Specification: Foundation Enhancements

**Module**: `foundation-enhancements` | **Created**: 2026-06-17 | **Status**: Draft

---

## Module Scope & Objectives

Foundation Enhancements extends [Project Setup](../project-setup/spec.md) with infrastructure that improves developer experience during iterative module development: a standardized API response envelope, development-mode Docker containers, project documentation, and organizational cleanup. This module sits between Project Setup (which establishes the scaffold) and Deployment (which provides production-grade containerization and full seed data).

**In scope**:
- A **standardized API response envelope** that wraps all success and error responses in a consistent structure, enabling frontend code to handle responses uniformly regardless of endpoint.
- **Development-mode Docker setup** (`Dockerfile` + `docker-compose.yml`) for running the backend and frontend locally without installing Python or Node — focused on developer convenience, not production optimization.
- **Project documentation**: root `README.md` (project overview, quick start), `backend/README.md` (backend-specific setup, API docs), `frontend/README.md` (frontend-specific setup, component conventions).
- **Organizational cleanup**: move `mocks/` folder under `specs/` to co-locate UI reference materials with specifications.
- **Basic seed script**: minimal seed data (3-5 records per entity) for development verification — enough to confirm CRUD works, not the full 50+ records per entity reserved for the [Deployment module](../deployment/spec.md).

**Out of scope** (explicitly deferred to Deployment module):
- Production-optimized multi-stage Dockerfiles
- Full seed data (50+ records per entity with comprehensive status/stage coverage)
- Clear/reset data operation
- Production web server configuration (nginx, etc.)
- Docker volume persistence guarantees (Deployment FR-DEPLOY-002)

**Objective**: Let a developer run `docker compose up` at any point during iterative module development, see the API return consistent response shapes, and have just enough seed data to manually verify the system works — without waiting for all 9 CRM modules to be complete.

---

## User Stories

### User Story FE-1 - Consistent API Response Structure (Priority: P1)

A frontend developer integrating with the API needs every endpoint to return the same response shape, so that a single response handler works everywhere without per-endpoint special cases.

**Why this priority**: Without a standard envelope, the frontend must handle success responses (raw data) differently from error responses (nested `detail` object), leading to duplicated error-handling logic and inconsistent UX.

**Independent Test**: Call any successful endpoint → response matches `{"success": true, "data": {...}}`. Call any endpoint that returns an error → response matches `{"success": false, "error": {"code": "...", "message": "...", ...}}`. No endpoint returns raw data or a non-envelope structure.

**Acceptance Scenarios**:

1. **Given** a successful `GET /roles` request, **When** the response is received, **Then** it has shape `{"success": true, "data": [...], "meta": {"count": N}}`.
2. **Given** a successful `POST /roles` request, **When** the response is received, **Then** it has shape `{"success": true, "data": {...}}` where `data` is the created resource.
3. **Given** a `POST /roles` request with invalid `permission_ids`, **When** the 400 response is received, **Then** it has shape `{"success": false, "error": {"code": "INVALID_PERMISSION_IDS", "message": "...", "invalid_ids": [...]}}`.
4. **Given** a `DELETE /roles/1` on a system role, **When** the 400 response is received, **Then** it has shape `{"success": false, "error": {"code": "SYSTEM_ROLE_IMMUTABLE", "message": "..."}}`.

### User Story FE-2 - Development Docker Environment (Priority: P1)

A developer without Python or Node installed locally can run `docker compose up` and have the full stack running for manual testing.

**Why this priority**: Not every team member has matching Python/Node versions installed; Docker provides a reproducible environment from day one of development, not just at the Deployment phase.

**Independent Test**: From a clean checkout, run `docker compose up` → backend reachable at configured port → frontend reachable at configured port → `GET /health` returns 200 → frontend loads without console errors.

**Acceptance Scenarios**:

1. **Given** `docker-compose.yml` exists, **When** `docker compose up` is run, **Then** both services start within 2 minutes.
2. **Given** running containers, **When** backend code changes, **Then** the backend auto-reloads (development mode).
3. **Given** running containers, **When** frontend code changes, **Then** Vite HMR updates the browser.
4. **Given** `docker compose down` followed by `docker compose up`, **Then** the stack restarts cleanly.

### User Story FE-3 - Project Documentation (Priority: P2)

A new developer cloning the repo can understand the project structure, run setup commands, and know where to find API documentation by reading the READMEs.

**Why this priority**: The current `frontend/README.md` is Vite boilerplate; no root or backend README exists. New developers waste time discovering setup steps that should be documented.

**Acceptance Scenarios**:

1. **Given** the root `README.md`, **When** a developer reads it, **Then** they understand the project purpose, tech stack, and how to run both backend and frontend (with and without Docker).
2. **Given** `backend/README.md`, **When** a developer reads it, **Then** they know how to install dependencies, run migrations, start the server, and access API docs.
3. **Given** `frontend/README.md`, **When** a developer reads it, **Then** they know how to install dependencies, start the dev server, and understand the folder structure.

### User Story FE-4 - Basic Seed Data for Development (Priority: P2)

A developer can seed minimal test data to verify CRUD operations work without manually creating records.

**Why this priority**: Manual record creation for every test cycle is tedious; even 3-5 records per entity lets a developer verify list views, detail views, and relationships work.

**Acceptance Scenarios**:

1. **Given** an empty database, **When** the seed script runs, **Then** at least 3 records exist for each implemented entity (Permissions, Roles currently).
2. **Given** seeded data, **When** the seed script runs again, **Then** it is idempotent (no duplicates).
3. **Given** seeded Roles, **When** inspected, **Then** they have valid permission associations.

---

## Functional Requirements

### API Response Envelope

- **FR-FE-001**: All successful responses (2xx) MUST return `{"success": true, "data": <payload>}` where `<payload>` is the resource or list of resources.
- **FR-FE-002**: List endpoints MUST include `"meta": {"count": N, "offset": M, "limit": L}` alongside `data` for pagination context.
- **FR-FE-003**: All error responses (4xx, 5xx) MUST return `{"success": false, "error": {"code": "<ERROR_CODE>", "message": "<human-readable>", ...extra}}`.
- **FR-FE-004**: The `error.code` field MUST use SCREAMING_SNAKE_CASE and match the service-layer exception's `error_code`.
- **FR-FE-005**: Existing routers (permissions, roles) MUST be updated to use the new envelope; new routers MUST use it from creation.

### Development Docker

- **FR-FE-006**: A `Dockerfile` MUST exist for the backend that installs dependencies and runs uvicorn in reload mode.
- **FR-FE-007**: A `Dockerfile` MUST exist for the frontend that installs dependencies and runs `npm run dev`.
- **FR-FE-008**: A `docker-compose.yml` MUST exist at the project root that starts both services with `docker compose up`.
- **FR-FE-009**: The backend container MUST apply Alembic migrations on startup before starting the server.
- **FR-FE-010**: The frontend container MUST expose Vite's dev server with HMR working through Docker.

### Documentation

- **FR-FE-011**: A root `README.md` MUST exist with: project name, description, tech stack summary, quick start (Docker and native), link to backend/frontend READMEs.
- **FR-FE-012**: `backend/README.md` MUST exist with: setup instructions, environment variables, running migrations, starting the server, API documentation access (`/docs`).
- **FR-FE-013**: `frontend/README.md` MUST be updated from Vite boilerplate to: project-specific setup, folder structure explanation, environment variables, running dev server.

### Organization

- **FR-FE-014**: The `mocks/` folder MUST be moved to `specs/mocks/` and any references in `CLAUDE.md` updated.

### Basic Seed Data

- **FR-FE-015**: A seed script MUST exist that creates minimal test data for all currently implemented modules (Permissions, Roles).
- **FR-FE-016**: The seed script MUST be idempotent — running it multiple times MUST NOT create duplicates.
- **FR-FE-017**: The seed script MUST be runnable via a documented command (e.g., `python -m app.seed` or a CLI command).

---

## Key Entities

*(None new — this module adds infrastructure and documentation, not business data. It touches existing routers/schemas to add the envelope wrapper.)*

---

## Success Criteria

- **SC-FE-001**: Every endpoint returns responses matching the standardized envelope schema — no raw data or inconsistent error shapes.
- **SC-FE-002**: `docker compose up` starts both services from a clean checkout in under 2 minutes.
- **SC-FE-003**: A new developer can go from clone to running stack by following only the root README.
- **SC-FE-004**: The seed script populates minimal test data for manual verification of implemented modules.

---

## Dependencies on Other Modules

| Dependency | Direction | Reason |
|---|---|---|
| [Project Setup](../project-setup/spec.md) | Foundation Enhancements **depends on** | Requires existing FastAPI app, folder structure, and base configuration |
| [Permissions](../permissions/spec.md) | Foundation Enhancements **depends on** | Envelope updates applied to existing `/permissions` router |
| [Roles](../roles/spec.md) | Foundation Enhancements **depends on** | Envelope updates applied to existing `/roles` router |
| All future CRM modules | **Pattern established by** | New routers must follow the envelope pattern established here |
| [Deployment](../deployment/spec.md) | **Depended on by** Deployment | Production Docker builds on dev Docker; full seed extends basic seed |

**Build order implication**: Foundation Enhancements can be built **now**, after Permissions and Roles are complete, without waiting for the remaining 7 CRM modules.
