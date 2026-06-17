import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { X, Loader2 } from 'lucide-react';
import { createOpportunity, updateOpportunity } from './api';
import { listAccounts } from '../accounts/api';
import type { Opportunity, OpportunityCreate, OpportunityUpdate, OpportunityStage } from './types';
import { STAGE_ORDER, STAGE_LABELS } from './types';

interface OpportunityFormProps {
  opportunity?: Opportunity | null;
  defaultAccountId?: number;
  onClose: () => void;
  onSuccess: () => void;
}

export function OpportunityForm({
  opportunity,
  defaultAccountId,
  onClose,
  onSuccess,
}: OpportunityFormProps) {
  const isEdit = !!opportunity;

  const [formData, setFormData] = useState({
    title: opportunity?.title || '',
    account_id: opportunity?.account_id?.toString() || defaultAccountId?.toString() || '',
    contact_id: opportunity?.contact_id?.toString() || '',
    stage: (opportunity?.stage || 'prospecting') as OpportunityStage,
    value: opportunity?.value || '',
    probability: opportunity?.probability?.toString() || '',
    expected_close_date: opportunity?.expected_close_date || '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Fetch accounts for the dropdown
  const { data: accountsData } = useQuery({
    queryKey: ['accounts', { limit: 1000 }],
    queryFn: () => listAccounts({ limit: 1000 }),
  });

  const createMutation = useMutation({
    mutationFn: (data: OpportunityCreate) => createOpportunity(data),
    onSuccess: () => onSuccess(),
    onError: (err: unknown) => {
      const axiosError = err as {
        response?: { data?: { error?: { message?: string; details?: Array<{ msg: string }> } } };
      };
      const errorData = axiosError.response?.data?.error;
      if (errorData?.details?.length) {
        setErrors({ submit: errorData.details.map((d) => d.msg).join(', ') });
      } else {
        setErrors({ submit: errorData?.message || 'Failed to create opportunity' });
      }
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: OpportunityUpdate) => updateOpportunity(opportunity!.id, data),
    onSuccess: () => onSuccess(),
    onError: (err: unknown) => {
      const axiosError = err as {
        response?: { data?: { error?: { message?: string } } };
      };
      setErrors({
        submit: axiosError.response?.data?.error?.message || 'Failed to update opportunity',
      });
    },
  });

  const isPending = createMutation.isPending || updateMutation.isPending;

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }

    if (!formData.account_id) {
      newErrors.account_id = 'Account is required';
    }

    if (formData.value && parseFloat(formData.value) <= 0) {
      newErrors.value = 'Value must be greater than 0';
    }

    if (formData.probability) {
      const prob = parseInt(formData.probability, 10);
      if (isNaN(prob) || prob < 0 || prob > 100) {
        newErrors.probability = 'Probability must be between 0 and 100';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    const data: OpportunityCreate | OpportunityUpdate = {
      title: formData.title.trim(),
      account_id: parseInt(formData.account_id, 10),
      stage: formData.stage,
    };

    if (formData.contact_id) {
      data.contact_id = parseInt(formData.contact_id, 10);
    }

    if (formData.value) {
      data.value = parseFloat(formData.value);
    }

    if (formData.probability) {
      data.probability = parseInt(formData.probability, 10);
    }

    if (formData.expected_close_date) {
      data.expected_close_date = formData.expected_close_date;
    }

    if (isEdit) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data as OpportunityCreate);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
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
      <div className="relative bg-white rounded-xl shadow-lg w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 sticky top-0 bg-white">
          <h2 className="text-lg font-semibold text-slate-900">
            {isEdit ? 'Edit Opportunity' : 'New Opportunity'}
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
            <label htmlFor="title" className="block text-sm font-medium text-slate-700 mb-1">
              Title <span className="text-red-500">*</span>
            </label>
            <input
              id="title"
              name="title"
              type="text"
              value={formData.title}
              onChange={handleChange}
              className={`w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                errors.title ? 'border-red-300' : 'border-slate-300'
              }`}
              placeholder="Opportunity title"
            />
            {errors.title && <p className="mt-1 text-xs text-red-500">{errors.title}</p>}
          </div>

          <div>
            <label htmlFor="account_id" className="block text-sm font-medium text-slate-700 mb-1">
              Account <span className="text-red-500">*</span>
            </label>
            <select
              id="account_id"
              name="account_id"
              value={formData.account_id}
              onChange={handleChange}
              className={`w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                errors.account_id ? 'border-red-300' : 'border-slate-300'
              }`}
            >
              <option value="">Select an account</option>
              {accountsData?.data.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.name}
                </option>
              ))}
            </select>
            {errors.account_id && <p className="mt-1 text-xs text-red-500">{errors.account_id}</p>}
          </div>

          <div>
            <label htmlFor="stage" className="block text-sm font-medium text-slate-700 mb-1">
              Stage
            </label>
            <select
              id="stage"
              name="stage"
              value={formData.stage}
              onChange={handleChange}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              {STAGE_ORDER.map((stage) => (
                <option key={stage} value={stage}>
                  {STAGE_LABELS[stage]}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="value" className="block text-sm font-medium text-slate-700 mb-1">
                Value (USD)
              </label>
              <input
                id="value"
                name="value"
                type="number"
                min="0.01"
                step="0.01"
                value={formData.value}
                onChange={handleChange}
                className={`w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                  errors.value ? 'border-red-300' : 'border-slate-300'
                }`}
                placeholder="0.00"
              />
              {errors.value && <p className="mt-1 text-xs text-red-500">{errors.value}</p>}
            </div>

            <div>
              <label
                htmlFor="probability"
                className="block text-sm font-medium text-slate-700 mb-1"
              >
                Probability (%)
              </label>
              <input
                id="probability"
                name="probability"
                type="number"
                min="0"
                max="100"
                value={formData.probability}
                onChange={handleChange}
                className={`w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                  errors.probability ? 'border-red-300' : 'border-slate-300'
                }`}
                placeholder="0-100"
              />
              {errors.probability && (
                <p className="mt-1 text-xs text-red-500">{errors.probability}</p>
              )}
            </div>
          </div>

          <div>
            <label
              htmlFor="expected_close_date"
              className="block text-sm font-medium text-slate-700 mb-1"
            >
              Expected Close Date
            </label>
            <input
              id="expected_close_date"
              name="expected_close_date"
              type="date"
              value={formData.expected_close_date}
              onChange={handleChange}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
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
              {isEdit ? 'Save Changes' : 'Create Opportunity'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
