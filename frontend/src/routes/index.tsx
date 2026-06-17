import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { RequireAuth } from './RequireAuth';
import { ROUTES } from './config';
import { DashboardPage } from '../pages/DashboardPage';
import { AccountsPage } from '../pages/AccountsPage';
import { AccountDetailPage } from '../features/accounts/AccountDetailPage';
import { ContactsPage } from '../pages/ContactsPage';
import { ContactDetailPage } from '../features/contacts/ContactDetailPage';
import { LeadsPage } from '../pages/LeadsPage';
import { LeadDetailPage } from '../features/leads/LeadDetailPage';
import { OpportunitiesPage } from '../features/opportunities/OpportunitiesPage';
import { OpportunityDetailPage } from '../features/opportunities/OpportunityDetailPage';
import { ActivitiesPage } from '../pages/ActivitiesPage';
import { UsersPage } from '../pages/admin/UsersPage';
import { MockEmailPage } from '../pages/admin/MockEmailPage';
import { SeedManagerPage } from '../pages/admin/SeedManagerPage';
import { ProfilePage } from '../features/users/ProfilePage';
import { LoginPage } from '../pages/LoginPage';

const router = createBrowserRouter([
  {
    element: <RequireAuth />,
    children: [
      {
        element: <AppShell />,
        children: [
          { path: ROUTES.DASHBOARD, element: <DashboardPage /> },
          { path: ROUTES.ACCOUNTS, element: <AccountsPage /> },
          { path: ROUTES.ACCOUNT_DETAIL, element: <AccountDetailPage /> },
          { path: ROUTES.CONTACTS, element: <ContactsPage /> },
          { path: ROUTES.CONTACT_DETAIL, element: <ContactDetailPage /> },
          { path: ROUTES.LEADS, element: <LeadsPage /> },
          { path: ROUTES.LEAD_DETAIL, element: <LeadDetailPage /> },
          { path: ROUTES.OPPORTUNITIES, element: <OpportunitiesPage /> },
          { path: ROUTES.OPPORTUNITY_DETAIL, element: <OpportunityDetailPage /> },
          { path: ROUTES.ACTIVITIES, element: <ActivitiesPage /> },
          { path: ROUTES.ADMIN_USERS, element: <UsersPage /> },
          { path: ROUTES.ADMIN_MOCK_EMAIL, element: <MockEmailPage /> },
          { path: ROUTES.ADMIN_SEED, element: <SeedManagerPage /> },
          { path: ROUTES.PROFILE, element: <ProfilePage /> },
        ],
      },
    ],
  },
  { path: ROUTES.LOGIN, element: <LoginPage /> },
]);

export function Routes() {
  return <RouterProvider router={router} />;
}
