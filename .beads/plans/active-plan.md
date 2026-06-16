# Active Plan
<!-- approved: 2026-06-16 -->
<!-- gate-iterations: 3 -->
<!-- user-approved: true -->
<!-- status: in-progress -->

## Task
Create per-module `work-units.md` files for all 11 CRM modules that break each module's T-* tasks into WU-* work units with DoD items, file scopes, and dependency graphs.

## Deliverables (11 files, all written)
- `specs/project-setup/work-units.md`     — WU-SETUP-1..9 (covers T-SETUP-1..13; SC-SETUP-001..003)
- `specs/permissions/work-units.md`       — WU-PERM-1..5 (covers T-PERM-1..8; SC-PERM-001..002)
- `specs/roles/work-units.md`             — WU-ROLE-1..6 (covers T-ROLE-1..8; SC-ROLE-001..002)
- `specs/accounts/work-units.md`          — WU-ACCT-1..6 (covers T-ACCT-1..8; SC-ACCT-001..003)
- `specs/users/work-units.md`             — WU-USR-1..8 (covers T-USR-1..9; SC-USR-001..003)
- `specs/authentication/work-units.md`    — WU-AUTH-1..9 (covers T-AUTH-1..11; SC-AUTH-001..003)
- `specs/contacts/work-units.md`          — WU-CONT-1..6 (covers T-CONT-1..8; SC-CONT-001..002)
- `specs/opportunities/work-units.md`     — WU-OPP-1..6 (covers T-OPP-1..8; SC-OPP-001..003)
- `specs/leads/work-units.md`             — WU-LEAD-1..9 (covers T-LEAD-1..10; SC-LEAD-001..003)
- `specs/activities/work-units.md`        — WU-ACT-1..7 (covers T-ACT-1..8; SC-ACT-001..002)
- `specs/deployment/work-units.md`        — WU-DEPLOY-1..8 (covers T-DEPLOY-1..8; SC-DEPLOY-001..004)

## Each work-units.md contains
1. **Dependency Graph** — Upstream (with specific WU IDs) / Downstream / Internal sequence (ASCII flow)
2. **Per WU**: Tasks (T-* IDs), Depends on, File scope (concrete repo paths), Definition of Done (verifiable checklist), Success Criteria covered (SC-* IDs)

## Cross-module integration explicit
- Leads conversion (WU-LEAD-5) → Accounts WU-ACCT-2, Contacts WU-CONT-2, Opportunities WU-OPP-2 in a single transaction
- Activities cross-module wiring (WU-ACT-6) → Contacts WU-CONT-5, Opportunities WU-OPP-5 (read-only)
- Deployment seed (WU-DEPLOY-4) → all 9 CRM modules' real service functions
- Permissions catalogue (WU-PERM-1) is single source of truth for all `{module}:{action}` codes referenced anywhere

## Gate history
- Iter 1: Feasibility FAIL, Completeness FAIL, Scope PASS
- Iter 2: Feasibility FAIL (3 blocking: missing `accounts.address`, fabricated `seed:run` permission, contradictory `LeadConvertResponse`), Completeness FAIL (2 blocking: fabricated AC-N refs, missing SC mappings), Scope PASS
- Iter 3: Feasibility FAIL (2 blocking in users WU-USR-4: rogue DELETE endpoint, omitted GET /users/me), Completeness PASS, Scope PASS
- Iter 3 fixes applied post-cap to `specs/users/work-units.md:87` (router endpoint list matches `users/plan.md:25` exactly; no DELETE, includes GET /users/me)

## Status
Approved by user 2026-06-16 after iter-3 fix. All 81 WUs traceable to SC-* IDs across the 11 spec.md files. Ready as input to per-module orchestrated execution when implementation phase begins.
