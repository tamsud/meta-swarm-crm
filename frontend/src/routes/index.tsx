import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { ROUTES } from './config';
import { DashboardPage } from '../pages/DashboardPage';
import { AccountsPage } from '../pages/AccountsPage';
import { ContactsPage } from '../pages/ContactsPage';
import { LeadsPage } from '../pages/LeadsPage';
import { PipelinePage } from '../pages/PipelinePage';
import { ActivitiesPage } from '../pages/ActivitiesPage';
import { UsersPage } from '../pages/admin/UsersPage';
import { MockEmailPage } from '../pages/admin/MockEmailPage';
import { SeedManagerPage } from '../pages/admin/SeedManagerPage';
import { LoginPage } from '../pages/LoginPage';

const router = createBrowserRouter([
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
