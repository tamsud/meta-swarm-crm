# Master Implementation Plan

**Generated**: 2026-06-17 | **Total Work Units**: 88 across 12 modules

---

## Executive Summary

The CRM project has **88 work units** across **12 modules**. Currently, **5 modules are complete** (39 WUs), **7 modules remain** (49 WUs).

### Current Status

| Phase | Modules | WUs | Status |
|-------|---------|-----|--------|
| Foundation | Project Setup, Permissions, Roles | 20 | ✅ Complete |
| Shell | Frontend Shell | 9 | ✅ Complete |
| Core Data | Accounts, Users | 14 | ✅ Backend Complete |
| **Blocking** | Authentication | 9 | ❌ NOT STARTED |
| CRM Modules | Contacts, Opportunities, Leads, Activities | 28 | ❌ NOT STARTED |
| Finalization | Deployment | 8 | ❌ NOT STARTED |
| **MISSING** | Dashboard | ? | ❌ NOT IN SPECS |

---

## Module Completion Matrix

| Module | Backend | Frontend | Integration | Overall |
|--------|---------|----------|-------------|---------|
| Project Setup | ✅ | ✅ | ✅ | ✅ 100% |
| Permissions | ✅ | ❌ Placeholder | ✅ | 80% |
| Roles | ✅ | ❌ Placeholder | ✅ | 80% |
| Accounts | ✅ | ❌ Blocked by Auth | ❌ | 50% |
| Users | ✅ | ❌ Blocked by Auth | ❌ | 50% |
| Frontend Shell | - | ✅ | - | ✅ 100% |
| **Authentication** | ❌ | ❌ | ❌ | **0%** |
| Contacts | ❌ | ❌ | ❌ | 0% |
| Opportunities | ❌ | ❌ | ❌ | 0% |
| Leads | ❌ | ❌ | ❌ | 0% |
| Activities | ❌ | ❌ | ❌ | 0% |
| Deployment | ❌ | ❌ | ❌ | 0% |

---

## Critical Path

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CRITICAL PATH                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✅ COMPLETE                  ❌ REMAINING                                   │
│  ─────────                    ──────────                                    │
│                                                                             │
│  Project Setup ─┬─► Permissions ─► Roles ─┬─► Accounts (BE) ─► Users (BE)  │
│                 │                         │        │                │       │
│                 └─► Frontend Shell        │        └────────────────┘       │
│                                           │                 │               │
│                                           │                 ▼               │
│                                           │        ┌───────────────┐        │
│                                           │        │ AUTHENTICATION│        │
│                                           │        │  (BLOCKER)    │        │
│                                           │        └───────┬───────┘        │
│                                           │                │                │
│                                           │    ┌───────────┼────────────┐   │
│                                           │    │           │            │   │
│                                           │    ▼           ▼            ▼   │
│                                           └─► Contacts → Opportunities  │   │
│                                                    │           │        │   │
│                                                    └─────┬─────┘        │   │
│                                                          │              │   │
│                                                          ▼              │   │
│                                               ┌──────────────────┐      │   │
│                                               │      Leads       │◄─────┘   │
│                                               └────────┬─────────┘          │
│                                                        │                    │
│                                                        ▼                    │
│                                               ┌──────────────────┐          │
│                                               │    Activities    │          │
│                                               └────────┬─────────┘          │
│                                                        │                    │
│                                                        ▼                    │
│                                               ┌──────────────────┐          │
│                                               │    Deployment    │          │
│                                               └──────────────────┘          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Remaining Work Units by Module

### 1. Authentication (9 WUs) - **MUST BE NEXT**

| WU | Description | Depends On | Effort |
|----|-------------|------------|--------|
| WU-AUTH-1 | JWT Utility | Project Setup | S |
| WU-AUTH-2 | Password Utility | Project Setup | ✅ DONE |
| WU-AUTH-3 | Current-User Dependency | AUTH-1, Users | M |
| WU-AUTH-4 | Auth Router (login + me) | AUTH-1,2,3 | M |
| WU-AUTH-5 | Retrofit Permission Gates | AUTH-3, ALL routers | L |
| WU-AUTH-6 | Frontend AuthContext | AUTH-4 | M |
| WU-AUTH-7 | Axios Interceptors | AUTH-6 | S |
| WU-AUTH-8 | Login Page + Guards | AUTH-6,7 | M |
| WU-AUTH-9 | Integration Tests | AUTH-4-8 | M |

**Unlocks**: All frontend pages can wire to APIs

---

### 2. Contacts (6 WUs)

| WU | Description | Depends On | Effort |
|----|-------------|------------|--------|
| WU-CONT-1 | Schema Migration | Accounts WU-ACCT-1 | S |
| WU-CONT-2 | ORM + Schemas + Service | CONT-1 | M |
| WU-CONT-3 | Router | CONT-2, Auth | S |
| WU-CONT-4 | Frontend List + Form | CONT-3, Auth | M |
| WU-CONT-5 | Frontend Detail Page | CONT-3 | M |
| WU-CONT-6 | Integration Tests | CONT-3 | S |

**Unlocks**: FK target for Opportunities, Leads

---

### 3. Opportunities (6 WUs) - **"Pipeline" in UI**

| WU | Description | Depends On | Effort |
|----|-------------|------------|--------|
| WU-OPP-1 | Schema Migration | Accounts, Contacts | S |
| WU-OPP-2 | ORM + Schemas + Service | OPP-1 | M |
| WU-OPP-3 | Router | OPP-2, Auth | S |
| WU-OPP-4 | Frontend Board + Table | OPP-3, Accounts, Contacts | L |
| WU-OPP-5 | Frontend Detail Page | OPP-3 | M |
| WU-OPP-6 | Integration Tests | OPP-3 | M |

**Unlocks**: Pipeline Kanban board (mock: `pipeline.png`)

---

### 4. Leads (9 WUs) - Most Complex Module

| WU | Description | Depends On | Effort |
|----|-------------|------------|--------|
| WU-LEAD-1 | Schema Migration | Users | S |
| WU-LEAD-2 | ORM + Schemas | LEAD-1 | M |
| WU-LEAD-3 | State Machine Validation | LEAD-2 | M |
| WU-LEAD-4 | Service + Ownership Filter | LEAD-2,3, Auth | M |
| WU-LEAD-5 | Conversion Orchestration | LEAD-4, Accounts, Contacts, Opportunities | L |
| WU-LEAD-6 | Router | LEAD-4,5 | S |
| WU-LEAD-7 | Frontend List + Filter | LEAD-6 | M |
| WU-LEAD-8 | Frontend Detail + Convert | LEAD-6 | L |
| WU-LEAD-9 | Integration Tests (atomicity) | LEAD-6 | M |

**Unlocks**: Lead qualification and conversion workflow

---

### 5. Activities (7 WUs)

| WU | Description | Depends On | Effort |
|----|-------------|------------|--------|
| WU-ACT-1 | Schema Migration | Users, Contacts, Opportunities | S |
| WU-ACT-2 | ORM + Schemas | ACT-1 | M |
| WU-ACT-3 | Service + Polymorphic Filters | ACT-2 | M |
| WU-ACT-4 | Router | ACT-3, Auth | S |
| WU-ACT-5 | Frontend Activity Timeline | ACT-4 | M |
| WU-ACT-6 | Cross-Module Activity Tabs | ACT-5 | M |
| WU-ACT-7 | Integration Tests | ACT-4 | S |

**Unlocks**: Activity tracking across all entities

---

### 6. Deployment (8 WUs) - **FINAL**

| WU | Description | Depends On | Effort |
|----|-------------|------------|--------|
| WU-DEPLOY-1 | Dockerfile (backend) | ALL backend modules | S |
| WU-DEPLOY-2 | Dockerfile (frontend) | ALL frontend modules | S |
| WU-DEPLOY-3 | docker-compose.yml | DEPLOY-1,2 | S |
| WU-DEPLOY-4 | Seed Script (50+ records) | ALL service layers | L |
| WU-DEPLOY-5 | Clear Function | DEPLOY-4 | S |
| WU-DEPLOY-6 | Frontend Seed Manager | DEPLOY-4,5 | M |
| WU-DEPLOY-7 | Verification Script | ALL | M |
| WU-DEPLOY-8 | Integration Tests | ALL | M |

---

### 7. Dashboard Module (NOT IN SPECS) - **NEEDS CREATION**

The mock (`dashboards.png`) shows:
- KPI Cards: Total Accounts, Active Leads, Open Pipeline, Weighted Value, Win Rate
- Charts: Pipeline by Stage (3D funnel), Deals by Stage (bar), Deals by Value (pie)
- Summaries: Closed Won/Lost totals
- Recent Activity feed

**Recommended Work Units**:
| WU | Description | Depends On | Effort |
|----|-------------|------------|--------|
| WU-DASH-1 | Dashboard API endpoints | ALL data modules | M |
| WU-DASH-2 | Frontend KPI Cards | DASH-1, Auth | M |
| WU-DASH-3 | Frontend Charts | DASH-1, chart library | L |
| WU-DASH-4 | Frontend Activity Feed | Activities | S |

---

## Frontend Pages vs Mock Designs

| Page | Mock File | Current State | Required Module |
|------|-----------|---------------|-----------------|
| Login | `login.png` | UI exists, not functional | Authentication |
| Dashboard | `dashboards.png` | "Coming soon" | Dashboard (NEW) |
| Accounts | `accounts.png` | "Coming soon" | Auth + WU-ACCT-4/5 |
| Contacts | `conatacts.png` | "Coming soon" | Contacts |
| Pipeline | `pipeline.png` | "Coming soon" | Opportunities |
| Users | (in mock) | "Coming soon" | Auth + WU-USR-6/7 |

---

## Estimated Timeline (Work Sessions)

| Phase | Modules | Estimated Sessions |
|-------|---------|-------------------|
| Phase 1 | Authentication (8 WUs remaining) | 2-3 sessions |
| Phase 2 | Contacts (6 WUs) | 1-2 sessions |
| Phase 3 | Opportunities (6 WUs) | 2 sessions |
| Phase 4 | Leads (9 WUs) | 2-3 sessions |
| Phase 5 | Activities (7 WUs) | 1-2 sessions |
| Phase 6 | Deployment (8 WUs) | 1-2 sessions |
| Phase 7 | Dashboard (4 WUs - NEW) | 1-2 sessions |
| **TOTAL** | 49+ WUs remaining | **10-16 sessions** |

---

## Recommendations

1. **Immediate Priority**: Build Authentication module — it unblocks ALL frontend work
2. **Parallel Opportunity**: After Auth, Contacts and Accounts-frontend can run in parallel
3. **Missing Spec**: Create Dashboard module spec to match `dashboards.png`
4. **Mock Alignment**: Review all mock PNGs before implementing each frontend page
5. **Testing Strategy**: Run integration tests after each module, not just at the end

---

## Next Actions

1. [ ] Implement Authentication (WU-AUTH-1,3,4,5,6,7,8,9)
2. [ ] Create Dashboard module spec (new: `specs/dashboard/`)
3. [ ] Implement Contacts (WU-CONT-1-6)
4. [ ] Implement Opportunities (WU-OPP-1-6)
5. [ ] Implement Leads (WU-LEAD-1-9)
6. [ ] Implement Activities (WU-ACT-1-7)
7. [ ] Implement Deployment (WU-DEPLOY-1-8)
8. [ ] Implement Dashboard (WU-DASH-1-4)
