# Active Plan
<!-- approved: 2026-06-16 -->
<!-- gate-iterations: 2 -->
<!-- user-approved: true -->
<!-- status: in-progress -->

## Task
Implement Roles module (WU-ROLE-1..6) — permission bundles for RBAC, gates Users and Auth.

## Source
`specs/roles/work-units.md` (gate-approved 2026-06-16, iteration 2)

## Execution Sequence
```
WU-ROLE-1 ──► WU-ROLE-2 ──► WU-ROLE-3 ──► WU-ROLE-4 ──┬──► WU-ROLE-5
                                                        └──► WU-ROLE-6
```

## Key Decisions from Gate Review
1. **No Auth dependency**: Router implemented WITHOUT permission gating; Auth adds it later
2. **Deferred user_count**: Returns 0 until Users module creates users table
3. **Deferred ROLE_HAS_USERS**: Guard skipped until Users FK exists
4. **Pagination required**: list_roles(offset, limit) per FR-ROLE-004

## Work Unit Status
| WU | Description | Status | Notes |
|----|-------------|--------|-------|
| WU-ROLE-1 | Schema + Seed Migrations | ⏳ pending | 0004 + 0005 with 3 system roles |
| WU-ROLE-2 | Backend ORM + Schemas | ⏳ pending | Role, RolePermission, RoleCreate/Update/Response |
| WU-ROLE-3 | Service Layer + Guards | ⏳ pending | CRUD + system role protection + pagination |
| WU-ROLE-4 | Router | ⏳ pending | 5 CRUD endpoints, no auth gating yet |
| WU-ROLE-5 | Frontend Admin Page | ⏳ deferred | Depends on Auth WU-AUTH-8 |
| WU-ROLE-6 | Integration Tests | ⏳ pending | System role tests, permission validation |

## Dependencies
- Upstream: Permissions WU-PERM-1 ✅
- Downstream: Users WU-USR-1 (role_id FK), Authentication WU-AUTH-3
