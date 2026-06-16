# Module Work Units: Activities

**Module**: `activities` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Tasks**: [tasks.md](tasks.md)

---

## Dependency Graph

### Upstream
- **Project Setup** WU-SETUP-9
- **Contacts** WU-CONT-1 (FK target: `activities.contact_id`)
- **Opportunities** WU-OPP-1 (FK target: `activities.opportunity_id`)
- **Users** WU-USR-1 (FK target: `activities.created_by_user_id`)
- **Authentication** WU-AUTH-3 (for ownership filter)

### Downstream
- **None.** Activities is a terminal leaf module — no schema or service depends on it.
- Cross-module *read* dependencies: Contacts detail page + Opportunities detail page consume Activities API.

### Internal sequence
```
WU-ACT-1 ──► WU-ACT-2 ──► WU-ACT-3 ──► WU-ACT-4 ──┬──► WU-ACT-5
                                                    ├──► WU-ACT-6
                                                    └──► WU-ACT-7
```

---

## Work Units

### WU-ACT-1: Schema Migration
**Tasks**: T-ACT-1
**Depends on**: Contacts WU-CONT-1, Opportunities WU-OPP-1, Users WU-USR-1

**File scope**:
- `backend/alembic/versions/0012_create_activities.py` (new)

**Definition of Done**:
- [ ] `activities` table: `(id, type activity_type, subject, notes, activity_date DEFAULT now(), contact_id FK nullable, opportunity_id FK nullable, created_by_user_id FK nullable, created_at, updated_at)`
- [ ] `activity_type` ENUM with 3 spec values (call / email / meeting)
- [ ] CHECK constraint: `contact_id IS NOT NULL OR opportunity_id IS NOT NULL` (link-required)
- [ ] FK `created_by_user_id` → `users(id)` `ON DELETE SET NULL` (preserves audit history — see users/plan.md "Soft deactivation only")
- [ ] FKs `contact_id` / `opportunity_id` use `ON DELETE RESTRICT` (Contacts/Opportunities dependency-guard owns those)
- [ ] Downgrade reverses cleanly

**Success Criteria covered**: SC-ACT-001

---

### WU-ACT-2: ORM + Schemas
**Tasks**: T-ACT-2, T-ACT-3
**Depends on**: WU-ACT-1

**File scope**:
- `backend/app/models/activity.py` (new)
- `backend/app/schemas/activity.py` (new — `ActivityCreate`, `ActivityUpdate`, `ActivityResponse`)

**Definition of Done**:
- [ ] `ActivityCreate` model_validator: `contact_id` or `opportunity_id` (or both) must be set, else `ACTIVITY_NO_LINK` (400) BEFORE DB write
- [ ] `activity_date` defaults to `datetime.utcnow()` in the schema when omitted
- [ ] Pydantic enum rejects invalid `type` values with 422

**Success Criteria covered**: SC-ACT-001

---

### WU-ACT-3: Service Layer
**Tasks**: T-ACT-4
**Depends on**: WU-ACT-2, Contacts WU-CONT-2 + Opportunities WU-OPP-2 (read functions for FK validation)

**File scope**:
- `backend/app/services/activity_service.py` (new — `create`, `get`, `list (filter by type/contact/opportunity, sort, paginate)`, `update`, `delete`, `assert_ownership`)

**Definition of Done**:
- [ ] `contact_id` / `opportunity_id` validated to exist (when provided) — 422 otherwise
- [ ] Ownership filter mirrors Leads: Sales Rep (with only `activities:manage-own`) can only see/edit/delete own; Manager/Admin (with `activities:manage-all`) can act on any
- [ ] `assert_ownership` raises 403 for cross-user mutations by Sales Rep
- [ ] List ordering defaults to `activity_date DESC` (timeline ordering)

**Success Criteria covered**: SC-ACT-002

---

### WU-ACT-4: Router
**Tasks**: T-ACT-5
**Depends on**: WU-ACT-3, Authentication WU-AUTH-3

**File scope**:
- `backend/app/routers/activities.py` (new — GET list, GET one, POST, PATCH, DELETE)
- `backend/app/main.py` (modify — register router)

**Definition of Done**:
- [ ] Each endpoint gated by `require_permission("activities:{action}")`
- [ ] `?type=`, `?contact_id=`, `?opportunity_id=` filters validated at boundary
- [ ] Link-required error from schema returns 400 `ACTIVITY_NO_LINK` (not the default 422 wrapping)

**Success Criteria covered**: SC-ACT-001, SC-ACT-002

---

### WU-ACT-5: Frontend Timeline Page
**Tasks**: T-ACT-6
**Depends on**: WU-ACT-4

**File scope**:
- `frontend/src/features/activities/ActivitiesPage.tsx` (new — unified timeline view)
- `frontend/src/features/activities/ActivityForm.tsx` (new — type selector, contact + opportunity pickers)
- `frontend/src/features/activities/api.ts` (new)
- `frontend/src/routes/index.tsx` (modify — register `/activities`)

**Definition of Done**:
- [ ] Timeline groups activities by date (descending)
- [ ] Filter chips for type (call / email / meeting)
- [ ] Form blocks submission if neither contact nor opportunity is picked (client-side mirror of server CHECK)
- [ ] Empty state matches mock under `mocks/activities.html`

**Success Criteria covered**: SC-ACT-001

---

### WU-ACT-6: Cross-Module Frontend Wiring
**Tasks**: T-ACT-7
**Depends on**: WU-ACT-4, Contacts WU-CONT-5, Opportunities WU-OPP-5

**File scope** (modify only):
- `frontend/src/features/contacts/ContactHistoryTab.tsx` (replace empty state with `ActivityList` filtered by `contact_id`)
- `frontend/src/features/contacts/ContactDetailPage.tsx` (add "days since last contact" header field — derived from latest activity)
- `frontend/src/features/opportunities/OpportunityActivityList.tsx` (replace empty state with real list)
- `frontend/src/features/opportunities/OpportunityDetailPage.tsx` (add "Log activity" button → opens `ActivityForm` pre-filled with `opportunity_id`)

**Definition of Done**:
- [ ] Contact detail's History tab renders activities filtered to that contact
- [ ] "Days since last contact" computes from the most recent activity, or "Never" if zero
- [ ] Opportunity detail's activity list renders and the Log button pre-fills the opportunity context

**Success Criteria covered**: SC-ACT-001

---

### WU-ACT-7: Integration Tests
**Tasks**: T-ACT-8
**Depends on**: WU-ACT-4

**File scope**:
- `backend/tests/test_activities_integration.py` (new)

**Definition of Done**:
- [ ] Test: POST with both link fields null → 400 `ACTIVITY_NO_LINK` (Pydantic-level, before DB)
- [ ] Test: DB-level CHECK constraint also rejects a direct SQL insert with both nulls (defense in depth)
- [ ] Test: POST with both contact_id + opportunity_id set → 201 (dual-link supported)
- [ ] Test: `GET /activities?type=call` returns only call rows
- [ ] Test: omit `activity_date` → stored value equals creation timestamp (within tolerance)
- [ ] Test: Sales Rep cannot update/delete another user's activity → 403
- [ ] Test: Manager DELETE on any activity → 204

**Success Criteria covered**: SC-ACT-001, SC-ACT-002
