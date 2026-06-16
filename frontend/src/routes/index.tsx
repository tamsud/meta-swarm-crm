import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';

function HomePage() {
  return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">CRM Application</h1>
        <p className="text-lg text-gray-600">
          Frontend scaffold initialized
        </p>
      </div>
    </div>
  );
}

const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <AppShell>
        <HomePage />
      </AppShell>
    ),
  },
]);

export function Routes() {
  return <RouterProvider router={router} />;
}
