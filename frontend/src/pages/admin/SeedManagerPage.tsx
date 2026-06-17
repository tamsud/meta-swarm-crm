import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Database, Loader2, Trash2, CheckCircle, AlertTriangle } from 'lucide-react';
import { seedData, clearData } from '../../features/admin/api';
import type { SeedSummary, ClearSummary } from '../../features/admin/api';

export function SeedManagerPage() {
  const queryClient = useQueryClient();
  const [seedResult, setSeedResult] = useState<SeedSummary | null>(null);
  const [clearResult, setClearResult] = useState<ClearSummary | null>(null);
  const [clearConfirmText, setClearConfirmText] = useState('');
  const [showClearModal, setShowClearModal] = useState(false);
  const [seedError, setSeedError] = useState<string | null>(null);
  const [clearError, setClearError] = useState<string | null>(null);

  useEffect(() => { document.title = 'Seed Manager | CRM'; }, []);

  const seedMutation = useMutation({
    mutationFn: seedData,
    onSuccess: (result) => {
      setSeedResult(result);
      setClearResult(null);
      setSeedError(null);
      queryClient.invalidateQueries();
    },
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { error?: { message?: string } } } };
      setSeedError(axiosError.response?.data?.error?.message ?? 'Seed failed');
    },
  });

  const clearMutation = useMutation({
    mutationFn: clearData,
    onSuccess: (result) => {
      setClearResult(result);
      setSeedResult(null);
      setClearError(null);
      setShowClearModal(false);
      setClearConfirmText('');
      queryClient.invalidateQueries();
    },
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { error?: { message?: string } } } };
      setClearError(axiosError.response?.data?.error?.message ?? 'Clear failed');
      setShowClearModal(false);
    },
  });

  return (
    <div className="p-4 space-y-4 max-w-2xl">
      <div className="px-1 pb-1">
        <h1 className="text-base font-semibold text-slate-900 tracking-tight">Seed Manager</h1>
        <p className="text-xs text-slate-500 mt-0.5">Populate or clear demo data for all CRM modules.</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-100 p-5 space-y-5">
        {/* Seed section */}
        <div>
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-sm font-semibold text-slate-800">Seed Demo Data</h2>
              <p className="text-xs text-slate-500 mt-0.5">Creates demo accounts, contacts, opportunities, leads, activities, and emails. Idempotent — skips existing records.</p>
            </div>
            <button
              onClick={() => { setSeedResult(null); seedMutation.mutate(); }}
              disabled={seedMutation.isPending}
              className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors disabled:opacity-50 flex-shrink-0 ml-4"
            >
              {seedMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Database className="h-4 w-4" />}
              Seed Data
            </button>
          </div>

          {seedError && (
            <div className="mt-3 flex items-start gap-2 p-3 bg-red-50 rounded-lg border border-red-100 text-sm text-red-700">
              <AlertTriangle className="h-4 w-4 flex-shrink-0 mt-0.5" />
              {seedError}
            </div>
          )}

          {seedResult && (
            <div className="mt-3 p-3 bg-green-50 rounded-lg border border-green-100">
              <div className="flex items-center gap-1.5 mb-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <p className="text-sm font-medium text-green-800">Seed complete</p>
              </div>
              <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                {Object.entries(seedResult).map(([entity, counts]) => (
                  <div key={entity} className="flex justify-between text-xs text-green-700">
                    <span className="capitalize">{entity.replace('_', ' ')}</span>
                    <span>{counts.created} created, {counts.skipped} skipped</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="border-t border-slate-100" />

        {/* Clear section */}
        <div>
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-sm font-semibold text-slate-800">Clear All Data</h2>
              <p className="text-xs text-slate-500 mt-0.5">Deletes all CRM records. Preserves permissions, roles, and the 3 demo users.</p>
            </div>
            <button
              onClick={() => { setClearError(null); setShowClearModal(true); }}
              disabled={clearMutation.isPending}
              className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-red-700 border border-red-200 bg-white hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50 flex-shrink-0 ml-4"
            >
              <Trash2 className="h-4 w-4" />
              Clear Data
            </button>
          </div>

          {clearError && (
            <div className="mt-3 flex items-start gap-2 p-3 bg-red-50 rounded-lg border border-red-100 text-sm text-red-700">
              <AlertTriangle className="h-4 w-4 flex-shrink-0 mt-0.5" />
              {clearError}
            </div>
          )}

          {clearResult && (
            <div className="mt-3 p-3 bg-amber-50 rounded-lg border border-amber-100">
              <p className="text-sm font-medium text-amber-800 mb-2">Data cleared</p>
              <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                {Object.entries(clearResult).map(([entity, count]) => (
                  <div key={entity} className="flex justify-between text-xs text-amber-700">
                    <span className="capitalize">{entity.replace('_', ' ')}</span>
                    <span>{count} deleted</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Clear confirmation modal */}
      {showClearModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50" onClick={() => { setShowClearModal(false); setClearConfirmText(''); }} />
          <div className="relative bg-white rounded-xl shadow-xl p-6 max-w-sm w-full mx-4">
            <h3 className="text-base font-semibold text-slate-900 mb-1">Confirm Clear</h3>
            <p className="text-sm text-slate-600 mb-4">
              This will permanently delete all CRM data. Type <strong>CLEAR</strong> to confirm.
            </p>
            <input
              type="text"
              value={clearConfirmText}
              onChange={(e) => setClearConfirmText(e.target.value)}
              placeholder="Type CLEAR"
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 mb-4"
              autoFocus
            />
            <div className="flex justify-end gap-3">
              <button onClick={() => { setShowClearModal(false); setClearConfirmText(''); }} className="px-4 py-2 text-sm text-slate-700 hover:bg-slate-100 rounded-lg">Cancel</button>
              <button
                onClick={() => clearMutation.mutate()}
                disabled={clearConfirmText !== 'CLEAR' || clearMutation.isPending}
                className="px-4 py-2 text-sm text-white bg-red-600 hover:bg-red-700 rounded-lg disabled:opacity-50 flex items-center gap-2"
              >
                {clearMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                Clear All Data
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
