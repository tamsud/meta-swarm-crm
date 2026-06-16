# Module Work Units: Leads

**Module**: `leads` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Tasks**: [tasks.md](tasks.md)

---

## Dependency Graph

### Upstream (most heavily-blocked module in the project)
- **Project Setup** WU-SETUP-9
- **Users** WU-USR-1 (FK target: `leads.created_by_user_id`)
- **Accounts** WU-ACCT-2 (service layer — `find_or_create_by_name`)
- **Contacts** WU-CONT-2 (service layer — `find_by_email`)
- **Opportunities** WU-OPP-1 (FK target: `leads.converted_opportunity_id`) + WU-OPP-2 (service — `create_opportunity`)
- **Authentication** WU-AUTH-3 (`get_current_user` + `require_permission` for ownership filter)

### Downstream
- **None.** Leads is terminal for downstream schema deps.

### Internal sequence
```
WU-LEAD-1 ──► WU-LEAD-2 ──► WU-LEAD-3 ──┬──► WU-LEAD-4 ──┐
                                          └──► WU-LEAD-5 ──┴──► WU-LEAD-6 ──┬──► WU-LEAD-7
                                                                              ├──► WU-LEAD-8
                                                                              └──► WU-LEAD-9
```

---

## Work Units

### WU-LEAD-1: Schema Migration
**Tasks**: T-LEAD-1
**Depends on**: Users WU-USR-1, Opportunities WU-OPP-1

**File scope**:
- `backend/alembic/versions/0011_create_leads.py` (new)

**Definition of Done**:
- [ ] `leads` table: `(id, first_name, last_name, email, phone, company, status lead_status, source, notes, created_by_user_id FK nullable, converted_opportunity_id FK nullable, converted_at nullable, created_at, updated_at)`
- [ ] `lead_status` ENUM with exactly 4 spec values: `new`, `contacted`, `qualified`, `lost`
- [ ] FK `created_by_user_id` → `users(id)` `ON DELETE SET NULL` (preserves audit history when a User is hard-deleted — see users/plan.md "Soft deactivation only")
- [ ] FK `converted_opportunity_id` → `opportunities(id)` `ON DELETE SET NULL`
- [ ] Downgrade reverses cleanly

**Success Criteria covered**: SC-LEAD-001

---

### WU-LEAD-2: ORM + Schemas
**Tasks**: T-LEAD-2, T-LEAD-3
**Depends on**: WU-LEAD-1

**File scope**:
- `backend/app/models/lead.py` (new)
- `backend/app/schemas/lead.py` (new — `LeadCreate`, `LeadUpdate`, `LeadResponse`; conversion endpoint returns `OpportunityResponse` per plan.md — no separate `LeadConvertResponse` schema)

**Definition of Done**:
- [ ] `LeadResponse` includes `converted_opportunity_id` and `created_by_user_id` (read-only)
- [ ] `LeadUpdate` does NOT allow patching `created_by_user_id` or `converted_opportunity_id` (extra=forbid)

**Success Criteria covered**: SC-LEAD-001

---

### WU-LEAD-3: State-Machine Validation
**Tasks**: T-LEAD-4
**Depends on**: WU-LEAD-2

**File scope**:
- `backend/app/services/lead_service.py` (new — `validate_status_transition(current, next)` + transition table)

**Definition of Done**:
- [ ] Transition table encoded as data: `VALID_TRANSITIONS = {new: [contacted, lost], contacted: [qualified, lost], qualified: [lost], lost: []}`
- [ ] Any transition away from `lost` is rejected (lost is terminal)
- [ ] Any transition away from a converted Lead is rejected
- [ ] Invalid transitions raise `INVALID_LEAD_TRANSITION` (400) with both current + attempted status in the payload
- [ ] Unit tests cover all valid + invalid transitions exhaustively (4×4 matrix test)

**Success Criteria covered**: SC-LEAD-001

---

### WU-LEAD-4: Ownership Filter
**Tasks**: T-LEAD-5
**Depends on**: WU-LEAD-3, Authentication WU-AUTH-3 (resolved permissions on the current user)

**File scope**:
- `backend/app/services/lead_service.py` (modify — `apply_ownership_filter(query, user)`, `assert_ownership(lead, user)`)

**Definition of Done**:
- [ ] Manager / Admin (those with `leads:manage-all`) see/edit/delete any lead
- [ ] Sales Rep (with only `leads:manage-own`) see only `created_by_user_id == current_user.id`
- [ ] `assert_ownership` raises 403 when a Sales Rep targets another user's lead
- [ ] Filter applied in the SQL query (NOT post-filtered in Python) — verified by query plan inspection in a test

**Success Criteria covered**: SC-LEAD-003

---

### WU-LEAD-5: Conversion Orchestration
**Tasks**: T-LEAD-6
**Depends on**: WU-LEAD-3, Accounts WU-ACCT-2 (`find_or_create_by_name`), Contacts WU-CONT-2 (`find_by_email`, `create_contact`), Opportunities WU-OPP-2 (`create_opportunity`)

**File scope**:
- `backend/app/services/lead_service.py` (modify — `convert_lead(lead_id, payload, user)`)

**Definition of Done**:
- [ ] Entire conversion wrapped in a single `async with session.begin():` transaction
- [ ] Step 1: validate lead is `qualified` and `converted_opportunity_id IS NULL`, else `LEAD_ALREADY_CONVERTED` (400) with existing opportunity id
- [ ] Step 2: `find_or_create_by_name(lead.company)` → account (case-insensitive)
- [ ] Step 3: `find_by_email(lead.email)` OR create new contact (linked to account)
- [ ] Step 4: `create_opportunity(...)` — receives account_id + contact_id from steps 2/3
- [ ] Step 5: update lead with `converted_opportunity_id` + `converted_at = now()`
- [ ] Forced mid-transaction failure (test injects exception in step 4) rolls back ALL writes; `accounts`, `contacts`, `opportunities` row counts unchanged; `leads.converted_opportunity_id` remains NULL

**Success Criteria covered**: SC-LEAD-002

---

### WU-LEAD-6: Router
**Tasks**: T-LEAD-7
**Depends on**: WU-LEAD-3, WU-LEAD-4, WU-LEAD-5, Authentication WU-AUTH-3

**File scope**:
- `backend/app/routers/leads.py` (new — GET list, GET one, POST, PATCH, DELETE, POST `/:id/convert`)
- `backend/app/main.py` (modify — register router)

**Definition of Done**:
- [ ] All endpoints gated by `require_permission("leads:{action}")`
- [ ] `GET /leads` applies ownership filter automatically
- [ ] `PATCH /leads/:id` routes through `validate_status_transition` AND `assert_ownership`
- [ ] `POST /leads/:id/convert` returns `201 OpportunityResponse` (per plan.md) — frontend reads `id` to link the new Opportunity
- [ ] Re-converting returns 400 `LEAD_ALREADY_CONVERTED` with existing opportunity id in body

**Success Criteria covered**: SC-LEAD-002, SC-LEAD-003

---

### WU-LEAD-7: Frontend List Page
**Tasks**: T-LEAD-8
**Depends on**: WU-LEAD-6

**File scope**:
- `frontend/src/features/leads/LeadsListPage.tsx` (new — status tabs across the top, search)
- `frontend/src/features/leads/LeadForm.tsx` (new — create modal)
- `frontend/src/features/leads/api.ts` (new)
- `frontend/src/routes/index.tsx` (modify — register `/leads`)

**Definition of Done**:
- [ ] Status tabs (New / Contacted / Qualified / Lost / Converted) drive `?status=` filter
- [ ] Search hits `?search=` query param
- [ ] Sales Rep sees only their own leads automatically (server-side filter — frontend does nothing special)

**Success Criteria covered**: SC-LEAD-003

---

### WU-LEAD-8: Frontend Detail + Convert Flow
**Tasks**: T-LEAD-9
**Depends on**: WU-LEAD-6

**File scope**:
- `frontend/src/features/leads/LeadDetailPage.tsx` (new)
- `frontend/src/features/leads/LeadStatusControl.tsx` (new — shows only valid next-states from the transition table)
- `frontend/src/features/leads/LeadConvertModal.tsx` (new — confirms conversion + shows result links)
- `frontend/src/routes/index.tsx` (modify — register `/leads/:id`)

**Definition of Done**:
- [ ] `LeadStatusControl` disables invalid transitions visually (greys/hides them)
- [ ] Convert button hidden when lead status ≠ `qualified` or already converted
- [ ] After convert: shows badge with linked Opportunity, navigable to `/opportunities/:id`
- [ ] 400 `LEAD_ALREADY_CONVERTED` surfaces inline with link to existing opportunity

**Success Criteria covered**: SC-LEAD-002

---

### WU-LEAD-9: Integration Tests
**Tasks**: T-LEAD-10
**Depends on**: WU-LEAD-6

**File scope**:
- `backend/tests/test_leads_integration.py` (new)
- `backend/tests/test_leads_atomicity.py` (new — separate file for the rollback test)

**Definition of Done**:
- [ ] Test: every cell of the transition matrix (valid → 200, invalid → 400)
- [ ] Test: happy-path convert creates exactly 1 account, 1 contact, 1 opportunity; lead updated
- [ ] Test: atomicity — patch `create_opportunity` to raise mid-transaction; assert account/contact/opportunity row counts unchanged AND `lead.converted_opportunity_id IS NULL`
- [ ] Test: re-convert returns 400 `LEAD_ALREADY_CONVERTED` with existing opportunity_id in body
- [ ] Test: Sales Rep cannot update/delete another user's lead → 403
- [ ] Test: Manager/Admin can act on any lead → 200/204

**Success Criteria covered**: SC-LEAD-001, SC-LEAD-002, SC-LEAD-003
