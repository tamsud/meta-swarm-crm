import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { User, Loader2, Mail, Shield, CheckCircle } from 'lucide-react';
import { updateCurrentUser } from './api';
import type { UserUpdate } from './types';
import { useAuth } from '../../context/useAuth';

export function ProfilePage() {
  const { user, role } = useAuth();
  const queryClient = useQueryClient();

  const [displayName, setDisplayName] = useState(user?.display_name || '');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    document.title = 'Profile | CRM';
  }, []);

  useEffect(() => {
    if (user) {
      setDisplayName(user.display_name || '');
    }
  }, [user]);

  const updateMutation = useMutation({
    mutationFn: (data: UserUpdate) => updateCurrentUser(data),
    onSuccess: async () => {
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      setSuccess(true);
      setError(null);
      setTimeout(() => setSuccess(false), 3000);
    },
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { error?: { message?: string } } } };
      setError(axiosError.response?.data?.error?.message || 'Failed to update profile');
      setSuccess(false);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    if (!displayName.trim()) {
      setError('Display name cannot be empty');
      return;
    }

    updateMutation.mutate({ display_name: displayName.trim() });
  };

  const handleCancel = () => {
    setDisplayName(user?.display_name || '');
    setError(null);
    setSuccess(false);
  };

  const hasChanges = displayName !== (user?.display_name || '');

  if (!user) {
    return (
      <div className="p-4">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-indigo-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      <div className="px-1 pb-1">
        <h1 className="text-base font-semibold text-slate-900 tracking-tight">Profile</h1>
      </div>

      <div className="max-w-xl">
        <div className="bg-white rounded-xl shadow-card border border-slate-100 overflow-hidden">
          {/* Profile Header */}
          <div className="p-6 border-b border-slate-100 flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-indigo-600 flex items-center justify-center text-white text-2xl font-semibold">
              {(user.display_name || user.email)[0].toUpperCase()}
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">
                {user.display_name || user.email}
              </h2>
              <p className="text-sm text-slate-500">{role?.name || 'User'}</p>
            </div>
          </div>

          {/* Profile Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            {success && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <p className="text-sm text-green-600">Profile updated successfully</p>
              </div>
            )}

            {/* Read-only fields */}
            <div className="space-y-3">
              <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                <Mail className="h-4 w-4 text-slate-500" />
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wider">Email</p>
                  <p className="text-sm text-slate-900">{user.email}</p>
                </div>
              </div>

              <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                <Shield className="h-4 w-4 text-slate-500" />
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wider">Role</p>
                  <p className="text-sm text-slate-900">{role?.name || 'User'}</p>
                </div>
              </div>

              <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                <User className="h-4 w-4 text-slate-500" />
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wider">Status</p>
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                      user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
            </div>

            {/* Editable field */}
            <div className="pt-2">
              <label htmlFor="display_name" className="block text-sm font-medium text-slate-700 mb-1">
                Display Name
              </label>
              <input
                id="display_name"
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Your display name"
              />
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={handleCancel}
                disabled={!hasChanges || updateMutation.isPending}
                className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!hasChanges || updateMutation.isPending}
                className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {updateMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                Save Changes
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
