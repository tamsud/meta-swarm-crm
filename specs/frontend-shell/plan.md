# Frontend Shell Module Plan

## Architecture Overview

The Frontend Shell establishes the visual and routing foundation that all other frontend modules build upon. It follows React patterns consistent with the existing codebase structure in `frontend/src/`.

```
┌─────────────────────────────────────────────────────────────┐
│                         App.tsx                             │
│  (QueryClientProvider, Routes, ReactQueryDevtools)          │
└───────────────────────────┬─────────────────────────────────┘
                            │
         ┌──────────────────┴──────────────────┐
         │           React Router               │
         │        createBrowserRouter           │
         └──────────────────┬──────────────────┘
                            │
         ┌──────────────────┴──────────────────┐
         │                                      │
    ┌────▼────┐                          ┌─────▼─────┐
    │ Login   │                          │ AppShell  │
    │ Layout  │                          │ Layout    │
    │(no nav) │                          │(sidebar)  │
    └────┬────┘                          └─────┬─────┘
         │                                     │
    ┌────▼────┐              ┌─────────────────┼───────────────┐
    │LoginPage│              │                 │               │
    └─────────┘         ┌────▼────┐      ┌─────▼─────┐   ┌────▼────┐
                        │Dashboard│      │ CRM Pages │   │ Admin   │
                        │  Page   │      │(Acc,Con,  │   │ Pages   │
                        └─────────┘      │Lead,Opp,  │   │(Users,  │
                                         │Activity)  │   │Email,   │
                                         └───────────┘   │Seed)    │
                                                         └─────────┘
```

## Components & Responsibilities

### Layout Components

| Component | Location | Responsibility |
|-----------|----------|----------------|
| `AppShell` | `components/layout/AppShell.tsx` | Main layout wrapper with sidebar + top bar + content area |
| `Sidebar` | `components/layout/Sidebar.tsx` | Navigation menu with main and admin sections |
| `TopBar` | `components/layout/TopBar.tsx` | Header with mobile menu toggle and user dropdown |
| `NavItem` | `components/layout/NavItem.tsx` | Reusable navigation link with icon and active state |

### Page Components

| Component | Location | Route |
|-----------|----------|-------|
| `DashboardPage` | `pages/DashboardPage.tsx` | `/` |
| `AccountsPage` | `pages/AccountsPage.tsx` | `/accounts` |
| `ContactsPage` | `pages/ContactsPage.tsx` | `/contacts` |
| `LeadsPage` | `pages/LeadsPage.tsx` | `/leads` |
| `PipelinePage` | `pages/PipelinePage.tsx` | `/opportunities` |
| `ActivitiesPage` | `pages/ActivitiesPage.tsx` | `/activities` |
| `UsersPage` | `pages/admin/UsersPage.tsx` | `/admin/users` |
| `MockEmailPage` | `pages/admin/MockEmailPage.tsx` | `/admin/mock-email` |
| `SeedManagerPage` | `pages/admin/SeedManagerPage.tsx` | `/admin/seed` |
| `LoginPage` | `pages/LoginPage.tsx` | `/login` |

### Routing Configuration

| File | Responsibility |
|------|----------------|
| `routes/index.tsx` | Export `<Routes />` component with all route definitions |
| `routes/config.ts` | Route path constants and navigation config array |

## Data Flow

### Navigation State

```
User clicks nav item
       │
       ▼
React Router updates URL
       │
       ▼
NavItem reads location.pathname via useLocation()
       │
       ▼
Matching NavItem renders with active styling
       │
       ▼
Browser title updated via useEffect in page component
```

### Sidebar Collapse State

```
User clicks collapse button
       │
       ▼
Local state toggles in Sidebar component
       │
       ▼
Conditional classNames applied:
  - w-60 (expanded) → w-[68px] (collapsed)
  - Label visibility toggled
  - Chevron icon rotates
```

### Mobile Menu State

```
User clicks mobile menu button (TopBar)
       │
       ▼
State passed up to AppShell or managed via context
       │
       ▼
Sidebar rendered as overlay on mobile
       │
       ▼
Click outside or nav item closes overlay
```

## Integration Points

### With Authentication Module (Future)

- `TopBar` user menu will show real user email from `AuthContext`
- Routes will be wrapped with `ProtectedRoute` component
- Logout action will be added to user dropdown
- Role-based nav item visibility (admin section hidden for non-admins)

### With CRM Modules (Future)

Each CRM module will:
1. Replace placeholder page with real implementation
2. Use the same `AppShell` layout
3. Follow the established styling patterns

### With Project Setup Module

Consumes:
- React 18 + TypeScript + Vite
- TailwindCSS configuration
- React Router v6 with `createBrowserRouter`
- Lucide React for icons

## File Structure

```
frontend/src/
├── components/
│   └── layout/
│       ├── AppShell.tsx       # Main layout wrapper
│       ├── Sidebar.tsx        # Navigation sidebar
│       ├── TopBar.tsx         # Header bar
│       └── NavItem.tsx        # Navigation link component
├── pages/
│   ├── DashboardPage.tsx
│   ├── AccountsPage.tsx
│   ├── ContactsPage.tsx
│   ├── LeadsPage.tsx
│   ├── PipelinePage.tsx
│   ├── ActivitiesPage.tsx
│   ├── LoginPage.tsx
│   └── admin/
│       ├── UsersPage.tsx
│       ├── MockEmailPage.tsx
│       └── SeedManagerPage.tsx
└── routes/
    ├── index.tsx              # Router definition
    └── config.ts              # Route constants and nav config
```

## Architectural Decisions

### Decision 1: Layout via Route Nesting
**Choice**: Use React Router's nested routes with layout components
**Rationale**: Login page needs different layout (no sidebar). Nested routes let us wrap authenticated pages in AppShell while keeping LoginPage standalone.
**Implementation**: 
```tsx
<Route element={<AppShell />}>
  <Route path="/" element={<DashboardPage />} />
  {/* ... other pages */}
</Route>
<Route path="/login" element={<LoginPage />} />
```

### Decision 2: Local State for Sidebar Collapse
**Choice**: Manage collapsed state in Sidebar component with useState
**Rationale**: No need for global state — sidebar collapse is a UI-only concern. If persistence is needed later, can lift to localStorage.
**Trade-off**: Collapse state resets on navigation. Acceptable for shell-only scope.

### Decision 3: Lucide React for Icons
**Choice**: Use lucide-react (already in project dependencies)
**Rationale**: Consistent icon library with TypeScript support. Icons referenced in mocks are Lucide icons.
**Implementation**: Import individual icons: `import { LayoutDashboard, Building2 } from 'lucide-react'`

### Decision 4: Navigation Config Array
**Choice**: Define navigation items in config file as array of objects
**Rationale**: Enables programmatic rendering, easy reordering, future permission filtering.
**Implementation**:
```tsx
export const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  // ...
];
```

### Decision 5: Placeholder Content Pattern
**Choice**: Each placeholder page shows page title + "Coming soon" message
**Rationale**: Provides clear indication that navigation works while signaling unimplemented state. Easy to replace with real implementation.

## Styling Patterns

### Tailwind Classes (from mocks)

**Sidebar**:
```
bg-indigo-900 px-3 py-4 w-60
```

**Active nav item**:
```
bg-indigo-50 text-indigo-700 rounded-lg px-3 py-2
```

**Inactive nav item**:
```
text-indigo-100/80 hover:bg-indigo-700 hover:text-white rounded-lg px-3 py-2
```

**Top bar**:
```
h-12 bg-white border-b border-slate-100 shadow-xs
```

**Page content**:
```
p-4 space-y-3
```

### Responsive Breakpoints

| Breakpoint | Behavior |
|------------|----------|
| < md (768px) | Sidebar hidden, mobile menu visible, overlay navigation |
| ≥ md | Sidebar visible (expanded or collapsed), no mobile menu |

## Testing Strategy (Deferred)

Unit tests for:
- NavItem active state logic
- Route matching

Integration tests for:
- Navigation between pages
- Sidebar collapse behavior
- Mobile responsiveness

Visual tests for:
- Layout matching mocks

Note: Test implementation deferred until CRM module implementation begins per CLAUDE.md instructions.

## Dependencies

### NPM Packages (already installed via Project Setup)

- `react` ^19
- `react-dom` ^19
- `react-router-dom` ^7
- `tailwindcss` ^4

### New Dependencies Required

The following packages must be installed as part of this module:

| Package | Version | Purpose |
|---------|---------|---------|
| `lucide-react` | ^0.511 | Icon library for navigation icons |
| `clsx` | ^2.1 | Utility for conditional class merging |

Install command: `cd frontend && npm install lucide-react clsx`
