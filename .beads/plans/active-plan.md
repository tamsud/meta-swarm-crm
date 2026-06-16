# Active Plan: Accounts/Users Frontend Pages
<!-- approved: 2026-06-17T21:30:00Z -->
<!-- gate-iterations: 3 -->
<!-- user-approved: true -->
<!-- status: complete -->

## Overview

Build frontend pages for Accounts and Users modules. Backend APIs already exist. This plan covers 4 work units: WU-ACCT-4, WU-ACCT-5, WU-USR-6, WU-USR-7.

## Work Units

| WU | Description | Status |
|----|-------------|--------|
| WU-ACCT-4 | Accounts List + Form | complete |
| WU-ACCT-5 | Account Detail Page | complete |
| WU-USR-6 | Users Admin Page | complete |
| WU-USR-7 | Profile Page | complete |

## Execution Order

1. WU-ACCT-4 (Accounts List + Form) - no FE dependencies
2. WU-ACCT-5 (Account Detail Page) - depends on WU-ACCT-4 for shared API
3. WU-USR-6 (Users Admin Page) - independent of Accounts, can parallel with ACCT-5
4. WU-USR-7 (Profile Page) - depends on WU-USR-6 for shared API

---

## WU-ACCT-4: Accounts List + Form

**File Scope:**
- `frontend/src/features/accounts/api.ts` (CREATE)
- `frontend/src/features/accounts/types.ts` (CREATE)
- `frontend/src/features/accounts/AccountsListPage.tsx` (CREATE)
- `frontend/src/features/accounts/AccountForm.tsx` (CREATE)
- `frontend/src/pages/AccountsPage.tsx` (UPDATE - replace placeholder)
- `frontend/src/routes/index.tsx` (UPDATE - if needed)

**Definition of Done:**
- [ ] API client calls GET /accounts, POST /accounts, PATCH /accounts/:id, DELETE /accounts/:id
- [ ] List page displays accounts in a table matching mock (Name, Industry, Website columns)
- [ ] List supports pagination via URL params (?offset=X&limit=Y)
- [ ] List supports search filter via URL param (?search=X)
- [ ] List ordered by ID (backend default) — sorting deferred to future enhancement
- [ ] "New Account" button opens modal form
- [ ] Form validates required field (name)
- [ ] Edit button opens form pre-filled with account data
- [ ] Delete button visible only when `hasPermission("accounts:delete")`
- [ ] Delete shows confirmation dialog
- [ ] 409 ACCOUNT_HAS_DEPENDENTS error surfaces both counts in toast
- [ ] Loading state shows skeleton/spinner
- [ ] Empty state shows appropriate message

---

## WU-ACCT-5: Account Detail Page

**File Scope:**
- `frontend/src/features/accounts/AccountDetailPage.tsx` (CREATE)
- `frontend/src/features/accounts/AccountContactsTab.tsx` (CREATE - placeholder)
- `frontend/src/features/accounts/AccountOpportunitiesTab.tsx` (CREATE - placeholder)
- `frontend/src/routes/index.tsx` (UPDATE - add /accounts/:id route)
- `frontend/src/routes/config.ts` (UPDATE - add ACCOUNT_DETAIL route)

**Definition of Done:**
- [ ] Detail page renders at /accounts/:id
- [ ] Shows account fields (name, industry, website, phone, address)
- [ ] Edit button opens AccountForm in edit mode
- [ ] Tab strip with Contacts and Opportunities tabs
- [ ] Contacts tab shows "Coming soon" placeholder (until Contacts module ships)
- [ ] Opportunities tab shows "Coming soon" placeholder (until Opportunities module ships)
- [ ] Tab components designed for extensibility: downstream modules update tab files directly (no refactor to AccountDetailPage.tsx needed)
- [ ] Back button returns to accounts list
- [ ] 404 handling for non-existent account ID

---

## WU-USR-6: Users Admin Page

**File Scope:**
- `frontend/src/features/users/api.ts` (CREATE)
- `frontend/src/features/users/types.ts` (CREATE)
- `frontend/src/features/users/UsersListPage.tsx` (CREATE)
- `frontend/src/features/users/UserForm.tsx` (CREATE)
- `frontend/src/pages/admin/UsersPage.tsx` (UPDATE - replace placeholder)

**Definition of Done:**
- [ ] API client calls GET /users, POST /users, PATCH /users/:id
- [ ] List page displays users in table (Email, Display Name, Role, Status columns)
- [ ] List supports pagination, search filter, role filter
- [ ] Role filter dropdown populated from GET /roles
- [ ] "New User" button opens modal form
- [ ] Form has email, password (create only), display_name, role dropdown, is_active toggle
- [ ] Role dropdown populated from GET /roles API
- [ ] Edit button opens form (password field hidden for edit)
- [ ] Deactivate toggle shows confirmation dialog
- [ ] LAST_ADMIN_LOCKOUT error (400) surfaces inline with clear message
- [ ] Page requires users:manage permission (route guard or inline check)

---

## WU-USR-7: Profile Page

**Note**: tasks.md T-USR-8 mentions "Admin's embedded Users tab" but work-units.md WU-USR-7 (authoritative DoD) does not include this. Following work-units.md.

**File Scope:**
- `frontend/src/features/users/ProfilePage.tsx` (CREATE)
- `frontend/src/routes/index.tsx` (UPDATE - add /profile route)
- `frontend/src/routes/config.ts` (UPDATE - add PROFILE route)

**Definition of Done:**
- [ ] Profile page renders at /profile
- [ ] Shows current user's email (read-only), role (read-only), is_active (read-only)
- [ ] display_name field is editable
- [ ] Save calls PATCH /users/me
- [ ] Success refreshes AuthContext to update display name in TopBar
- [ ] Cancel button discards changes
- [ ] Form validates display_name is not empty

---

## Dependencies

**Upstream (already complete):**
- Backend: GET/POST/PATCH/DELETE /accounts (WU-ACCT-3) ✅
- Backend: GET/POST/PATCH /users, GET/PATCH /users/me (WU-USR-4) ✅
- Backend: GET /roles (WU-ROLE-4) ✅
- Frontend: AuthContext with hasPermission() (WU-AUTH-6) ✅
- Frontend: Axios interceptors (WU-AUTH-7) ✅

**Downstream (will use this work):**
- Contacts module (WU-CONT-4) - will populate AccountContactsTab
- Opportunities module (WU-OPP-4) - will populate AccountOpportunitiesTab

---

## Reference

- Mock: `specs/mocks/Accounts _ CRM.html` - accounts list table design
- Mock: `specs/mocks/User Management _ CRM.html` - users admin design
- Existing pattern: `frontend/src/pages/LoginPage.tsx` - form handling
- Existing pattern: `frontend/src/lib/api.ts` - API client
