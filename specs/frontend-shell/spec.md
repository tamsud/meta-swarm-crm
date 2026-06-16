# Frontend Shell Module Specification

## Module Overview

The Frontend Shell module establishes the core navigation structure, layout components, and routing foundation for the CRM application. It provides a consistent visual framework matching the reference mocks in `specs/mocks/` — an indigo sidebar with navigation, a top bar with user menu, and page content areas with placeholder pages for each route.

**Scope**: Shell layout, navigation, routing, and placeholder pages only. Actual CRUD functionality, API integration, and complex page logic belong to their respective CRM modules (Accounts, Contacts, Leads, Opportunities, Activities, Users).

## Dependencies

| Module | Relationship |
|--------|--------------|
| [Project Setup](../project-setup/spec.md) | Required — provides React 18, Vite, TypeScript, TailwindCSS, React Router, React Query |
| [Foundation Enhancements](../foundation-enhancements/spec.md) | Required — provides mocks organization and Docker dev setup |
| [Authentication](../authentication/spec.md) | Deferred — shell renders without auth; route protection added by Auth module |

## User Stories

### US-SHELL-1: Sales Rep Navigates Between CRM Pages
**As a** sales rep,
**I want** a sidebar navigation to move between Dashboard, Accounts, Contacts, Leads, Pipeline, and Activities,
**So that** I can quickly access different parts of the CRM.

**Acceptance Criteria**:
- Sidebar displays all 6 main navigation items with icons
- Active route is highlighted with indigo-50 background and indigo-700 text
- Inactive items have indigo-100/80 text, hover shows indigo-700 background
- Clicking a nav item navigates to the corresponding route

### US-SHELL-2: Admin Accesses Admin Section
**As an** admin user,
**I want** a separated "Admin" section in the sidebar,
**So that** I can access Users, Mock Email, and Seed Manager pages.

**Acceptance Criteria**:
- Divider separates main nav from admin section
- "ADMIN" label in indigo-400 uppercase text
- Admin nav items: Users, Mock Email, Seed Manager
- Same active/inactive styling as main nav items

### US-SHELL-3: User Identifies Current Location
**As a** user,
**I want** the browser title and sidebar to reflect the current page,
**So that** I know where I am in the application.

**Acceptance Criteria**:
- Document title updates to "{Page Name} | CRM" format
- Active sidebar item matches current route

### US-SHELL-4: User Views Their Identity
**As a** logged-in user,
**I want** to see my email/avatar in the top bar,
**So that** I know which account I'm using.

**Acceptance Criteria**:
- Top bar shows avatar (first letter of email) and email address
- User dropdown menu shows with chevron icon (menu content deferred to Auth module)

### US-SHELL-5: User Accesses App on Mobile
**As a** mobile user,
**I want** responsive navigation that works on small screens,
**So that** I can use the CRM on my phone.

**Acceptance Criteria**:
- Sidebar collapses to hidden on mobile (md: breakpoint)
- Mobile menu button appears in top bar
- Sidebar collapse button toggles sidebar state

## Functional Requirements

### FR-SHELL-001: Application Shell Layout
The application shall provide a shell layout with:
- Fixed-width sidebar (w-60, 240px) on desktop
- Top bar header (h-12, 48px) with user menu
- Main content area that scrolls vertically
- Full viewport height layout (h-screen)

### FR-SHELL-002: Sidebar Navigation Structure
The sidebar shall include in order:
1. Logo/brand area: "Sales CRM" with bar chart icon
2. Main navigation items:
   - Dashboard (`/`) — LayoutDashboard icon
   - Accounts (`/accounts`) — Building2 icon
   - Contacts (`/contacts`) — Users icon
   - Leads (`/leads`) — Target icon
   - Pipeline (`/opportunities`) — TrendingUp icon
   - Activities (`/activities`) — Activity icon
3. Divider (border-t border-indigo-700)
4. "ADMIN" section label
5. Admin navigation items:
   - Users (`/admin/users`) — UserCog icon
   - Mock Email (`/admin/mock-email`) — Mail icon
   - Seed Manager (`/admin/seed`) — Database icon
6. Collapse toggle button (absolute positioned -right-3)

### FR-SHELL-003: Navigation Styling
The sidebar navigation shall follow this styling:
- Background: bg-indigo-900
- Active item: bg-indigo-50 text-indigo-700
- Inactive item: text-indigo-100/80
- Hover: bg-indigo-700 text-white
- Icons: h-4 w-4 (16px)
- Text: text-sm font-medium
- Padding: px-3 py-2
- Border radius: rounded-lg
- Gap between items: gap-1

### FR-SHELL-004: Top Bar Structure
The top bar shall include:
- Height: h-12 (48px)
- Background: bg-white with bottom border (border-slate-100)
- Mobile menu button (hidden md:visible inverse)
- User menu on right side with:
  - Avatar circle (w-8 h-8, bg-indigo-600, white initial)
  - Email text (hidden on mobile)
  - Chevron down icon

### FR-SHELL-005: Route Configuration
The router shall define these routes:
| Path | Component | Title |
|------|-----------|-------|
| `/` | DashboardPage | Dashboard |
| `/accounts` | AccountsPage | Accounts |
| `/contacts` | ContactsPage | Contacts |
| `/leads` | LeadsPage | Leads |
| `/opportunities` | PipelinePage | Opportunities |
| `/activities` | ActivitiesPage | Activities |
| `/admin/users` | UsersPage | User Management |
| `/admin/mock-email` | MockEmailPage | Mail Inbox |
| `/admin/seed` | SeedManagerPage | Seed Manager |
| `/login` | LoginPage | Sign in |

### FR-SHELL-006: Placeholder Pages
Each placeholder page shall display:
- Page title matching the route (h1, text-base font-semibold)
- "Coming soon" or equivalent placeholder content
- Consistent padding (p-4) matching mock layout

### FR-SHELL-007: Login Page Layout
The login page shall have a distinct layout:
- No sidebar or top bar
- Split screen: left indigo branded, right white with form
- Login form with email, password, sign in button
- Demo accounts info displayed below form

### FR-SHELL-008: Sidebar Collapse
The sidebar shall support collapsing:
- Toggle button: absolute, -right-3, top-6
- Button style: rounded-full, bg-indigo-700, hover:bg-indigo-600
- Collapsed state: w-[68px] with icons only
- ChevronLeft icon, rotates when collapsed

### FR-SHELL-009: Responsive Behavior
The layout shall adapt to screen sizes:
- Desktop (md and above): Sidebar visible, no mobile menu
- Mobile (below md): Sidebar hidden, mobile menu button visible
- Mobile sidebar: Slides in as overlay when toggled

## Success Criteria

### SC-SHELL-001: Navigation Completeness
All 10 navigation items render with correct icons, labels, and routes. Active state correctly indicates current route.

### SC-SHELL-002: Visual Match
The shell layout matches the reference mocks in `specs/mocks/` for:
- Sidebar colors and spacing
- Top bar height and styling
- Navigation item appearance (active/inactive/hover)

### SC-SHELL-003: Route Functionality
All defined routes render without errors. Browser URL matches expected route paths. Document title updates appropriately.

### SC-SHELL-004: Responsive Behavior
On viewport < 768px, sidebar collapses and mobile menu appears. Navigation remains functional on mobile.

### SC-SHELL-005: TypeScript Compliance
All components pass TypeScript strict mode with no type errors.

### SC-SHELL-006: Build Success
`npm run build` completes without errors or warnings.

## Key Entities

This module does not define database entities. It consumes routing and layout concerns only.

## UI Reference

Visual designs are captured in `specs/mocks/`:
- `dashboards.png` — Dashboard with sidebar navigation
- `accounts.png` — Accounts list page
- `conatacts.png` — Contacts list page
- `pipeline.png` — Pipeline/Opportunities kanban
- `login.png` — Login page split layout
- `dashboard.html` — Full HTML reference for sidebar structure
- `Activities _ CRM.html` — Activities page structure
- `User Management _ CRM.html` — Users admin page
- `Seed Manager _ CRM.html` — Seed manager page
- `Leads _ CRM.html` — Leads table page

## Out of Scope

- Authentication/authorization logic (Auth module)
- API calls to backend (respective CRM modules)
- CRUD forms and modals (respective CRM modules)
- Real data fetching (respective CRM modules)
- Chart/graph components (Dashboard real implementation)
- Table sorting/filtering (respective CRM modules)
