# Module Work Units: Opportunities

**Module**: `opportunities` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Tasks**: [tasks.md](tasks.md)

---

## Dependency Graph

### Upstream
- **Project Setup** WU-SETUP-9
- **Accounts** WU-ACCT-1 (FK target)
- **Contacts** WU-CONT-1 (FK target — nullable but still required schema)

### Downstream
- **Activities** WU-ACT-1 (FK target: `activities.opportunity_id`)
- **Leads** WU-LEAD-5 (conversion needs `create_opportunity`)

### Internal sequence
```
WU-OPP-1 ──► WU-OPP-2 ──► WU-OPP-3 ──┬──► WU-OPP-4
                                       ├──► WU-OPP-5
                                       └──► WU-OPP-6
```

---

## Work Units

### WU-OPP-1: Schema Migration
**Tasks**: T-OPP-1
**Depends on**: Accounts WU-ACCT-1, Contacts WU-CONT-1
**Parallelizable with**: Contacts WU-CONT-2/3 (they don't need Opportunities)

**File scope**:
- `backend/alembic/versions/0010_create_opportunities.py` (new)

**Definition of Done**:
- [ ] `opportunities` table: `(id, title, account_id FK NOT NULL, contact_id FK nullable, stage opportunity_stage, value NUMERIC, probability INT, expected_close_date, created_at, updated_at)`
- [ ] `opportunity_stage` ENUM with the 5 spec values; default `prospecting`
- [ ] CHECK constraint: `value > 0` AND `probability BETWEEN 0 AND 100`
- [ ] FK to accounts/contacts with appropriate `ON DELETE` (RESTRICT — Accounts/Contacts dependency-guard owns it)
- [ ] Downgrade reverses cleanly

**Success Criteria covered**: SC-OPP-001

---

### WU-OPP-2: ORM + Schemas + Service
**Tasks**: T-OPP-2, T-OPP-3, T-OPP-4
**Depends on**: WU-OPP-1, Accounts WU-ACCT-2 + Contacts WU-CONT-2 (read functions for FK validation)

**File scope**:
- `backend/app/models/opportunity.py` (new)
- `backend/app/schemas/opportunity.py` (new — `OpportunityCreate`, `OpportunityUpdate`, `OpportunityResponse`; value > 0 + probability 0–100 validators)
- `backend/app/services/opportunity_service.py` (new — `create`, `get`, `list (filter by stage/account, sort, paginate)`, `update`, `delete`)

**Definition of Done**:
- [ ] Pydantic validator rejects `value ≤ 0` and `probability < 0 || > 100` with 422 BEFORE DB write
- [ ] Default `stage = "prospecting"` applied when create omits it
- [ ] `account_id` validated to exist; optional `contact_id` validated if provided
- [ ] Stage updates accept any-to-any transition (no sequence rules)
- [ ] List supports `?stage=...` filter

**Success Criteria covered**: SC-OPP-001, SC-OPP-003

---

### WU-OPP-3: Router
**Tasks**: T-OPP-5
**Depends on**: WU-OPP-2, Authentication WU-AUTH-3

**File scope**:
- `backend/app/routers/opportunities.py` (new — GET list, GET one, POST, PATCH, DELETE)
- `backend/app/main.py` (modify — register router)

**Definition of Done**:
- [ ] Each endpoint gated by `require_permission("opportunities:{action}")`
- [ ] `DELETE` requires `opportunities:delete` (Manager/Admin only) — Sales Rep gets 403
- [ ] Query params validated at boundary

**Success Criteria covered**: SC-OPP-003

---

### WU-OPP-4: Frontend Board + Table Page
**Tasks**: T-OPP-6
**Depends on**: WU-OPP-3, Accounts WU-ACCT-3, Contacts WU-CONT-3 (for filter dropdowns)

**File scope**:
- `frontend/src/features/opportunities/OpportunitiesPage.tsx` (new — board/table toggle)
- `frontend/src/features/opportunities/OpportunityBoard.tsx` (new — 5-column Kanban)
- `frontend/src/features/opportunities/OpportunityTable.tsx` (new)
- `frontend/src/features/opportunities/OpportunityForm.tsx` (new)
- `frontend/src/features/opportunities/api.ts` (new)
- `frontend/src/routes/index.tsx` (modify — register `/opportunities`)

**Definition of Done**:
- [ ] Board view groups records into the 5 stage columns with accurate per-stage totals
- [ ] Table view paginates + sorts
- [ ] Stage drag-and-drop (board) PATCHes the stage with no validation error
- [ ] Filter dropdowns sourced from `GET /accounts` and `GET /contacts`

**Success Criteria covered**: SC-OPP-002, SC-OPP-003

---

### WU-OPP-5: Frontend Detail Page
**Tasks**: T-OPP-7
**Depends on**: WU-OPP-3

**File scope**:
- `frontend/src/features/opportunities/OpportunityDetailPage.tsx` (new)
- `frontend/src/features/opportunities/OpportunityActivityList.tsx` (new — renders empty until Activities ships)
- `frontend/src/routes/index.tsx` (modify — register `/opportunities/:id`)

**Definition of Done**:
- [ ] Detail page renders all fields + linked account/contact (clickable)
- [ ] Stage control allows any-to-any transitions
- [ ] Delete visible only with `opportunities:delete` permission
- [ ] Activity list renders empty placeholder until Activities WU-ACT-6 wires it in

**Success Criteria covered**: SC-OPP-003

---

### WU-OPP-6: Integration Tests
**Tasks**: T-OPP-8
**Depends on**: WU-OPP-3

**File scope**:
- `backend/tests/test_opportunities_integration.py` (new)

**Definition of Done**:
- [ ] Test: create without `stage` → stage = `prospecting`
- [ ] Test: `value = 0` → 422 (before DB)
- [ ] Test: `value = -1` → 422
- [ ] Test: `probability = -1` → 422; `probability = 101` → 422
- [ ] Test: stage transition `closed_won → prospecting` succeeds (no sequence restriction)
- [ ] Test: `GET /opportunities?stage=proposal` returns only that stage
- [ ] Test: Sales Rep DELETE → 403; Manager DELETE → 204

**Success Criteria covered**: SC-OPP-001, SC-OPP-002, SC-OPP-003
