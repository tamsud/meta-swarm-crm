import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { TrendingUp, Plus, Loader2, Trash2 } from 'lucide-react';
import { listOpportunities, deleteOpportunity } from '../opportunities/api';
import { OpportunityForm } from '../opportunities/OpportunityForm';
import { STAGE_LABELS, STAGE_COLORS } from '../opportunities/types';
import type { Opportunity, OpportunityStage } from '../opportunities/types';
import { useAuth } from '../../context/useAuth';

interface AccountOpportunitiesTabProps {
  accountId: number;
}

export function AccountOpportunitiesTab({ accountId }: AccountOpportunitiesTabProps) {
  const queryClient = useQueryClient();
  const { hasPermission } = useAuth();
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<Opportunity | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const canDelete = hasPermission('opportunities:delete');

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['opportunities', { account_id: accountId }],
    queryFn: () => listOpportunities({ account_id: accountId, limit: 100 }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteOpportunity,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['opportunities'] });
      setDeleteConfirm(null);
      setDeleteError(null);
    },
    onError: (err: unknown) => {
      const axiosError = err as {
        response?: { data?: { error?: { message?: string } } };
      };
      setDeleteError(
        axiosError.response?.data?.error?.message || 'Failed to delete opportunity'
      );
    },
  });

  const handleFormClose = () => {
    setIsFormOpen(false);
  };

  const handleFormSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['opportunities'] });
    setIsFormOpen(false);
  };

  const handleDeleteConfirm = () => {
    if (deleteConfirm) {
      deleteMutation.mutate(deleteConfirm.id);
    }
  };

  const formatCurrency = (value: string | null) => {
    if (!value) return '---';
    const num = parseFloat(value);
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-indigo-600" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex items-center justify-center py-8 text-red-600">
        Error: {(error as Error).message}
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm text-slate-500">
          {data?.meta.total || 0} opportunity(ies)
        </span>
        <button
          onClick={() => setIsFormOpen(true)}
          className="inline-flex items-center gap-1 rounded-md bg-indigo-600 px-2 py-1.5 text-xs font-medium text-white hover:bg-indigo-700 transition-colors"
        >
          <Plus className="h-3 w-3" />
          Add
        </button>
      </div>

      {data?.data.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8 text-slate-500">
          <TrendingUp className="h-10 w-10 text-slate-300 mb-3" />
          <p className="text-sm font-medium">No opportunities</p>
          <p className="text-xs mt-1">Create an opportunity to get started</p>
        </div>
      ) : (
        <div className="space-y-2">
          {data?.data.map((opp) => (
            <div
              key={opp.id}
              className="flex items-center justify-between p-3 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors"
            >
              <div className="flex-1 min-w-0">
                <Link
                  to={`/opportunities/${opp.id}`}
                  className="text-sm font-medium text-indigo-600 hover:underline truncate block"
                >
                  {opp.title}
                </Link>
                <div className="flex items-center gap-3 mt-1 text-xs text-slate-500">
                  <span
                    className={`px-2 py-0.5 rounded border ${
                      STAGE_COLORS[opp.stage as OpportunityStage]
                    }`}
                  >
                    {STAGE_LABELS[opp.stage as OpportunityStage]}
                  </span>
                  <span className="font-medium text-slate-700">
                    {formatCurrency(opp.value)}
                  </span>
                  {opp.probability !== null && <span>{opp.probability}%</span>}
                </div>
              </div>
              {canDelete && (
                <button
                  onClick={() => {
                    setDeleteError(null);
                    setDeleteConfirm(opp);
                  }}
                  className="p-1.5 rounded-md text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors ml-2"
                  title="Delete"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Opportunity Form Modal */}
      {isFormOpen && (
        <OpportunityForm
          defaultAccountId={accountId}
          onClose={handleFormClose}
          onSuccess={handleFormSuccess}
        />
      )}

      {/* Delete Confirmation Dialog */}
      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50" onClick={() => setDeleteConfirm(null)} />
          <div className="relative bg-white rounded-xl shadow-lg p-6 max-w-sm w-full mx-4">
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Delete Opportunity</h3>
            <p className="text-slate-600 text-sm mb-4">
              Are you sure you want to delete "{deleteConfirm.title}"? This action cannot be undone.
            </p>
            {deleteError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{deleteError}</p>
              </div>
            )}
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setDeleteConfirm(null);
                  setDeleteError(null);
                }}
                className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteConfirm}
                disabled={deleteMutation.isPending}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {deleteMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
