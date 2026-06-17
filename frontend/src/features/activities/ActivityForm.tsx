import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { X, Loader2 } from 'lucide-react';
import { createActivity, updateActivity } from './api';
import type { Activity, ActivityCreate, ActivityType } from './types';
import { listContacts } from '../contacts/api';
import { listOpportunities } from '../opportunities/api';

interface ActivityFormProps {
  activity?: Activity | null;
  prefillContactId?: number;
  prefillOpportunityId?: number;
  onClose: () => void;
  onSuccess: () => void;
}

export function ActivityForm({ activity, prefillContactId, prefillOpportunityId, onClose, onSuccess }: ActivityFormProps) {
  const queryClient = useQueryClient();

  const [type, setType] = useState<ActivityType>(activity?.type ?? 'call');
  const [subject, setSubject] = useState(activity?.subject ?? '');
  const [notes, setNotes] = useState(activity?.notes ?? '');
  const [contactId, setContactId] = useState<number | ''>(activity?.contact_id ?? prefillContactId ?? '');
  const [opportunityId, setOpportunityId] = useState<number | ''>(activity?.opportunity_id ?? prefillOpportunityId ?? '');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, []);

  const { data: contactsData } = useQuery({
    queryKey: ['contacts', { limit: 200 }],
    queryFn: () => listContacts({ limit: 200 }),
  });

  const { data: oppsData } = useQuery({
    queryKey: ['opportunities', { limit: 200 }],
    queryFn: () => listOpportunities({ limit: 200 }),
  });

  const mutation = useMutation({
    mutationFn: (data: ActivityCreate) =>
      activity ? updateActivity(activity.id, data) : createActivity(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['activities'] });
      onSuccess();
    },
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { error?: { message?: string } } } };
      setError(axiosError.response?.data?.error?.message ?? 'Failed to save activity');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!contactId && !opportunityId) {
      setError('At least one of Contact or Opportunity must be selected.');
      return;
    }
    setError(null);
    mutation.mutate({
      type,
      subject,
      notes: notes || undefined,
      contact_id: contactId || null,
      opportunity_id: opportunityId || null,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-xl p-6 max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-slate-900">
            {activity ? 'Edit Activity' : 'Log Activity'}
          </h2>
          <button onClick={onClose} className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100">
            <X className="h-4 w-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">Type</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value as ActivityType)}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="call">Call</option>
              <option value="email">Email</option>
              <option value="meeting">Meeting</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">Subject *</label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              required
              maxLength={512}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="e.g. Discovery call with John"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">Contact</label>
            <select
              value={contactId}
              onChange={(e) => setContactId(e.target.value ? parseInt(e.target.value, 10) : '')}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">— None —</option>
              {contactsData?.data.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.first_name} {c.last_name} ({c.email})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">Opportunity</label>
            <select
              value={opportunityId}
              onChange={(e) => setOpportunityId(e.target.value ? parseInt(e.target.value, 10) : '')}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">— None —</option>
              {oppsData?.data.map((o) => (
                <option key={o.id} value={o.id}>{o.title}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">Notes</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
              placeholder="Optional notes..."
            />
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
              {error}
            </div>
          )}

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
              disabled={mutation.isPending}
              className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {mutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              {activity ? 'Save Changes' : 'Log Activity'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
