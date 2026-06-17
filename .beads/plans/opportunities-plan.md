# Module Implementation Plan: Opportunities

**Module**: `opportunities`  
**Work Unit Count**: 6 (WU-OPP-1 through WU-OPP-6)  
**Status**: approved
**Spec Reference**: `specs/opportunities/spec.md`  
**Plan Reference**: `specs/opportunities/plan.md`  
**Tasks Reference**: `specs/opportunities/tasks.md`

---

## Prerequisites

Before starting implementation:
- **Accounts module** (WU-ACCT-1, WU-ACCT-2) must be complete - provides `account_id` FK target
- **Contacts module** (WU-CONT-1, WU-CONT-2) must be complete - provides `contact_id` FK target
- **Authentication** (WU-AUTH-3) must be complete - provides `require_permission` dependency

---

## Work Unit Details

### WU-OPP-1: Schema Migration

**Tasks**: T-OPP-1  
**Dependencies**: Accounts WU-ACCT-1, Contacts WU-CONT-1  
**Estimated Time**: 1-2 hours

**File Scope**:
- `backend/alembic/versions/0010_create_opportunities.py` (new)

**Definition of Done**:
- [ ] `opportunities` table with columns: `id`, `title`, `account_id` (FK NOT NULL), `contact_id` (FK nullable), `stage` (ENUM), `value` (NUMERIC), `probability` (INT), `expected_close_date`, `created_at`, `updated_at`
- [ ] `opportunity_stage` ENUM with 5 values: `prospecting`, `proposal`, `negotiation`, `closed_won`, `closed_lost`
- [ ] DEFAULT `prospecting` for stage column
- [ ] CHECK constraint: `value > 0` when not NULL
- [ ] CHECK constraint: `probability BETWEEN 0 AND 100` when not NULL
- [ ] FK to `accounts(id)` with `ON DELETE RESTRICT`
- [ ] FK to `contacts(id)` with `ON DELETE SET NULL`
- [ ] Downgrade reverses cleanly (drop table, drop enum type)

**Pattern Reference**: Follow `backend/alembic/versions/0006_create_accounts.py` structure

---

### WU-OPP-2: ORM + Schemas + Service

**Tasks**: T-OPP-2, T-OPP-3, T-OPP-4  
**Dependencies**: WU-OPP-1, Accounts WU-ACCT-2, Contacts WU-CONT-2  
**Estimated Time**: 3-4 hours

**File Scope**:
- `backend/app/models/opportunity.py` (new)
- `backend/app/schemas/opportunity.py` (new)
- `backend/app/services/opportunity_service.py` (new)
- `backend/app/models/__init__.py` (modify - add Opportunity import)
- `backend/app/exceptions.py` (modify - add Opportunity exceptions)

**Definition of Done**:
- [ ] `OpportunityStage` Enum with 5 values: prospecting, proposal, negotiation, closed_won, closed_lost
- [ ] `Opportunity` ORM model with all columns and relationships
- [ ] `OpportunityCreate` schema with:
  - `title` (required, str)
  - `account_id` (required, int)
  - `contact_id` (optional, int)
  - `stage` (optional, default to None - service sets default)
  - `value` (optional, Decimal > 0 validator)
  - `probability` (optional, int 0-100 validator)
  - `expected_close_date` (optional, date)
- [ ] `OpportunityUpdate` schema with all optional fields
- [ ] `OpportunityResponse` schema with `ConfigDict(from_attributes=True)`
- [ ] Pydantic `field_validator` rejects `value <= 0` with 422
- [ ] Pydantic `field_validator` rejects `probability < 0 or > 100` with 422
- [ ] Service function `create_opportunity`: validates `account_id` exists, validates `contact_id` if provided, defaults stage to `prospecting`
- [ ] Service function `get_opportunity`: raises `OpportunityNotFoundError` if not found
- [ ] Service function `list_opportunities`: supports `stage`, `account_id`, `contact_id` filters, pagination, sorting
- [ ] Service function `update_opportunity`: any-to-any stage transition allowed
- [ ] Service function `delete_opportunity`: raises `OpportunityNotFoundError` if not found
- [ ] New exceptions in `exceptions.py`: `OpportunityNotFoundError`, `InvalidAccountIdError`, `InvalidContactIdError`

**Pattern Reference**: Follow `backend/app/models/account.py`, `backend/app/schemas/account.py`, `backend/app/services/account_service.py`

---

### WU-OPP-3: Router

**Tasks**: T-OPP-5  
**Dependencies**: WU-OPP-2, Authentication WU-AUTH-3  
**Estimated Time**: 2-3 hours

**File Scope**:
- `backend/app/routers/opportunities.py` (new)
- `backend/app/main.py` (modify - register router)
- `backend/app/routers/__init__.py` (modify - add opportunities import)

**Definition of Done**:
- [ ] `GET /opportunities` - list with filters (`stage`, `account_id`, `contact_id`), pagination (`offset`, `limit`), sorting - requires `opportunities:read`
- [ ] `GET /opportunities/{id}` - single opportunity - requires `opportunities:read`
- [ ] `POST /opportunities` - create new - requires `opportunities:create`
- [ ] `PATCH /opportunities/{id}` - update existing - requires `opportunities:update`
- [ ] `DELETE /opportunities/{id}` - delete - requires `opportunities:delete` (Manager/Admin only)
- [ ] Sales Rep calling DELETE gets 403 Forbidden
- [ ] Query params validated at router boundary
- [ ] Router registered in `main.py`

**Pattern Reference**: Follow `backend/app/routers/accounts.py` structure

---

### WU-OPP-4: Frontend Board + Table Page

**Tasks**: T-OPP-6  
**Dependencies**: WU-OPP-3, Accounts WU-ACCT-3, Contacts WU-CONT-3  
**Estimated Time**: 6-8 hours

**File Scope**:
- `frontend/src/features/opportunities/OpportunitiesPage.tsx` (new)
- `frontend/src/features/opportunities/OpportunityBoard.tsx` (new)
- `frontend/src/features/opportunities/OpportunityTable.tsx` (new)
- `frontend/src/features/opportunities/OpportunityForm.tsx` (new)
- `frontend/src/features/opportunities/OpportunityCard.tsx` (new - for Kanban)
- `frontend/src/features/opportunities/api.ts` (new)
- `frontend/src/features/opportunities/types.ts` (new)
- `frontend/src/routes/index.tsx` (modify - update OPPORTUNITIES route)
- `frontend/src/pages/PipelinePage.tsx` (remove or replace)

**Definition of Done**:
- [ ] Board view groups opportunities into 5 stage columns (Kanban)
- [ ] Each column shows count and total value for that stage
- [ ] Table view with pagination, sorting by value/close date/created_at
- [ ] Toggle button persists view preference (localStorage)
- [ ] Stage drag-and-drop on board triggers PATCH with optimistic update
- [ ] Filter dropdowns: stage (multi-select), account (from GET /accounts), contact (scoped to selected account via GET /contacts?account_id=)
- [ ] Create/Edit form modal with validation
- [ ] Delete confirmation with permission check (`opportunities:delete`)
- [ ] Responsive layout for board columns

**Pattern Reference**: Follow `frontend/src/features/accounts/AccountsListPage.tsx`, `frontend/src/features/accounts/AccountForm.tsx`

---

### WU-OPP-5: Frontend Detail Page

**Tasks**: T-OPP-7  
**Dependencies**: WU-OPP-3  
**Estimated Time**: 3-4 hours

**File Scope**:
- `frontend/src/features/opportunities/OpportunityDetailPage.tsx` (new)
- `frontend/src/features/opportunities/OpportunityActivityList.tsx` (new - placeholder)
- `frontend/src/routes/index.tsx` (modify - add `/opportunities/:id` route)
- `frontend/src/routes/config.ts` (modify - add OPPORTUNITY_DETAIL constant)

**Definition of Done**:
- [ ] Detail page renders all fields: title, stage, value, probability, expected_close_date, timestamps
- [ ] Linked account displayed as clickable link to `/accounts/:id`
- [ ] Linked contact displayed as clickable link (if exists)
- [ ] Stage dropdown/control allows any-to-any transitions
- [ ] Edit button opens form modal
- [ ] Delete button visible only with `opportunities:delete` permission
- [ ] Activity list section renders empty placeholder with message "Activities will appear here once the Activities module is complete"

**Pattern Reference**: Follow `frontend/src/features/accounts/AccountDetailPage.tsx`

---

### WU-OPP-6: Integration Tests

**Tasks**: T-OPP-8  
**Dependencies**: WU-OPP-3  
**Estimated Time**: 2-3 hours

**File Scope**:
- `backend/tests/test_opportunities_integration.py` (new)

**Definition of Done**:
- [ ] Test: Create opportunity without `stage` - stage defaults to `prospecting`
- [ ] Test: Create opportunity with `value = 0` - returns 422 before DB write
- [ ] Test: Create opportunity with `value = -1` - returns 422
- [ ] Test: Create opportunity with `probability = -1` - returns 422
- [ ] Test: Create opportunity with `probability = 101` - returns 422
- [ ] Test: PATCH stage from `closed_won` to `prospecting` - succeeds (non-linear allowed)
- [ ] Test: GET `/opportunities?stage=proposal` - returns only matching records
- [ ] Test: Sales Rep DELETE - returns 403
- [ ] Test: Manager DELETE - returns 204
- [ ] Test: Create with invalid `account_id` - returns 422
- [ ] Test: Create with invalid `contact_id` - returns 422
- [ ] Test: GET `/opportunities/{id}` with non-existent ID - returns 404

**Pattern Reference**: Follow `backend/tests/test_roles_integration.py`

---

## Execution Sequence Diagram

```
                    [Prerequisites]
                          |
        +-----------------+-----------------+
        |                                   |
   Accounts             Contacts       Authentication
   WU-ACCT-1            WU-CONT-1       WU-AUTH-3
   WU-ACCT-2            WU-CONT-2
        |                   |               |
        +---------+---------+---------------+
                  |
                  v
           [WU-OPP-1]
         Schema Migration
           (1-2 hours)
                  |
                  v
           [WU-OPP-2]
      ORM + Schemas + Service
           (3-4 hours)
                  |
        +---------+---------+
        |                   |
        v                   |
   [WU-OPP-3]              |
     Router                 |
   (2-3 hours)              |
        |                   |
   +----+----+----+         |
   |         |    |         |
   v         v    v         |
[WU-OPP-4][WU-OPP-5][WU-OPP-6]
  Board    Detail   Tests
 (6-8h)   (3-4h)   (2-3h)
   |         |        |
   +---------+--------+
             |
             v
    [Module Complete]
```

---

## Human Checkpoint Locations

| Checkpoint | After WU | Review Focus | Decision Gate |
|------------|----------|--------------|---------------|
| **CP-1** | WU-OPP-1 | Migration SQL, constraints, enum values | Approve before ORM implementation |
| **CP-2** | WU-OPP-2 | Schema validators, service logic, exception handling | Approve before API exposure |
| **CP-3** | WU-OPP-3 | API contract, permission gating, response format | Approve before frontend work |
| **CP-4** | WU-OPP-4 | Board UX, drag-drop behavior, filter interactions | Demo and iterate |
| **CP-5** | WU-OPP-6 | Test coverage completeness, edge cases | Final sign-off |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Contacts module not ready** | Medium | High | Stub contact_id validation initially; complete when Contacts ships |
| **Kanban drag-drop complexity** | Medium | Medium | Use established library (react-beautiful-dnd or @dnd-kit); keep optimistic updates simple |
| **Stage enum mismatch between FE/BE** | Low | High | Define shared constant; generate types from OpenAPI spec |
| **CHECK constraints not portable to SQLite tests** | Medium | Medium | Use in-memory SQLite for unit tests but Postgres for integration; document constraint differences |
| **Value/probability validation bypass** | Low | High | Defense in depth: Pydantic validators + DB constraints ensure double validation |

---

## Downstream Impact

Once this module is complete:
- **Leads module** (WU-LEAD-5) can implement conversion to create Opportunity rows
- **Activities module** (WU-ACT-1) can add `opportunity_id` FK column
- **Account detail page** can populate its Opportunities tab via `GET /opportunities?account_id=`
- **Dashboard** can query pipeline metrics from this module's data
