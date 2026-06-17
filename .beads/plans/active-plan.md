# Active Plan: Dashboard, Activities, Leads, Seed Manager — Full Stack
<!-- approved: 2026-06-17T12:00:00Z -->
<!-- gate-iterations: 1 -->
<!-- user-approved: true -->
<!-- status: complete -->

## Overview

Complete 4 stub frontend modules by implementing both backend and frontend for:
- **Activities** — full CRUD with ownership filter + timeline view
- **Leads** — full CRUD with state machine, ownership, atomic conversion
- **Dashboard** — KPI aggregations + charts + activity feed
- **Seed Manager** — POST/DELETE /seed endpoints + admin UI

Backend services for activities and leads do not exist yet. Dashboard has no backend.
All four page stubs say "coming soon."

## Review Gate Blockers Fixed

1. Lead conversion uses flush-only inline ORM (no nested db.commit calls)
2. Migration 0015 explicitly inserts role_permissions rows for role_ids 1/2/3
3. clear_all() specifies exact FK-safe delete order
4. routes/config.ts LEAD_DETAIL constant added to WU-5 scope
5. Seed router coupling explicitly documented
6. OpportunityResponse cross-module import made explicit
7. Permission gate for list endpoints uses manage-own with service-layer scoping
8. LeadDetailPage import in routes/index.tsx made explicit
9. seed:manage permission gate stated for all seed endpoints
10. Activities filter design documented (type chips on page; contact/opp via cross-module URL params)

## Work Units

| WU | Description | Status |
|----|-------------|--------|
| WU-1 | Backend: Activities (migration + model + schema + service + router) | complete |
| WU-2 | Backend: Leads (migration + model + schema + service + router) | complete |
| WU-3 | Backend: Dashboard + Seed (permission migration + schemas + service + routers) | complete |
| WU-4 | Frontend: Activities timeline page + form | complete |
| WU-5 | Frontend: Leads list + detail + convert modal | complete |
| WU-6 | Frontend: Dashboard KPI cards + charts + activity feed | complete |
| WU-7 | Frontend: Seed Manager page + cross-module wiring | complete |

## Execution Order

WU-1 → WU-2 → WU-3 → WU-4 → WU-5 → WU-6 → WU-7

---

## WU-1: Backend Activities

### Files
- `backend/alembic/versions/0013_create_activities.py` (new)
- `backend/app/models/activity.py` (new)
- `backend/app/schemas/activity.py` (new)
- `backend/app/services/activity_service.py` (new)
- `backend/app/routers/activities.py` (new)
- `backend/app/models/__init__.py` (update — add Activity import so Base.metadata sees it)
- `backend/app/exceptions.py` (update — add ActivityNotFoundError, ActivityNoLinkError, ActivityOwnershipError)
- `backend/app/main.py` (update — register activities router)

### Key requirements

**Migration:**
- Table columns: id, type (ENUM: call/email/meeting), subject (VARCHAR 512), notes (TEXT nullable), activity_date (DATETIME DEFAULT CURRENT_TIMESTAMP), contact_id FK nullable, opportunity_id FK nullable, created_by_user_id FK nullable, created_at, updated_at
- CHECK constraint: `contact_id IS NOT NULL OR opportunity_id IS NOT NULL`
- FK contact_id → contacts(id) ON DELETE RESTRICT
- FK opportunity_id → opportunities(id) ON DELETE RESTRICT
- FK created_by_user_id → users(id) ON DELETE SET NULL

**Schema:**
- `ActivityCreate` model_validator: if both contact_id and opportunity_id are None → raise ACTIVITY_NO_LINK (400)
- `activity_date` defaults to datetime.utcnow() in schema when omitted
- Pydantic enum rejects invalid type values with 422

**Service (`activity_service.py`):**
- `create`, `get`, `list`, `update`, `delete`
- `list` filters: type, contact_id, opportunity_id; sorts by activity_date DESC
- Ownership: `apply_ownership_filter(query, user, permissions)` — if user lacks `activities:manage-all`, filter `WHERE created_by_user_id = user.id`
- `assert_ownership(activity, user, permissions)` — raises ActivityOwnershipError (403) if user lacks manage-all AND activity.created_by_user_id != user.id

**Router (`activities.py`):**
- GET /activities → requires `activities:manage-own` (lowest common denominator — both Sales Reps and Managers/Admins can access); router passes current_user to service; service applies ownership filter
- GET /activities/{id} → same permission gate (`activities:manage-own`)
- POST /activities → requires `activities:manage-own`
- PATCH /activities/{id} → requires `activities:manage-own`; service calls assert_ownership
- DELETE /activities/{id} → requires `activities:manage-own`; service calls assert_ownership
- Filter params: ?type=, ?contact_id=, ?opportunity_id=

---

## WU-2: Backend Leads

### Files
- `backend/alembic/versions/0014_create_leads.py` (new)
- `backend/app/models/lead.py` (new)
- `backend/app/schemas/lead.py` (new — includes LeadCreate, LeadUpdate, LeadResponse)
- `backend/app/services/lead_service.py` (new)
- `backend/app/routers/leads.py` (new)
- `backend/app/models/__init__.py` (update — add Lead import)
- `backend/app/exceptions.py` (update — add LeadNotFoundError, InvalidLeadTransitionError, LeadAlreadyConvertedError)
- `backend/app/main.py` (update — register leads router)

### Key requirements

**Migration:**
- Table: id, first_name, last_name, email, phone nullable, company nullable, status (ENUM: new/contacted/qualified/lost), source nullable, notes nullable, created_by_user_id FK nullable → users(id) ON DELETE SET NULL, converted_opportunity_id FK nullable → opportunities(id) ON DELETE SET NULL, converted_at nullable, created_at, updated_at

**Schema:**
- `LeadResponse` includes converted_opportunity_id and created_by_user_id (read-only)
- `LeadUpdate` forbids patching created_by_user_id or converted_opportunity_id (extra=forbid)
- conversion endpoint returns `OpportunityResponse` (import from `app.schemas.opportunity`) — this cross-module import is explicit

**Service:**
- `VALID_TRANSITIONS = {new: [contacted, lost], contacted: [qualified, lost], qualified: [lost], lost: []}`
- `validate_status_transition(current, next)` → raises InvalidLeadTransitionError (400) with current+attempted in payload
- `apply_ownership_filter` and `assert_ownership` — same pattern as activities; uses leads:manage-own vs leads:manage-all
- `convert_lead(lead_id, db, user)`:
  - Validates lead is qualified AND converted_opportunity_id IS NULL (else LeadAlreadyConvertedError 400)
  - Uses FLUSH-ONLY inline ORM operations — does NOT call find_or_create_account/create_contact/create_opportunity from their respective service modules (those services call db.commit() internally which would break the transaction)
  - Instead: inline all ORM adds + db.flush() within a single async with db.begin(): block
  - Step 1: find Account WHERE lower(name) = lower(lead.company) OR create new Account, flush
  - Step 2: find Contact WHERE email = lead.email OR create new Contact linked to account, flush
  - Step 3: create Opportunity (account_id, contact_id from steps 1/2), flush
  - Step 4: update lead.converted_opportunity_id + converted_at = now()
  - Single db.commit() at end of transaction block
  - Returns the Opportunity ORM object (caller wraps in OpportunityResponse)

**Router:**
- GET /leads → requires `leads:manage-own`; passes current_user to service for ownership filter
- GET /leads/{id} → requires `leads:manage-own`
- POST /leads → requires `leads:manage-own`; sets created_by_user_id = current_user.id
- PATCH /leads/{id} → requires `leads:manage-own`; routes through validate_status_transition AND assert_ownership
- DELETE /leads/{id} → requires `leads:manage-own`; routes through assert_ownership
- POST /leads/{id}/convert → requires `leads:manage-own`; returns 201 with OpportunityResponse body

---

## WU-3: Backend Dashboard + Seed

### Files
- `backend/alembic/versions/0015_add_dashboard_permission.py` (new)
- `backend/app/schemas/dashboard.py` (new)
- `backend/app/services/dashboard_service.py` (new)
- `backend/app/routers/dashboard.py` (new)
- `backend/app/routers/seed.py` (new)
- `backend/app/main.py` (update — register dashboard + seed routers)
- `backend/app/seed.py` (update — add seed_leads, seed_activities, seed_all, clear_all functions)

### Key requirements

**Migration 0015:**
- Inserts `('dashboard:view', 'dashboard', 'view', 'View the dashboard summary and KPIs')` into permissions table
- Queries the new permission's id
- Inserts into role_permissions: rows for role_id=1 (Admin), role_id=2 (Manager), role_id=3 (Sales Rep) — same pattern as 0012_add_mock_email_permission.py

**Dashboard schema:**
```
DashboardSummaryResponse:
  kpis: KpiData
    total_accounts: int
    active_leads: int   # new + contacted + qualified
    open_pipeline: float
    weighted_value: float
    win_rate: float     # 0.0–1.0, zero-safe
  stage_breakdown: list[StageBreakdown]  # 5 entries
    stage: str
    count: int
    value: float
  closed: ClosedData
    won: ClosedCard  # count + value
    lost: ClosedCard
  recent_activities: PaginatedActivities
    items: list[ActivitySummary]  # type, subject, contact_name, opp_title, activity_date
    total: int
    page: int
    page_size: int (=5)
    total_pages: int
```

**Dashboard service:**
- `get_summary(db, activity_page=1)` — all queries async; activity page size fixed at 5
- KPI formulas:
  - active_leads = COUNT WHERE status IN ('new', 'contacted', 'qualified')
  - open_pipeline = COALESCE(SUM(value), 0) WHERE stage NOT IN ('closed_won', 'closed_lost')
  - weighted_value = COALESCE(SUM(value * probability / 100.0), 0) WHERE stage NOT IN ('closed_won', 'closed_lost')
  - win_rate: closed_won_count / (closed_won_count + closed_lost_count) or 0.0 if denominator=0

**Dashboard router:**
- GET /dashboard/summary?activity_page=1 → requires `require_permission("dashboard:view")`

**Seed.py updates:**
- `seed_leads(db: AsyncSession)` — seeds 50+ leads covering all 4 statuses; includes ~5 "qualified" unconverted leads
- `seed_activities(db: AsyncSession, contacts, opportunities)` — seeds 50+ activities covering all 3 types; mix of single-linked (contact_id only) and dual-linked (both)
- `seed_all(db: AsyncSession)` — calls existing seed functions + new ones in order; returns dict of created/skipped counts per entity
- `clear_all(db: AsyncSession)` — deletes in FK-safe order within single transaction:
  1. DELETE FROM activities
  2. DELETE FROM leads
  3. DELETE FROM mock_emails  
  4. DELETE FROM opportunities
  5. DELETE FROM contacts
  6. DELETE FROM accounts
  7. DELETE FROM users WHERE email NOT IN (3 demo seed emails)
  Returns counts deleted per entity

**Seed router (`routers/seed.py`):**
- Both endpoints gated by `require_permission("seed:manage")` — Admin only
- POST /seed → opens AsyncSessionLocal, calls seed_all(db), returns summary with per-entity created/skipped counts
- DELETE /seed → opens AsyncSessionLocal, calls clear_all(db), returns summary with per-entity deleted counts

---

## WU-4: Frontend Activities

### Files
- `frontend/src/features/activities/types.ts` (new)
- `frontend/src/features/activities/api.ts` (new)
- `frontend/src/features/activities/ActivityForm.tsx` (new)
- `frontend/src/features/activities/ActivitiesPage.tsx` (new — full implementation)
- `frontend/src/pages/ActivitiesPage.tsx` (update — re-exports feature component)

### Key requirements

**types.ts:** Activity, ActivityCreate, ActivityUpdate, ActivitiesListResponse, ActivityResponse

**api.ts:** listActivities(?type, ?contact_id, ?opportunity_id, offset, limit), getActivity, createActivity, updateActivity, deleteActivity

**ActivitiesPage:**
- Timeline grouped by date (descending), using activity_date
- Filter chips for type: All / Call / Email / Meeting — drives ?type= query param
- Contact/opportunity filtering NOT on the main page; these filters are only used via cross-module URL params from ContactHistoryTab and OpportunityActivityList (design decision: the unified timeline view shows all-type filtering only; per-contact/per-opp views come from cross-module wiring)
- ActivityForm: type selector (call/email/meeting), subject input, notes textarea, contact picker (async search via /contacts?search=), opportunity picker (async search via /opportunities)
- Client-side: block submission if neither contact_id nor opportunity_id selected (mirrors server CHECK)
- Empty state per mock
- Permission check: hasPermission('activities:manage-own') guards edit/delete buttons

**ActivityForm:** reusable modal, accepts optional pre-filled contact_id and opportunity_id props (for cross-module use)

---

## WU-5: Frontend Leads

### Files
- `frontend/src/features/leads/types.ts` (new)
- `frontend/src/features/leads/api.ts` (new)
- `frontend/src/features/leads/LeadForm.tsx` (new — create/edit modal)
- `frontend/src/features/leads/LeadsListPage.tsx` (new)
- `frontend/src/features/leads/LeadDetailPage.tsx` (new)
- `frontend/src/features/leads/LeadStatusControl.tsx` (new)
- `frontend/src/features/leads/LeadConvertModal.tsx` (new)
- `frontend/src/pages/LeadsPage.tsx` (update — re-exports feature component)
- `frontend/src/routes/index.tsx` (update — add import for LeadDetailPage + add route `{ path: ROUTES.LEAD_DETAIL, element: <LeadDetailPage /> }`)
- `frontend/src/routes/config.ts` (update — add `LEAD_DETAIL: '/leads/:id'` to ROUTES object)

### Key requirements

**types.ts:** Lead, LeadCreate, LeadUpdate, LeadsListResponse, LeadResponse

**api.ts:** listLeads(?status, ?search, offset, limit), getLead, createLead, updateLead, deleteLead, convertLead (returns OpportunityResponse shape)

**LeadsListPage:**
- Status tabs: All / New / Contacted / Qualified / Lost / Converted — drives ?status= filter
- Search input → ?search= query param
- Table rows link to /leads/:id
- Sales Rep sees only own leads (server-side; frontend does nothing special)

**LeadStatusControl:**
- Transition table mirrored client-side: `{new: ['contacted','lost'], contacted: ['qualified','lost'], qualified: ['lost'], lost: [], converted: []}`
- Renders only valid next-states as buttons; invalid states hidden/disabled
- Shows "Converted" badge (non-clickable) when lead has converted_opportunity_id

**LeadDetailPage:**
- Shows lead fields + status control
- Convert button: only shown when status === 'qualified' AND !converted_opportunity_id
- After convert: shows "Converted to Opportunity" badge with Link to /opportunities/:id

**LeadConvertModal:**
- Confirmation dialog before triggering POST /leads/:id/convert
- On success: shows opportunity link
- On 400 LEAD_ALREADY_CONVERTED: shows inline error with link to existing opportunity

---

## WU-6: Frontend Dashboard

### Files
- `frontend/src/features/dashboard/types.ts` (new)
- `frontend/src/features/dashboard/api.ts` (new)
- `frontend/src/features/dashboard/components/KpiCard.tsx` (new)
- `frontend/src/features/dashboard/components/KpiGrid.tsx` (new)
- `frontend/src/features/dashboard/components/PipelineBarChart.tsx` (new — recharts BarChart of stage counts)
- `frontend/src/features/dashboard/components/ClosedDealsPanel.tsx` (new)
- `frontend/src/features/dashboard/components/RecentActivityFeed.tsx` (new)
- `frontend/src/pages/DashboardPage.tsx` (update — full implementation)
- `frontend/package.json` (update — add recharts)

### Key requirements

**types.ts:** DashboardSummary, KpiData, StageBreakdown, ClosedData, ActivitySummary, PaginatedActivities

**api.ts:** getDashboardSummary(activityPage?: number) → useDashboardSummary React Query hook

**KpiGrid:** 5 cards — Total Accounts, Active Leads, Open Pipeline ($), Weighted Value ($), Win Rate (%)

**PipelineBarChart:** Recharts BarChart showing count per stage (5 bars); tooltips; empty state when no data

**ClosedDealsPanel:** Two cards side by side — Closed Won (count + $value in green) and Closed Lost (count + $value in red)

**RecentActivityFeed:** List of 5 activities; each shows type icon (phone/mail/calendar), subject, linked contact or opportunity name, relative time; Previous/Next pagination buttons with "Page X of Y"; "View all" link to /activities

**DashboardPage:** Composes KpiGrid + PipelineBarChart + ClosedDealsPanel + RecentActivityFeed; loading = skeleton placeholders; error = retry button

---

## WU-7: Frontend Seed Manager + Cross-module Wiring

### Files (Seed Manager)
- `frontend/src/features/admin/api.ts` (new — seedData(), clearData())
- `frontend/src/pages/admin/SeedManagerPage.tsx` (update — full implementation)

### Files (Cross-module wiring)
- `frontend/src/features/contacts/ContactHistoryTab.tsx` (update — real activity list filtered by contact_id)
- `frontend/src/features/contacts/ContactDetailPage.tsx` (update — add "days since last contact" derived from MAX(activity_date))
- `frontend/src/features/opportunities/OpportunityActivityList.tsx` (update — real list filtered by opportunity_id)
- `frontend/src/features/opportunities/OpportunityDetailPage.tsx` (update — "Log Activity" button opens ActivityForm pre-filled with opportunity_id)

### Key requirements

**SeedManagerPage:**
- "Seed demo data" button → POST /seed → renders summary panel with per-entity created/skipped counts
- "Clear all data" button → shows modal requiring user to type "CLEAR" to confirm → DELETE /seed → renders counts deleted
- Both buttons show loading state during request
- Error handling: show error message inline

**ContactHistoryTab:**
- Fetches /activities?contact_id=:id&limit=20 via React Query
- Renders timeline of activities (date, type icon, subject, notes preview)
- Empty state: "No activity history yet"

**ContactDetailPage:**
- Fetches most recent activity for contact (first item from /activities?contact_id=:id&limit=1&sort=activity_date_desc)
- Shows "Last contact: X days ago" or "Never contacted" in the header info section
- "Days since last contact" = floor((now - activity_date) / (1000 * 86400)), using activity_date field (not created_at)

**OpportunityActivityList:**
- Fetches /activities?opportunity_id=:id&limit=20
- Renders timeline; empty state: "No activities logged"

**OpportunityDetailPage:**
- "Log Activity" button (or "+ Activity" in header) opens ActivityForm pre-filled with opportunity_id=:id
- On form success: invalidates activities query for this opportunity
