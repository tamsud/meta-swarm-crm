# Module Specification: Dockerization & Seed Data

**Module**: `deployment` | **Created**: 2026-06-16 | **Status**: Draft

---

## Module Scope & Objectives

Deployment is the **closing module** — it adds no new CRM entity and changes no other module's business rules, but it depends on all 9 CRM modules (and [Project Setup](../project-setup/spec.md)) being complete. It containerizes the backend and frontend for reproducible deployment, and provides a seed-data operation that populates every module's tables with realistic demo data (50+ records per entity) for development, demos, and QA.

**In scope**:
- Dockerfiles for `backend/` (Python 3.11+, installs dependencies, runs the FastAPI app via uvicorn) and `frontend/` (builds the Vite/React app, serves it via a production web server).
- `docker-compose.yml` orchestrating both services, with the database stored in a **named Docker volume** so data persists across `docker compose restart` and survives `docker compose down` (without `-v`).
- A seed-data script/endpoint that creates, idempotently, **50+ records per entity** across every module in scope: Users (with Role assignments across Admin/Manager/Sales Rep), Accounts, Contacts, Leads (across all 4 statuses, including converted ones), Opportunities (across all 5 stages), and Activities (across all 3 types, linked to a realistic mix of Contacts/Opportunities).
- A "clear all data" companion operation for resetting to an empty state, mirroring the reference CRM's demo/dev tooling.

**Out of scope**: production-grade orchestration (Kubernetes, autoscaling), CI/CD pipeline definitions, TLS/reverse-proxy configuration, multi-environment (staging/prod) compose overlays — all explicitly deferred beyond this v1 scope.

**Objective**: Let anyone — a new developer, a stakeholder running a demo, or a QA engineer — run `docker compose up`, seed realistic data with one command, and have a fully populated, RBAC-correct CRM running locally within minutes, with no manual data entry.

---

## User Stories

### User Story 9 - Docker Containerization with Persistent Data (Priority: P1, post-CRM-modules)

A developer or operator runs the entire stack with `docker compose up`, without installing Python or Node locally. Data survives container restarts.

**Why this priority**: Once all 9 CRM modules exist, the platform needs a reproducible way to run it as a unit — this is the natural closing step before the platform is considered demo/deploy-ready.

**Independent Test**: `docker compose up` from a clean checkout → both services reachable on their configured ports → use the CRM, create a record → `docker compose restart` → the record is still present → `docker compose down` (no `-v`) → `docker compose up` again → the record is still present → `docker compose down -v` → `docker compose up` → the database is empty again.

**Acceptance Scenarios**:

1. **Given** `docker-compose.yml` exists, **When** `docker compose up` is run from a clean checkout, **Then** both frontend and backend start and are reachable on their configured ports with no manual steps beyond the one command.
2. **Given** a running stack with data, **When** containers are restarted (`docker compose restart`), **Then** all database content is preserved.
3. **Given** `docker compose down` without `-v`, **When** the stack is brought back up, **Then** data is still present.
4. **Given** `docker compose down -v`, **When** the stack is brought back up, **Then** the database starts empty.

### User Story 10 - Seed Data Across All Modules (Priority: P1, post-CRM-modules)

A developer or demo presenter seeds the database with a large, realistic dataset spanning every module in one operation, then can clear it just as easily.

**Why this priority**: Manually creating 50+ records per entity across 7 data-bearing modules to demo or test the platform is impractical; an automated, idempotent seed operation is required the moment all modules exist.

**Independent Test**: Call the seed operation against an empty database → verify each entity type has at least 50 records (and the 3 demo Users exist with correct roles) → call it again → verify it is idempotent (no duplication) → call the clear operation → verify every CRM table (except Permissions/Roles, which remain as system catalogue/seed data) is empty.

**Acceptance Scenarios**:

1. **Given** an empty database (post-migration, pre-seed), **When** the seed operation is invoked, **Then** at least 50 Accounts, 50 Contacts, 50 Leads (spread across all 4 statuses, with at least one already converted), 50 Opportunities (spread across all 5 stages), and 50 Activities (spread across all 3 types) are created, plus the 3 demo Users (admin/manager/sales) with correct Role assignments.
2. **Given** seeded data, **When** the seed operation is invoked a second time, **Then** it is idempotent — no duplicate records are created and counts remain stable.
3. **Given** seeded data, **When** the clear operation is invoked (Admin only, behind a confirmation step on the frontend), **Then** all CRM records (Accounts, Contacts, Leads, Opportunities, Activities, and non-Admin/seed Users) are removed, while the Permissions catalogue and the 3 system Roles remain intact.
4. **Given** seeded Leads, **When** inspected, **Then** referential integrity holds end-to-end — every seeded Opportunity created via a "converted" Lead has a real, resolvable Account and Contact, exactly as the live conversion transaction would produce.

### Edge Cases

- What happens if the Docker volume already exists from a previous run? → The container starts normally and the existing data is preserved — this is the intended persistence behavior, not an error.
- What happens if the seed operation is run against a database that already has hand-created (non-seed) data? → Seed data is added alongside it; the operation does not delete or overwrite pre-existing records it didn't create itself (idempotency is keyed on the seed dataset's own deterministic identifiers/emails, not a blanket wipe).
- What happens to seeded Leads' `created_by_user_id`? → Distributed realistically across the 3 seeded Sales-Rep-equivalent users (or a dedicated seed Sales Rep), so that the Leads/Activities ownership-scoping rules ([Leads spec](../leads/spec.md) FR-LEAD-005, [Activities spec](../activities/spec.md) FR-ACT-006) have real, demonstrable data to exercise.

---

## Functional Requirements

- **FR-DEPLOY-001**: A `docker-compose.yml` MUST exist at the project root that starts both the frontend and backend services with one command.
- **FR-DEPLOY-002**: The database MUST be stored in a named Docker volume (not bind-mounted to a host path) so that data persists across `docker compose restart` and `docker compose down` (without `-v`).
- **FR-DEPLOY-003**: The frontend Dockerfile MUST build the Vite/React app and serve the resulting static assets via a production web server.
- **FR-DEPLOY-004**: The backend Dockerfile MUST install Python dependencies and start the FastAPI server via uvicorn, applying pending Alembic migrations on container startup.
- **FR-DEPLOY-005**: System MUST provide a seed-data operation that creates at least 50 records for each of: Accounts, Contacts, Leads, Opportunities, Activities, plus the 3 demo Users with correct Role assignments — all referentially consistent (every Contact/Opportunity FK resolves, every Activity satisfies the link-required constraint).
- **FR-DEPLOY-006**: The seed-data operation MUST be idempotent — repeated invocations MUST NOT create duplicate records.
- **FR-DEPLOY-007**: System MUST provide a companion clear-data operation (Admin-permission-gated) that removes all seeded/created CRM records while preserving the Permissions catalogue and system Roles.
- **FR-DEPLOY-008**: Seeded Leads MUST include examples of every status (`new`, `contacted`, `qualified`, `lost`) and at least one already-converted Lead with a valid `converted_opportunity_id`.
- **FR-DEPLOY-009**: Seeded Opportunities MUST include examples of every stage (`prospecting`, `proposal`, `negotiation`, `closed-won`, `closed-lost`).
- **FR-DEPLOY-010**: Seeded Activities MUST include examples of every type (`call`, `email`, `meeting`) and a realistic mix of Contact-only, Opportunity-only, and dual-linked records.

## Key Entities

*(None new — this module writes into every other module's existing tables via their own service-layer create functions; it owns only the seed-data definition/fixture data itself and the Docker/compose configuration files.)*

---

## Success Criteria

- **SC-DEPLOY-001**: `docker compose up` starts the full stack from a clean environment in under 3 minutes.
- **SC-DEPLOY-002**: Restarting Docker containers (without `-v`) preserves 100% of previously created CRM records.
- **SC-DEPLOY-003**: Seeding produces at least 50 records per entity (Accounts, Contacts, Leads, Opportunities, Activities) in under 30 seconds, end-to-end, with zero referential-integrity violations.
- **SC-DEPLOY-004**: Re-running the seed operation any number of times never doubles the record counts.

---

## Dependencies on Other Modules

| Dependency | Direction | Reason |
|---|---|---|
| [Project Setup](../project-setup/spec.md) | Deployment **depends on** | Dockerfiles wrap that module's exact backend/frontend scaffold and toolchain versions |
| [Permissions](../permissions/spec.md), [Roles](../roles/spec.md), [Users](../users/spec.md), [Authentication](../authentication/spec.md), [Accounts](../accounts/spec.md), [Contacts](../contacts/spec.md), [Opportunities](../opportunities/spec.md), [Leads](../leads/spec.md), [Activities](../activities/spec.md) | Deployment **depends on** all 9 | The seed operation calls each module's own service-layer create functions (never raw SQL) to guarantee every seeded record obeys that module's validation rules (e.g., seeded Leads still go through the real state machine to reach "qualified" before being converted) |
| None | **Depended on by** none | Deployment is the terminal module — nothing in the system depends on it being built |

**Build order implication**: Deployment is implemented **last**, only once all 9 CRM modules and Project Setup are complete and stable.
