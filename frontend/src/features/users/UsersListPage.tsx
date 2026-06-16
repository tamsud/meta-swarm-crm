import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Search, Loader2, UserCog, Pencil, Check, X } from 'lucide-react';
import { listUsers, listRoles, updateUser } from './api';
import type { User } from './types';
import { UserForm } from './UserForm';
import { useAuth } from '../../context/useAuth';

const DEFAULT_LIMIT = 20;

export function UsersListPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const { hasPermission } = useAuth();

  const search = searchParams.get('search') || '';
  const roleFilter = searchParams.get('role_id') ? parseInt(searchParams.get('role_id')!, 10) : undefined;
  const offset = parseInt(searchParams.get('offset') || '0', 10);
  const limit = parseInt(searchParams.get('limit') || String(DEFAULT_LIMIT), 10);

  const [searchInput, setSearchInput] = useState(search);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [deactivateConfirm, setDeactivateConfirm] = useState<User | null>(null);
  const [deactivateError, setDeactivateError] = useState<string | null>(null);

  const canManageUsers = hasPermission('users:manage');

  useEffect(() => {
    document.title = 'Users | CRM';
  }, []);

  const { data: usersData, isLoading, isError, error } = useQuery({
    queryKey: ['users', { search, role_id: roleFilter, offset, limit }],
    queryFn: () => listUsers({ search: search || undefined, role_id: roleFilter, offset, limit }),
    enabled: canManageUsers,
  });

  const { data: roles } = useQuery({
    queryKey: ['roles'],
    queryFn: listRoles,
    enabled: canManageUsers,
  });

  const toggleActiveMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: number; is_active: boolean }) =>
      updateUser(id, { is_active }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setDeactivateConfirm(null);
      setDeactivateError(null);
    },
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { error?: { code?: string; message?: string } } } };
      const errorData = axiosError.response?.data?.error;
      if (errorData?.code === 'LAST_ADMIN_LOCKOUT') {
        setDeactivateError('Cannot deactivate the last active admin user.');
      } else {
        setDeactivateError(errorData?.message || 'Failed to update user status');
      }
    },
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams(searchParams);
    if (searchInput.trim()) {
      params.set('search', searchInput.trim());
    } else {
      params.delete('search');
    }
    params.delete('offset');
    setSearchParams(params);
  };

  const handleRoleFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const params = new URLSearchParams(searchParams);
    if (e.target.value) {
      params.set('role_id', e.target.value);
    } else {
      params.delete('role_id');
    }
    params.delete('offset');
    setSearchParams(params);
  };

  const handleEdit = (user: User) => {
    setEditingUser(user);
    setIsFormOpen(true);
  };

  const handleFormClose = () => {
    setIsFormOpen(false);
    setEditingUser(null);
  };

  const handleFormSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['users'] });
    handleFormClose();
  };

  const handleToggleActive = (user: User) => {
    if (user.is_active) {
      setDeactivateError(null);
      setDeactivateConfirm(user);
    } else {
      toggleActiveMutation.mutate({ id: user.id, is_active: true });
    }
  };

  const handleDeactivateConfirm = () => {
    if (deactivateConfirm) {
      toggleActiveMutation.mutate({ id: deactivateConfirm.id, is_active: false });
    }
  };

  const getRoleName = (roleId: number): string => {
    const role = roles?.find((r) => r.id === roleId);
    return role?.name || `Role ${roleId}`;
  };

  if (!canManageUsers) {
    return (
      <div className="p-4">
        <div className="bg-white rounded-xl shadow-card border border-slate-100 p-8 text-center">
          <UserCog className="h-12 w-12 text-slate-300 mx-auto mb-3" />
          <h2 className="text-lg font-semibold text-slate-900 mb-2">Access Denied</h2>
          <p className="text-slate-500">You don't have permission to manage users.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-3">
      <div className="px-1 pb-1">
        <h1 className="text-base font-semibold text-slate-900 tracking-tight">Users</h1>
      </div>

      <div className="bg-white rounded-xl shadow-card border border-slate-100 overflow-hidden">
        {/* Search, Filter, and New button row */}
        <div className="p-4 border-b border-slate-100 flex flex-wrap items-center gap-3">
          <form onSubmit={handleSearch} className="flex-1 min-w-[200px] max-w-sm">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search users..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </form>

          <select
            value={roleFilter || ''}
            onChange={handleRoleFilterChange}
            className="px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          >
            <option value="">All Roles</option>
            {roles?.map((role) => (
              <option key={role.id} value={role.id}>
                {role.name}
              </option>
            ))}
          </select>

          <button
            onClick={() => setIsFormOpen(true)}
            className="inline-flex items-center gap-1 rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 active:bg-indigo-800 transition-colors shadow-xs"
          >
            <Plus className="h-4 w-4" />
            New User
          </button>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-indigo-600" />
            </div>
          ) : isError ? (
            <div className="flex items-center justify-center py-12 text-red-600">
              Error: {(error as Error).message}
            </div>
          ) : usersData?.data.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-500">
              <UserCog className="h-12 w-12 text-slate-300 mb-3" />
              <p className="text-sm font-medium">No users found</p>
              {search && <p className="text-xs mt-1">Try adjusting your search criteria</p>}
            </div>
          ) : (
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50">
                <tr className="border-b border-slate-100">
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Display Name
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-4 py-2.5 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {usersData?.data.map((user) => (
                  <tr key={user.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-medium text-slate-900">{user.email}</td>
                    <td className="px-4 py-3 text-slate-600">{user.display_name || '—'}</td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700">
                        {getRoleName(user.role_id)}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                          user.is_active
                            ? 'bg-green-50 text-green-700'
                            : 'bg-red-50 text-red-700'
                        }`}
                      >
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="inline-flex items-center gap-1">
                        <button
                          onClick={() => handleEdit(user)}
                          className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
                          title="Edit"
                        >
                          <Pencil className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleToggleActive(user)}
                          disabled={toggleActiveMutation.isPending}
                          className={`p-1.5 rounded-md transition-colors ${
                            user.is_active
                              ? 'text-slate-400 hover:text-red-600 hover:bg-red-50'
                              : 'text-slate-400 hover:text-green-600 hover:bg-green-50'
                          }`}
                          title={user.is_active ? 'Deactivate' : 'Activate'}
                        >
                          {user.is_active ? <X className="h-4 w-4" /> : <Check className="h-4 w-4" />}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* User Form Modal */}
      {isFormOpen && (
        <UserForm
          user={editingUser}
          roles={roles || []}
          onClose={handleFormClose}
          onSuccess={handleFormSuccess}
        />
      )}

      {/* Deactivate Confirmation Dialog */}
      {deactivateConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50" onClick={() => setDeactivateConfirm(null)} />
          <div className="relative bg-white rounded-xl shadow-lg p-6 max-w-sm w-full mx-4">
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Deactivate User</h3>
            <p className="text-slate-600 text-sm mb-4">
              Are you sure you want to deactivate "{deactivateConfirm.email}"? They will no longer be able to log in.
            </p>
            {deactivateError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{deactivateError}</p>
              </div>
            )}
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setDeactivateConfirm(null);
                  setDeactivateError(null);
                }}
                className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDeactivateConfirm}
                disabled={toggleActiveMutation.isPending}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {toggleActiveMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                Deactivate
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
