import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { X, Loader2 } from 'lucide-react';
import { createAccount, updateAccount } from './api';
import type { Account, AccountCreate, AccountUpdate } from './types';

interface AccountFormProps {
  account?: Account | null;
  onClose: () => void;
  onSuccess: () => void;
}

export function AccountForm({ account, onClose, onSuccess }: AccountFormProps) {
  const isEdit = !!account;

  const [formData, setFormData] = useState({
    name: account?.name || '',
    industry: account?.industry || '',
    website: account?.website || '',
    phone: account?.phone || '',
    address: account?.address || '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const createMutation = useMutation({
    mutationFn: (data: AccountCreate) => createAccount(data),
    onSuccess: () => onSuccess(),
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { error?: { message?: string } } } };
      setErrors({ submit: axiosError.response?.data?.error?.message || 'Failed to create account' });
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: AccountUpdate) => updateAccount(account!.id, data),
    onSuccess: () => onSuccess(),
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { error?: { message?: string } } } };
      setErrors({ submit: axiosError.response?.data?.error?.message || 'Failed to update account' });
    },
  });

  const isPending = createMutation.isPending || updateMutation.isPending;

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    const data = {
      name: formData.name.trim(),
      industry: formData.industry.trim() || undefined,
      website: formData.website.trim() || undefined,
      phone: formData.phone.trim() || undefined,
      address: formData.address.trim() || undefined,
    };

    if (isEdit) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data as AccountCreate);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
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
            {isEdit ? 'Edit Account' : 'New Account'}
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
            <label htmlFor="name" className="block text-sm font-medium text-slate-700 mb-1">
              Name <span className="text-red-500">*</span>
            </label>
            <input
              id="name"
              name="name"
              type="text"
              value={formData.name}
              onChange={handleChange}
              className={`w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                errors.name ? 'border-red-300' : 'border-slate-300'
              }`}
              placeholder="Account name"
            />
            {errors.name && <p className="mt-1 text-xs text-red-500">{errors.name}</p>}
          </div>

          <div>
            <label htmlFor="industry" className="block text-sm font-medium text-slate-700 mb-1">
              Industry
            </label>
            <input
              id="industry"
              name="industry"
              type="text"
              value={formData.industry}
              onChange={handleChange}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="e.g., Technology, Healthcare, Finance"
            />
          </div>

          <div>
            <label htmlFor="website" className="block text-sm font-medium text-slate-700 mb-1">
              Website
            </label>
            <input
              id="website"
              name="website"
              type="url"
              value={formData.website}
              onChange={handleChange}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="https://example.com"
            />
          </div>

          <div>
            <label htmlFor="phone" className="block text-sm font-medium text-slate-700 mb-1">
              Phone
            </label>
            <input
              id="phone"
              name="phone"
              type="tel"
              value={formData.phone}
              onChange={handleChange}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="+1 (555) 000-0000"
            />
          </div>

          <div>
            <label htmlFor="address" className="block text-sm font-medium text-slate-700 mb-1">
              Address
            </label>
            <textarea
              id="address"
              name="address"
              rows={2}
              value={formData.address}
              onChange={handleChange}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
              placeholder="Full address"
            />
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
              {isEdit ? 'Save Changes' : 'Create Account'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
