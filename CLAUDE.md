# Project Instructions

This project uses [metaswarm](https://github.com/dsifry/metaswarm), a multi-agent orchestration framework for Claude Code.

## Project Vision

Build a multi-tenant-ready CRM SaaS platform covering the full sales workflow — lead capture through qualification, conversion, pipeline management, and engagement history — with role-based access control as a first-class, Admin-configurable capability rather than a hardcoded afterthought.

## Business Goals

- Give sales teams a single system of record for Accounts, Contacts, Leads, Opportunities, and Activities.
- Make authorization data-driven: three system-defined roles (Admin, Manager, Sales Rep) ship by default, but Admins can compose additional custom roles from a fixed permission catalogue without code changes.
- Preserve a clean, atomic Lead-to-Opportunity conversion as the critical funnel handoff — never a partial or duplicated record.
- Ship a modern, accessible (WCAG 2.1 AA), responsive frontend modeled on contemporary SaaS CRM products (Zoho, HubSpot, Salesforce Lightning, Linear).

## Project Phase

This repository is currently in a **specification phase** — there is no application code, package manifest, or test runner yet. Implementation proceeds **module-by-module**, one module at a time, against the documentation in `specs/`.

Because no tech stack has been chosen for actual implementation yet, the usual metaswarm quality gates (coverage thresholds, test runner, CI, git hooks) are **not configured**. Re-run `/setup` when implementation of the first module begins, to configure those gates against the real stack.

## High-Level Architecture

- **Backend**: Python 3.11+ / FastAPI / SQLAlchemy 2.x (async) / Pydantic v2, SQLite for development with a PostgreSQL-portable schema (config-only migration path). Layered per module: `models/` → `schemas/` → `services/` → `routers/`, with a shared `core/security/` package providing JWT issuance/verification, password hashing, and the `get_current_user` / `require_permission(...)` dependencies every module's routes use.
- **Frontend**: React 18 + Vite + TypeScript + TailwindCSS SPA, React Query for server state, an in-memory-only `AuthContext` for the JWT (never `localStorage`/`sessionStorage`/cookies), React Router with permission-aware route guards.
- **Toolchain versions are locked, not just recommended**: Node.js **v22.17.1**, npm **10.9.2**, Python **3.11+** — pinned in `.nvmrc`/`.python-version`/`package.json#engines` by the Project Setup module. Verify with `node --version` / `npm --version` before starting work on any module.
- **Thirteen modules total**, in dependency order: **Project Setup** (foundation — must be built first, zero dependencies) → Foundation Enhancements → Frontend Shell → Permissions → Roles → Accounts (parallelizable) → Users → Authentication → Contacts → Opportunities (parallelizable) → Leads → Activities → **Deployment** (Dockerization + 50+-record seed data — must be built last, depends on all 9 CRM modules). Each module's `specs/<name>/spec.md` documents its own dependency table; there are no circular dependencies.
- **UI/UX reference**: `specs/mocks/` contains exported HTML/CSS/JS captures of the target frontend's look and feel (Dashboard, Leads, Contacts, Accounts, Opportunities, Activities, User Management, Mail Inbox, Seed Manager, Login).

## Documentation Structure & Standards

Every module lives in `specs/<module-name>/` with exactly four files, in this order of authorship:

1. **`spec.md`** — module scope/objectives, user stories, functional requirements (prefixed `FR-{MODULE}-NNN`), success criteria (prefixed `SC-{MODULE}-NNN`), key entities, dependencies on other modules.
2. **`plan.md`** — module architecture, components & responsibilities, data flow within the module, integration points with other modules.
3. **`tasks.md`** — implementation tasks (prefixed `T-{MODULE}-N`), task sequencing, acceptance criteria, dependencies/prerequisites.
4. **`work-units.md`** — atomic work units (prefixed `WU-{MODULE}-N`) with Definition of Done checkboxes, file scope, and dependency graph for orchestrated execution.

Cross-module references always link to another module's `spec.md`/`plan.md`/`tasks.md` by relative path (e.g., `[Roles](../roles/spec.md)`) rather than restating that module's content. When a module's documentation changes in a way that affects another module's stated dependency, update both sides of the link.

Do not place module-specific specifications, requirements, or task lists in this file (`CLAUDE.md`) — they belong only in the corresponding `specs/<name>/` folder.

## Cross-Module Principles

- **No circular dependencies.** The module dependency graph is a strict DAG. Before adding a new cross-module reference, verify it doesn't introduce a cycle.
- **Record-level ownership (`created_by_user_id`) is scoped narrowly.** Only Leads and Activities carry it; Accounts, Contacts, and Opportunities are governed by role-level permissions only. Do not add ownership scoping to a module without updating its `spec.md`'s explicit rationale.
- **Permissions are the single source of truth for "what can be gated."** Every `require_permission("{module}:{action}")` call site must reference a code that exists in the Permissions module's seeded catalogue. Roles only bundle existing permission codes — they never invent new ones.
- **Cross-module writes are the exception, not the norm.** The only documented cross-module write is Lead conversion (Leads writing into Accounts/Contacts/Opportunities inside one atomic transaction). Any new cross-module write path must be called out explicitly in both modules' `plan.md` files, the same way.
- **A module's frontend pages may read from another module's API, but a module's backend service layer may only write to its own table(s)** — except for the one documented exception above.

## Implementation Workflow

1. Implement modules in dependency order, following the `tasks.md` sequencing in each module folder: **Project Setup** (always first — no other module's files have anywhere to go without it) → **Permissions → Roles → Accounts** (parallelizable) → **Users → Authentication** → **Contacts → Opportunities** (parallelizable) → **Leads** → **Activities** → **Deployment** (always last — its seed script calls every other module's real service functions, so none may be a stub).
2. Before starting a module, re-read its `spec.md` and `plan.md`, and confirm every module listed under "Prerequisites" in its `tasks.md` is actually complete.
3. Use `/start-task` to begin work on a module; reference the module's `tasks.md` task IDs (e.g., `T-LEAD-6`) directly in the task description so progress is traceable back to this documentation.
4. When a module's implementation reveals that its documentation was wrong or incomplete, update that module's `spec.md`/`plan.md`/`tasks.md` in the same change — don't let the docs drift from reality.
5. Run `/setup` once Project Setup's implementation begins, to configure coverage/test/CI tooling against the real stack (Python 3.11+ / pytest, Node v22.17.1 / npm 10.9.2 / vitest).

## Coding Standards & Conventions

*(To be filled in once the first module's implementation begins and concrete tooling choices — linter, formatter, type checker — are finalized. Until then, see each module's `plan.md` "Architectural Decisions Specific to This Module" sections for the patterns expected once code exists: layered structure, Pydantic validation at the schema layer for stateless rules, service-layer enforcement for stateful/cross-record rules.)*
