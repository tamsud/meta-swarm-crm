# Frontend Shell Work Units

## Overview

This document decomposes the Frontend Shell module into work units for orchestrated execution. Each work unit has clear DoD (Definition of Done) items, file scope, and dependencies.

## Task-to-Work-Unit Mapping

| Task ID | Description | Work Units |
|---------|-------------|------------|
| T-SHELL-0 | Install required dependencies | WU-SHELL-0 |
| T-SHELL-1 | Route configuration and constants | WU-SHELL-1 |
| T-SHELL-2 | Layout components (AppShell, Sidebar, TopBar) | WU-SHELL-2, WU-SHELL-3, WU-SHELL-4 |
| T-SHELL-3 | Navigation items component | WU-SHELL-5 |
| T-SHELL-4 | Placeholder pages | WU-SHELL-6 |
| T-SHELL-5 | Login page | WU-SHELL-7 |
| T-SHELL-6 | Integration and verification | WU-SHELL-8 |

---

## WU-SHELL-0: Install Dependencies

**Description**: Install required npm packages for the frontend shell

### Definition of Done

- [ ] `lucide-react` package installed: `npm ls lucide-react` shows version ^0.511
- [ ] `clsx` package installed: `npm ls clsx` shows version ^2.1
- [ ] No npm audit high/critical vulnerabilities introduced
- [ ] `npm run build` still succeeds after installation

### File Scope

```
frontend/
├── package.json       # UPDATE: new dependencies added
├── package-lock.json  # UPDATE: lockfile updated
```

### Dependencies

- None (first work unit)

### Implementation Notes

```bash
cd frontend && npm install lucide-react clsx
```

---

## WU-SHELL-1: Route Configuration

**Description**: Define route paths and navigation configuration array

### Definition of Done

- [ ] `frontend/src/routes/config.ts` exports `ROUTES` object with all path constants
- [ ] `frontend/src/routes/config.ts` exports `NAV_ITEMS` array for main navigation
- [ ] `frontend/src/routes/config.ts` exports `ADMIN_NAV_ITEMS` array for admin section
- [ ] Each nav item has: `path`, `label`, `icon` (Lucide component reference)
- [ ] TypeScript types defined for NavItem interface
- [ ] No TypeScript errors: `npx tsc --noEmit` passes

### File Scope

```
frontend/src/routes/
├── config.ts      # CREATE: Route constants and nav config
```

### Dependencies

- WU-SHELL-0 (dependencies installed)

### Implementation Notes

```typescript
// Route paths
export const ROUTES = {
  DASHBOARD: '/',
  ACCOUNTS: '/accounts',
  CONTACTS: '/contacts',
  LEADS: '/leads',
  OPPORTUNITIES: '/opportunities',
  ACTIVITIES: '/activities',
  ADMIN_USERS: '/admin/users',
  ADMIN_MOCK_EMAIL: '/admin/mock-email',
  ADMIN_SEED: '/admin/seed',
  LOGIN: '/login',
} as const;

// Nav item type
export interface NavItemConfig {
  path: string;
  label: string;
  icon: LucideIcon;
}
```

---

## WU-SHELL-2: AppShell Layout Component

**Description**: Main layout wrapper with sidebar slot, top bar, and content outlet

### Definition of Done

- [ ] `frontend/src/components/layout/AppShell.tsx` created
- [ ] Component renders: Sidebar | (TopBar + main content) layout
- [ ] Uses `flex h-screen` for full viewport height
- [ ] Main content area has `flex-1 overflow-y-auto`
- [ ] Uses React Router `<Outlet />` for nested page content
- [ ] No TypeScript errors

### File Scope

```
frontend/src/components/layout/
├── AppShell.tsx   # UPDATE: Main layout wrapper (file exists, needs full implementation)
```

### Dependencies

- WU-SHELL-3 (Sidebar component)
- WU-SHELL-4 (TopBar component)

### Implementation Notes

```tsx
export function AppShell() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  return (
    <div className="flex h-screen bg-surface-base relative">
      <Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar onMobileMenuClick={() => setMobileMenuOpen(!mobileMenuOpen)} />
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
```

---

## WU-SHELL-3: Sidebar Component

**Description**: Navigation sidebar with brand, main nav, admin section, and collapse toggle

### Definition of Done

- [ ] `frontend/src/components/layout/Sidebar.tsx` created
- [ ] Brand area shows "Sales CRM" with bar chart SVG icon
- [ ] Renders main nav items from `NAV_ITEMS` config
- [ ] Renders divider and "ADMIN" label
- [ ] Renders admin nav items from `ADMIN_NAV_ITEMS` config
- [ ] Collapse toggle button positioned absolute -right-3 top-6
- [ ] Collapsed state shows icons only (w-60 → w-[68px])
- [ ] Styling matches mock: bg-indigo-900, px-3 py-4
- [ ] Hidden on mobile (< md breakpoint)
- [ ] No TypeScript errors

### File Scope

```
frontend/src/components/layout/
├── Sidebar.tsx    # CREATE: Navigation sidebar
```

### Dependencies

- WU-SHELL-1 (route config)
- WU-SHELL-5 (NavItem component)

### Implementation Notes

- Use `transition-all duration-200` for collapse animation
- ChevronLeft icon rotates 180deg when collapsed
- Conditional className: `collapsed ? 'w-[68px]' : 'w-60'`

---

## WU-SHELL-4: TopBar Component

**Description**: Header bar with mobile menu toggle and user dropdown

### Definition of Done

- [ ] `frontend/src/components/layout/TopBar.tsx` created
- [ ] Height: h-12, background: bg-white border-b border-slate-100 shadow-xs
- [ ] Mobile menu button visible only below md breakpoint
- [ ] User area on right: avatar circle (bg-indigo-600, white initial), email text, chevron
- [ ] Email hidden on mobile (sm:block)
- [ ] Avatar shows first letter of hardcoded email "admin@crm.local"
- [ ] No TypeScript errors

### File Scope

```
frontend/src/components/layout/
├── TopBar.tsx     # CREATE: Header bar
```

### Dependencies

- None (can be implemented independently)

### Implementation Notes

```tsx
// Hardcoded user for shell phase - replaced by AuthContext later
const user = { email: 'admin@crm.local' };
const initial = user.email.charAt(0).toUpperCase();
```

---

## WU-SHELL-5: NavItem Component

**Description**: Reusable navigation link with icon, label, and active state

### Definition of Done

- [ ] `frontend/src/components/layout/NavItem.tsx` created
- [ ] Props: `path`, `label`, `icon`, `collapsed` (optional)
- [ ] Uses `useLocation()` to determine active state
- [ ] Active styling: `bg-indigo-50 text-indigo-700`
- [ ] Inactive styling: `text-indigo-100/80 hover:bg-indigo-700 hover:text-white`
- [ ] Icon: h-4 w-4, 3px gap from label
- [ ] Sets `aria-current="page"` when active
- [ ] Label hidden when `collapsed` is true
- [ ] No TypeScript errors

### File Scope

```
frontend/src/components/layout/
├── NavItem.tsx    # CREATE: Navigation link component
```

### Dependencies

- WU-SHELL-1 (imports from config)

### Implementation Notes

```tsx
interface NavItemProps {
  path: string;
  label: string;
  icon: LucideIcon;
  collapsed?: boolean;
}

export function NavItem({ path, label, icon: Icon, collapsed }: NavItemProps) {
  const location = useLocation();
  const isActive = location.pathname === path;
  
  return (
    <Link
      to={path}
      aria-current={isActive ? 'page' : undefined}
      className={cn(
        'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
        isActive
          ? 'bg-indigo-50 text-indigo-700'
          : 'text-indigo-100/80 hover:bg-indigo-700 hover:text-white'
      )}
    >
      <Icon className="h-4 w-4 flex-shrink-0" />
      {!collapsed && <span>{label}</span>}
    </Link>
  );
}
```

---

## WU-SHELL-6: Placeholder Pages

**Description**: Create placeholder page components for all routes

### Definition of Done

- [ ] `DashboardPage.tsx` created with title "Dashboard"
- [ ] `AccountsPage.tsx` created with title "Accounts"
- [ ] `ContactsPage.tsx` created with title "Contacts"
- [ ] `LeadsPage.tsx` created with title "Leads"
- [ ] `PipelinePage.tsx` created with title "Opportunities" (Pipeline in nav)
- [ ] `ActivitiesPage.tsx` created with title "Activities"
- [ ] `pages/admin/UsersPage.tsx` created with title "User Management"
- [ ] `pages/admin/MockEmailPage.tsx` created with title "Mail Inbox"
- [ ] `pages/admin/SeedManagerPage.tsx` created with title "Seed Manager"
- [ ] Each page updates document.title via useEffect
- [ ] Each page has consistent structure: wrapper div, h1 title, placeholder content
- [ ] Styling: p-4 space-y-3 for wrapper, text-base font-semibold for h1
- [ ] No TypeScript errors

### File Scope

```
frontend/src/pages/
├── DashboardPage.tsx      # CREATE
├── AccountsPage.tsx       # CREATE
├── ContactsPage.tsx       # CREATE
├── LeadsPage.tsx          # CREATE
├── PipelinePage.tsx       # CREATE
├── ActivitiesPage.tsx     # CREATE
└── admin/
    ├── UsersPage.tsx      # CREATE
    ├── MockEmailPage.tsx  # CREATE
    └── SeedManagerPage.tsx # CREATE
```

### Dependencies

- None (pages are leaf components)

### Implementation Notes

```tsx
export function AccountsPage() {
  useEffect(() => {
    document.title = 'Accounts | CRM';
  }, []);
  
  return (
    <div className="p-4 space-y-3">
      <div className="px-1 pb-1">
        <h1 className="text-base font-semibold text-slate-900 tracking-tight">Accounts</h1>
      </div>
      <div className="bg-white rounded-xl shadow-card border border-slate-100 p-4">
        <p className="text-slate-500">Account management coming soon.</p>
      </div>
    </div>
  );
}
```

---

## WU-SHELL-7: Login Page

**Description**: Login page with split layout (distinct from AppShell)

### Definition of Done

- [ ] `frontend/src/pages/LoginPage.tsx` created
- [ ] Split layout: left indigo panel, right white panel
- [ ] Left panel: Sales CRM branding, tagline, feature bullets
- [ ] Right panel: Sign in form with email, password, submit button
- [ ] Demo accounts info displayed below form
- [ ] Form is non-functional (placeholder) — Auth module adds functionality
- [ ] No sidebar or top bar rendered (different from AppShell pages)
- [ ] Updates document.title to "Sign in | CRM"
- [ ] No TypeScript errors

### File Scope

```
frontend/src/pages/
├── LoginPage.tsx  # CREATE
```

### Dependencies

- None (standalone page)

### Implementation Notes

- Uses full viewport height layout
- Left panel: `bg-gradient-to-br from-indigo-900 to-indigo-800`
- Form fields are controlled inputs with local state
- Submit button disabled (no action) until Auth module

---

## WU-SHELL-8: Router Integration

**Description**: Wire up all routes in the router configuration

### Definition of Done

- [ ] `frontend/src/routes/index.tsx` updated with createBrowserRouter
- [ ] AppShell wraps all authenticated routes via layout route
- [ ] LoginPage rendered without AppShell wrapper
- [ ] All 10 routes render correct page components
- [ ] Navigation between all pages works correctly
- [ ] `npm run build` completes without errors
- [ ] `npm run dev` starts and app loads at localhost:5173
- [ ] Visual inspection: sidebar matches mock appearance
- [ ] Visual inspection: navigation highlights active item correctly
- [ ] Visual inspection: login page has split layout without sidebar

### File Scope

```
frontend/src/routes/
├── index.tsx      # UPDATE: Full router configuration (file exists, needs route definitions)
```

### Dependencies

- WU-SHELL-1 (route config)
- WU-SHELL-2 (AppShell)
- WU-SHELL-6 (all pages)
- WU-SHELL-7 (LoginPage)

### Implementation Notes

```tsx
export const router = createBrowserRouter([
  {
    element: <AppShell />,
    children: [
      { path: ROUTES.DASHBOARD, element: <DashboardPage /> },
      { path: ROUTES.ACCOUNTS, element: <AccountsPage /> },
      { path: ROUTES.CONTACTS, element: <ContactsPage /> },
      { path: ROUTES.LEADS, element: <LeadsPage /> },
      { path: ROUTES.OPPORTUNITIES, element: <PipelinePage /> },
      { path: ROUTES.ACTIVITIES, element: <ActivitiesPage /> },
      { path: ROUTES.ADMIN_USERS, element: <UsersPage /> },
      { path: ROUTES.ADMIN_MOCK_EMAIL, element: <MockEmailPage /> },
      { path: ROUTES.ADMIN_SEED, element: <SeedManagerPage /> },
    ],
  },
  { path: ROUTES.LOGIN, element: <LoginPage /> },
]);

export function Routes() {
  return <RouterProvider router={router} />;
}
```

---

## Dependency Graph

```
WU-SHELL-0 (Install Dependencies)
    │
    ▼
WU-SHELL-1 (Route Config)
    │
    ├──────────────────┐
    │                  │
    ▼                  ▼
WU-SHELL-5         WU-SHELL-4
(NavItem)          (TopBar)
    │                  │
    ▼                  │
WU-SHELL-3             │
(Sidebar)              │
    │                  │
    └────────┬─────────┘
             │
             ▼
        WU-SHELL-2
        (AppShell)
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
WU-SHELL-6        WU-SHELL-7
(Placeholders)    (LoginPage)
    │                 │
    └────────┬────────┘
             │
             ▼
        WU-SHELL-8
        (Router Integration)
```

## Execution Order

1. **WU-SHELL-0**: Install dependencies (no deps)
2. **WU-SHELL-1**: Route configuration (depends on WU-SHELL-0)
3. **WU-SHELL-4**: TopBar (depends on WU-SHELL-0)
4. **WU-SHELL-5**: NavItem (depends on WU-SHELL-0, WU-SHELL-1)
5. **WU-SHELL-3**: Sidebar (depends on WU-SHELL-1, WU-SHELL-5)
6. **WU-SHELL-2**: AppShell (depends on WU-SHELL-3, WU-SHELL-4)
7. **WU-SHELL-6**: Placeholder pages (depends on WU-SHELL-0, can parallel with 3-6)
8. **WU-SHELL-7**: LoginPage (depends on WU-SHELL-0, can parallel with 3-7)
9. **WU-SHELL-8**: Router integration (depends on all above)

## Human Checkpoints

- **After WU-SHELL-5**: Review NavItem component styling matches mocks
- **After WU-SHELL-8**: Full visual review of navigation and pages before marking complete

## Verification Commands

```bash
# TypeScript check
cd frontend && npx tsc --noEmit

# Build
cd frontend && npm run build

# Dev server
cd frontend && npm run dev

# Lint
cd frontend && npm run lint
```
