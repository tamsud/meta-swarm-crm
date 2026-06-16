import { useEffect } from 'react';

export function UsersPage() {
  useEffect(() => {
    document.title = 'User Management | CRM';
  }, []);

  return (
    <div className="p-4 space-y-3">
      <div className="px-1 pb-1">
        <h1 className="text-base font-semibold text-slate-900 tracking-tight">User Management</h1>
      </div>
      <div className="bg-white rounded-xl shadow-card border border-slate-100 p-4">
        <p className="text-slate-500">User management coming soon.</p>
      </div>
    </div>
  );
}
