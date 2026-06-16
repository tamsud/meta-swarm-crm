# Active Plan
<!-- approved: 2026-06-16 -->
<!-- gate-iterations: 0 (inherited from approved work-units.md) -->
<!-- user-approved: true -->
<!-- status: in-progress -->

## Task
Implement Permissions module (WU-PERM-1..5) — foundational catalogue, gates Roles and all downstream modules.

## Source
`specs/permissions/work-units.md` (gate-approved 2026-06-16)

## Execution Sequence
```
WU-PERM-1 ──► WU-PERM-2 ──► WU-PERM-3 ──► WU-PERM-4
                                              │
WU-PERM-5 (deferred — runs after all module routers exist)
```

## Permission Catalogue (21 codes)
| Module | Permission Codes |
|--------|------------------|
| accounts | accounts:create, accounts:read, accounts:update, accounts:delete |
| contacts | contacts:create, contacts:read, contacts:update, contacts:delete |
| leads | leads:manage-own, leads:manage-all |
| opportunities | opportunities:create, opportunities:read, opportunities:update, opportunities:delete |
| activities | activities:manage-own, activities:manage-all |
| users | users:manage, users:manage-self |
| roles | roles:manage |
| permissions | permissions:read |
| seed | seed:manage |

## Work Unit Status
| WU | Description | Status | Notes |
|----|-------------|--------|-------|
| WU-PERM-1 | Schema + Seed Migrations | ✅ completed | 0002 + 0003 with 21 codes |
| WU-PERM-2 | Backend ORM + Schemas + Service | ✅ completed | Permission model, PermissionResponse, list_permissions() |
| WU-PERM-3 | Read-Only Router | ✅ completed | GET /permissions with ?module= filter, no POST/PATCH/DELETE |
| WU-PERM-4 | Frontend Admin Page | ⏳ deferred | Depends on Auth WU-AUTH-8 |
| WU-PERM-5 | Catalogue Consistency Test | ⏳ deferred | Runs after all module routers exist |

## Dependencies
- Upstream: Project Setup WU-SETUP-9 ✅
- Downstream: Roles WU-ROLE-1 (FK target), Authentication WU-AUTH-3, every module router (WU-PERM-5)
