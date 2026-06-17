import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Search, Loader2, Target, Trash2, Pencil, ChevronLeft, ChevronRight } from 'lucide-react';
import { listLeads, deleteLead } from './api';
import type { Lead, LeadStatus } from './types';
import { LeadForm } from './LeadForm';
import { ROUTES } from '../../routes/config';

const STATUS_TABS = [
  { label: 'All', value: '' },
  { label: 'New', value: 'new' },
  { label: 'Contacted', value: 'contacted' },
  { label: 'Qualified', value: 'qualified' },
  { label: 'Lost', value: 'lost' },
];

const STATUS_BADGE: Record<string, string> = {
  new: 'bg-slate-100 text-slate-700',
  contacted: 'bg-blue-100 text-blue-700',
  qualified: 'bg-green-100 text-green-700',
  lost: 'bg-red-100 text-red-700',
};

const DEFAULT_LIMIT = 20;

export function LeadsListPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();

  const statusParam = searchParams.get('status') || '';
  const search = searchParams.get('search') || '';
  const offset = parseInt(searchParams.get('offset') || '0', 10);
  const limit = DEFAULT_LIMIT;

  const [searchInput, setSearchInput] = useState(search);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingLead, setEditingLead] = useState<Lead | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<Lead | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  useEffect(() => { document.title = 'Leads | CRM'; }, []);

  const { data, isLoading, isError } = useQuery({
    queryKey: ['leads', { status: statusParam, search, offset, limit }],
    queryFn: () => listLeads({
      status: statusParam ? statusParam as LeadStatus : undefined,
      search: search || undefined,
      offset,
      limit,
    }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteLead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      setDeleteConfirm(null);
    },
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { error?: { message?: string } } } };
      setDeleteError(axiosError.response?.data?.error?.message ?? 'Failed to delete lead');
    },
  });

  const setParam = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams);
    if (value) params.set(key, value); else params.delete(key);
    params.delete('offset');
    setSearchParams(params);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setParam('search', searchInput.trim());
  };

  const leads = data?.data ?? [];
  const total = data?.meta.total ?? 0;
  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.ceil(total / limit);

  return (
    <div className="p-4 space-y-3">
      <div className="px-1 pb-1 flex items-center justify-between">
        <h1 className="text-base font-semibold text-slate-900 tracking-tight">Leads</h1>
        <button
          onClick={() => { setEditingLead(null); setIsFormOpen(true); }}
          className="inline-flex items-center gap-1 rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors shadow-xs"
        >
          <Plus className="h-4 w-4" /> New Lead
        </button>
      </div>

      {/* Status tabs */}
      <div className="flex gap-1 border-b border-slate-200">
        {STATUS_TABS.map((tab) => (
          <button
            key={tab.value}
            onClick={() => setParam('status', tab.value)}
            className={`px-3 py-2 text-sm font-medium border-b-2 transition-colors ${
              statusParam === tab.value
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow-card border border-slate-100 overflow-hidden">
        {/* Search bar */}
        <div className="p-4 border-b border-slate-100">
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search leads..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <button type="submit" className="px-3 py-2 text-sm border border-slate-300 rounded-lg hover:bg-slate-50 text-slate-600">Search</button>
          </form>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-indigo-600" /></div>
        ) : isError ? (
          <div className="text-center py-12 text-red-600 text-sm">Failed to load leads.</div>
        ) : leads.length === 0 ? (
          <div className="flex flex-col items-center py-12 text-slate-500">
            <Target className="h-12 w-12 text-slate-300 mb-3" />
            <p className="text-sm font-medium">No leads found</p>
          </div>
        ) : (
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-100">
              <tr>
                <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Name</th>
                <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Email</th>
                <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Company</th>
                <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Source</th>
                <th className="px-4 py-2.5 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {leads.map((lead) => (
                <tr key={lead.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3 font-medium">
                    <Link to={`${ROUTES.LEADS}/${lead.id}`} className="text-indigo-600 hover:underline">
                      {lead.first_name} {lead.last_name}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-slate-600">{lead.email}</td>
                  <td className="px-4 py-3 text-slate-600">{lead.company ?? '—'}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${
                      lead.converted_opportunity_id ? 'bg-indigo-100 text-indigo-700' : (STATUS_BADGE[lead.status] ?? '')
                    }`}>
                      {lead.converted_opportunity_id ? 'Converted' : lead.status.charAt(0).toUpperCase() + lead.status.slice(1)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-500 text-xs">{lead.source ?? '—'}</td>
                  <td className="px-4 py-3 text-right">
                    <div className="inline-flex items-center gap-1">
                      <button onClick={() => { setEditingLead(lead); setIsFormOpen(true); }} className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100"><Pencil className="h-4 w-4" /></button>
                      <button onClick={() => { setDeleteError(null); setDeleteConfirm(lead); }} className="p-1.5 rounded-md text-slate-400 hover:text-red-600 hover:bg-red-50"><Trash2 className="h-4 w-4" /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {total > limit && (
          <div className="px-4 py-3 border-t border-slate-100 flex items-center justify-between text-sm">
            <span className="text-slate-600">Showing {offset + 1}–{Math.min(offset + limit, total)} of {total}</span>
            <div className="flex items-center gap-2">
              <button onClick={() => setParam('offset', String(Math.max(0, offset - limit)))} disabled={offset === 0} className="p-1.5 rounded-md border border-slate-300 text-slate-600 hover:bg-slate-50 disabled:opacity-50">
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="text-slate-600">Page {currentPage} of {totalPages}</span>
              <button onClick={() => setParam('offset', String(offset + limit))} disabled={offset + limit >= total} className="p-1.5 rounded-md border border-slate-300 text-slate-600 hover:bg-slate-50 disabled:opacity-50">
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {isFormOpen && (
        <LeadForm lead={editingLead} onClose={() => { setIsFormOpen(false); setEditingLead(null); }} onSuccess={() => { queryClient.invalidateQueries({ queryKey: ['leads'] }); setIsFormOpen(false); setEditingLead(null); }} />
      )}

      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50" onClick={() => setDeleteConfirm(null)} />
          <div className="relative bg-white rounded-xl shadow-lg p-6 max-w-sm w-full mx-4">
            <h3 className="text-base font-semibold text-slate-900 mb-2">Delete Lead</h3>
            <p className="text-sm text-slate-600 mb-4">Delete "{deleteConfirm.first_name} {deleteConfirm.last_name}"? This cannot be undone.</p>
            {deleteError && <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">{deleteError}</div>}
            <div className="flex justify-end gap-3">
              <button onClick={() => { setDeleteConfirm(null); setDeleteError(null); }} className="px-4 py-2 text-sm text-slate-700 hover:bg-slate-100 rounded-lg">Cancel</button>
              <button onClick={() => deleteMutation.mutate(deleteConfirm.id)} disabled={deleteMutation.isPending} className="px-4 py-2 text-sm text-white bg-red-600 hover:bg-red-700 rounded-lg disabled:opacity-50 flex items-center gap-2">
                {deleteMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
