import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/useAuth';
import { ROUTES } from './config';

interface RequirePermissionProps {
  permission: string;
}

export function RequirePermission({ permission }: RequirePermissionProps) {
  const { isAuthenticated, hasPermission } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} state={{ from: location }} replace />;
  }

  if (!hasPermission(permission)) {
    // Render 403 Forbidden page
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-50">
        <div className="text-center">
          <h1 className="text-6xl font-bold text-slate-900">403</h1>
          <p className="text-xl text-slate-600 mt-4">Forbidden</p>
          <p className="text-slate-500 mt-2">
            You don't have permission to access this page.
          </p>
        </div>
      </div>
    );
  }

  return <Outlet />;
}
