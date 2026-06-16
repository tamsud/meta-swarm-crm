import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { X, Loader2 } from 'lucide-react';
import { createUser, updateUser } from './api';
import type { User, UserCreate, UserUpdate, Role } from './types';

interface UserFormProps {
  user?: User | null;
  roles: Role[];
  onClose: () => void;
  onSuccess: () => void;
}

export function UserForm({ user, roles, onClose, onSuccess }: UserFormProps) {
  const isEdit = !!user;

  const [formData, setFormData] = useState({
    email: user?.email || '',
    password: '',
    display_name: user?.display_name || '',
    role_id: user?.role_id || (roles[0]?.id || 1),
    is_active: user?.is_active ?? true,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const createMutation = useMutation({
    mutationFn: (data: UserCreate) => createUser(data),
    onSuccess: () => onSuccess(),
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { error?: { message?: string; code?: string } } } };
      const errorData = axiosError.response?.data?.error;
      if (errorData?.code === 'EMAIL_ALREADY_EXISTS') {
        setErrors({ email: 'This email is already in use' });
      } else {
        setErrors({ submit: errorData?.message || 'Failed to create user' });
      }
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: UserUpdate) => updateUser(user!.id, data),
    onSuccess: () => onSuccess(),
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { error?: { message?: string; code?: string } } } };
      const errorData = axiosError.response?.data?.error;
      if (errorData?.code === 'EMAIL_ALREADY_EXISTS') {
        setErrors({ email: 'This email is already in use' });
      } else if (errorData?.code === 'LAST_ADMIN_LOCKOUT') {
        setErrors({ submit: 'Cannot change the last admin user\'s role or status' });
      } else {
        setErrors({ submit: errorData?.message || 'Failed to update user' });
      }
    },
  });

  const isPending = createMutation.isPending || updateMutation.isPending;

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    if (!isEdit && !formData.password) {
      newErrors.password = 'Password is required';
    } else if (!isEdit && formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    if (!formData.role_id) {
      newErrors.role_id = 'Role is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    if (isEdit) {
      const data: UserUpdate = {
        email: formData.email.trim(),
        display_name: formData.display_name.trim() || undefined,
        role_id: formData.role_id,
        is_active: formData.is_active,
      };
      updateMutation.mutate(data);
    } else {
      const data: UserCreate = {
        email: formData.email.trim(),
        password: formData.password,
        display_name: formData.display_name.trim() || undefined,
        role_id: formData.role_id,
        is_active: formData.is_active,
      };
      createMutation.mutate(data);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const newValue = type === 'checkbox' ? (e.target as HTMLInputElement).checked : value;
    setFormData((prev) => ({ ...prev, [name]: newValue }));
    if (errors[name]) {
      setErrors((prev) => {
        const { [name]: _, ...rest } = prev;
        return rest;
      });
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-lg w-full max-w-lg mx-4">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h2 className="text-lg font-semibold text-slate-900">
            {isEdit ? 'Edit User' : 'New User'}
          </h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {errors.submit && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{errors.submit}</p>
            </div>
          )}

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-1">
              Email <span className="text-red-500">*</span>
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              className={`w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                errors.email ? 'border-red-300' : 'border-slate-300'
              }`}
              placeholder="user@example.com"
            />
            {errors.email && <p className="mt-1 text-xs text-red-500">{errors.email}</p>}
          </div>

          {!isEdit && (
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-700 mb-1">
                Password <span className="text-red-500">*</span>
              </label>
              <input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                className={`w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                  errors.password ? 'border-red-300' : 'border-slate-300'
                }`}
                placeholder="••••••••"
              />
              {errors.password && <p className="mt-1 text-xs text-red-500">{errors.password}</p>}
            </div>
          )}

          <div>
            <label htmlFor="display_name" className="block text-sm font-medium text-slate-700 mb-1">
              Display Name
            </label>
            <input
              id="display_name"
              name="display_name"
              type="text"
              value={formData.display_name}
              onChange={handleChange}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="John Doe"
            />
          </div>

          <div>
            <label htmlFor="role_id" className="block text-sm font-medium text-slate-700 mb-1">
              Role <span className="text-red-500">*</span>
            </label>
            <select
              id="role_id"
              name="role_id"
              value={formData.role_id}
              onChange={handleChange}
              className={`w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                errors.role_id ? 'border-red-300' : 'border-slate-300'
              }`}
            >
              {roles.map((role) => (
                <option key={role.id} value={role.id}>
                  {role.name}
                </option>
              ))}
            </select>
            {errors.role_id && <p className="mt-1 text-xs text-red-500">{errors.role_id}</p>}
          </div>

          <div className="flex items-center gap-2">
            <input
              id="is_active"
              name="is_active"
              type="checkbox"
              checked={formData.is_active}
              onChange={handleChange}
              className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
            />
            <label htmlFor="is_active" className="text-sm font-medium text-slate-700">
              Active
            </label>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isPending}
              className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              {isEdit ? 'Save Changes' : 'Create User'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
