# Frontend Shell Tasks

## Prerequisites

- **Project Setup** module complete (React 18, Vite, TypeScript, TailwindCSS, React Router configured)
- **Foundation Enhancements** module complete (mocks organized in `specs/mocks/`)

## Task Summary

| Task ID | Description | Priority | Est. Effort |
|---------|-------------|----------|-------------|
| T-SHELL-0 | Install required dependencies | 1 | 5 min |
| T-SHELL-1 | Route configuration and constants | 1 | 15 min |
| T-SHELL-2 | Layout components | 1 | 45 min |
| T-SHELL-3 | Navigation items component | 1 | 20 min |
| T-SHELL-4 | Placeholder pages | 2 | 30 min |
| T-SHELL-5 | Login page | 2 | 25 min |
| T-SHELL-6 | Integration and verification | 1 | 20 min |

---

## T-SHELL-0: Install Required Dependencies

**Description**: Install npm packages needed for the frontend shell module.

**Acceptance Criteria**:
- [ ] `lucide-react` package installed (^0.511)
- [ ] `clsx` package installed (^2.1)
- [ ] No npm audit high/critical vulnerabilities
- [ ] Build still succeeds

**Command**:
```bash
cd frontend && npm install lucide-react clsx
```

---

## T-SHELL-1: Route Configuration and Constants

**Description**: Define route path constants and navigation configuration arrays for programmatic rendering.

**Acceptance Criteria**:
- [ ] `ROUTES` object with all 10 route paths exported
- [ ] `NAV_ITEMS` array with main navigation (6 items)
- [ ] `ADMIN_NAV_ITEMS` array with admin navigation (3 items)
- [ ] TypeScript `NavItemConfig` interface defined
- [ ] No TypeScript errors (`npx tsc --noEmit` passes)

**Files**: `frontend/src/routes/config.ts`

---

## T-SHELL-2: Layout Components

**Description**: Create the main application layout wrapper with sidebar and top bar.

**Acceptance Criteria**:
- [ ] `AppShell` component with flex layout (sidebar + main area)
- [ ] `Sidebar` component with brand, nav items, admin section, collapse toggle
- [ ] `TopBar` component with mobile menu button and user dropdown
- [ ] Sidebar collapse toggles between w-60 and w-[68px]
- [ ] Mobile responsive: sidebar hidden below md breakpoint
- [ ] Styling matches mocks (bg-indigo-900 sidebar, h-12 top bar)

**Files**: 
- `frontend/src/components/layout/AppShell.tsx` (UPDATE)
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/layout/TopBar.tsx`

**Dependencies**: T-SHELL-1, T-SHELL-3

---

## T-SHELL-3: Navigation Items Component

**Description**: Create reusable navigation link component with active state detection.

**Acceptance Criteria**:
- [ ] `NavItem` component with icon, label, collapsed support
- [ ] Uses `useLocation()` to determine active state
- [ ] Active styling: `bg-indigo-50 text-indigo-700`
- [ ] Inactive styling: `text-indigo-100/80 hover:bg-indigo-700`
- [ ] Sets `aria-current="page"` when active
- [ ] Icon size: h-4 w-4

**Files**: `frontend/src/components/layout/NavItem.tsx`

**Dependencies**: T-SHELL-1

---

## T-SHELL-4: Placeholder Pages

**Description**: Create placeholder page components for all routes (non-login).

**Acceptance Criteria**:
- [ ] 9 placeholder pages created (Dashboard, Accounts, Contacts, Leads, Pipeline, Activities, Users, MockEmail, SeedManager)
- [ ] Each page updates document.title
- [ ] Consistent structure: wrapper div, h1 title, placeholder content
- [ ] Styling: p-4 space-y-3, text-base font-semibold for h1

**Files**:
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/pages/AccountsPage.tsx`
- `frontend/src/pages/ContactsPage.tsx`
- `frontend/src/pages/LeadsPage.tsx`
- `frontend/src/pages/PipelinePage.tsx`
- `frontend/src/pages/ActivitiesPage.tsx`
- `frontend/src/pages/admin/UsersPage.tsx`
- `frontend/src/pages/admin/MockEmailPage.tsx`
- `frontend/src/pages/admin/SeedManagerPage.tsx`

---

## T-SHELL-5: Login Page

**Description**: Create login page with split-screen layout distinct from AppShell.

**Acceptance Criteria**:
- [ ] Split layout: left indigo branded panel, right white form panel
- [ ] Left panel: Sales CRM branding, tagline, feature bullets
- [ ] Right panel: Sign in form (email, password, submit)
- [ ] Demo accounts info displayed
- [ ] No sidebar/top bar (standalone page)
- [ ] Updates document.title to "Sign in | CRM"

**Files**: `frontend/src/pages/LoginPage.tsx`

---

## T-SHELL-6: Integration and Verification

**Description**: Wire up all routes and verify the complete frontend shell.

**Acceptance Criteria**:
- [ ] Router configuration with all 10 routes
- [ ] AppShell wraps authenticated routes via layout route
- [ ] LoginPage rendered without AppShell wrapper
- [ ] `npm run build` completes without errors
- [ ] `npm run dev` starts successfully
- [ ] Visual inspection: sidebar matches mocks
- [ ] Visual inspection: active nav item highlighted correctly
- [ ] Visual inspection: login page has split layout

**Files**: `frontend/src/routes/index.tsx` (UPDATE)

**Dependencies**: T-SHELL-0 through T-SHELL-5

---

## Sequencing

```
T-SHELL-0 (Install deps)
    │
    ▼
T-SHELL-1 (Route config)
    │
    ├──────────────────┐
    │                  │
    ▼                  ▼
T-SHELL-3          T-SHELL-4, T-SHELL-5
(NavItem)          (Pages - can parallel)
    │
    ▼
T-SHELL-2 (Layout components)
    │
    ▼
T-SHELL-6 (Integration)
```
