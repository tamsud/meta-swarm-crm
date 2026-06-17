import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { X, Loader2 } from 'lucide-react';
import { createLead, updateLead } from './api';
import type { Lead, LeadCreate, LeadStatus } from './types';

interface LeadFormProps {
  lead?: Lead | null;
  onClose: () => void;
  onSuccess: () => void;
}

const STATUS_OPTIONS: LeadStatus[] = ['new', 'contacted', 'qualified', 'lost'];

export function LeadForm({ lead, onClose, onSuccess }: LeadFormProps) {
  const queryClient = useQueryClient();
  const [firstName, setFirstName] = useState(lead?.first_name ?? '');
  const [lastName, setLastName] = useState(lead?.last_name ?? '');
  const [email, setEmail] = useState(lead?.email ?? '');
  const [phone, setPhone] = useState(lead?.phone ?? '');
  const [company, setCompany] = useState(lead?.company ?? '');
  const [status, setStatus] = useState<LeadStatus>(lead?.status ?? 'new');
  const [source, setSource] = useState(lead?.source ?? '');
  const [notes, setNotes] = useState(lead?.notes ?? '');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, []);

  const mutation = useMutation({
    mutationFn: (data: LeadCreate) =>
      lead ? updateLead(lead.id, data) : createLead(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      onSuccess();
    },
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { error?: { message?: string } } } };
      setError(axiosError.response?.data?.error?.message ?? 'Failed to save lead');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    mutation.mutate({ first_name: firstName, last_name: lastName, email, phone: phone || undefined, company: company || undefined, status, source: source || undefined, notes: notes || undefined });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-xl p-6 max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-slate-900">{lead ? 'Edit Lead' : 'New Lead'}</h2>
          <button onClick={onClose} className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100"><X className="h-4 w-4" /></button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">First Name *</label>
              <input type="text" value={firstName} onChange={(e) => setFirstName(e.target.value)} required className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">Last Name *</label>
              <input type="text" value={lastName} onChange={(e) => setLastName(e.target.value)} required className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">Email *</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">Phone</label>
              <input type="text" value={phone} onChange={(e) => setPhone(e.target.value)} className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">Company</label>
              <input type="text" value={company} onChange={(e) => setCompany(e.target.value)} className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">Status</label>
              <select value={status} onChange={(e) => setStatus(e.target.value as LeadStatus)} className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">
                {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">Source</label>
              <input type="text" value={source} onChange={(e) => setSource(e.target.value)} placeholder="e.g. Website, LinkedIn" className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">Notes</label>
            <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={3} className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" />
          </div>
          {error && <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">{error}</div>}
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg">Cancel</button>
            <button type="submit" disabled={mutation.isPending} className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg disabled:opacity-50 flex items-center gap-2">
              {mutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              {lead ? 'Save Changes' : 'Create Lead'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
