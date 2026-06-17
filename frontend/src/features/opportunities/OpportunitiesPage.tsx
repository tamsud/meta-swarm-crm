import { useState, useEffect, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Plus,
  Loader2,
  TrendingUp,
  LayoutGrid,
  List,
  Filter,
} from 'lucide-react';
import { listOpportunities, updateOpportunity, deleteOpportunity } from './api';
import { listAccounts } from '../accounts/api';
import type { Opportunity, OpportunityStage } from './types';
import { STAGE_ORDER, STAGE_LABELS } from './types';
import { OpportunityBoard } from './OpportunityBoard';
import { OpportunityTable } from './OpportunityTable';
import { OpportunityForm } from './OpportunityForm';
import { useAuth } from '../../context/useAuth';

const DEFAULT_LIMIT = 100;
const VIEW_PREFERENCE_KEY = 'opportunities_view_preference';

type ViewMode = 'board' | 'table';

export function OpportunitiesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { hasPermission } = useAuth();

  // View mode with localStorage persistence
  const [viewMode, setViewMode] = useState<ViewMode>(() => {
    const saved = localStorage.getItem(VIEW_PREFERENCE_KEY);
    return (saved === 'table' ? 'table' : 'board') as ViewMode;
  });

  // Filters from URL
  const stageFilter = (searchParams.get('stage') as OpportunityStage) || undefined;
  const accountIdFilter = searchParams.get('account_id')
    ? parseInt(searchParams.get('account_id')!, 10)
    : undefined;
  const offset = parseInt(searchParams.get('offset') || '0', 10);
  const limit = parseInt(searchParams.get('limit') || String(DEFAULT_LIMIT), 10);
  const sortBy = searchParams.get('sort_by') || null;
  const sortOrder = (searchParams.get('sort_order') || 'asc') as 'asc' | 'desc';

  // UI state
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingOpportunity, setEditingOpportunity] = useState<Opportunity | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<Opportunity | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  const canDelete = hasPermission('opportunities:delete');

  useEffect(() => {
    document.title = 'Pipeline | CRM';
  }, []);

  // Persist view mode to localStorage
  useEffect(() => {
    localStorage.setItem(VIEW_PREFERENCE_KEY, viewMode);
  }, [viewMode]);

  // Fetch opportunities
  const { data: opportunitiesData, isLoading, isError, error } = useQuery({
    queryKey: [
      'opportunities',
      { stage: stageFilter, account_id: accountIdFilter, offset, limit, sort_by: sortBy, sort_order: sortOrder },
    ],
    queryFn: () =>
      listOpportunities({
        stage: stageFilter,
        account_id: accountIdFilter,
        offset,
        limit,
        sort_by: sortBy || undefined,
        sort_order: sortOrder,
      }),
  });

  // Fetch accounts for filtering and display
  const { data: accountsData } = useQuery({
    queryKey: ['accounts', { limit: 1000 }],
    queryFn: () => listAccounts({ limit: 1000 }),
  });

  const accountsMap = useMemo(() => {
    return new Map(accountsData?.data.map((acc) => [acc.id, acc]) || []);
  }, [accountsData]);

  // Update mutation for stage changes (drag-and-drop)
  const stageMutation = useMutation({
    mutationFn: ({ id, stage }: { id: number; stage: OpportunityStage }) =>
      updateOpportunity(id, { stage }),
    onMutate: async ({ id, stage }) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ['opportunities'] });
      const previousData = queryClient.getQueryData(['opportunities']);

      queryClient.setQueriesData({ queryKey: ['opportunities'] }, (old: unknown) => {
        if (!old || typeof old !== 'object') return old;
        const data = old as { data: Opportunity[] };
        return {
          ...data,
          data: data.data.map((opp: Opportunity) =>
            opp.id === id ? { ...opp, stage } : opp
          ),
        };
      });

      return { previousData };
    },
    onError: (_err, _variables, context) => {
      // Rollback on error
      if (context?.previousData) {
        queryClient.setQueryData(['opportunities'], context.previousData);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['opportunities'] });
    },
  });

  // Delete mutation
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

  const handleStageChange = (opportunityId: number, newStage: OpportunityStage) => {
    stageMutation.mutate({ id: opportunityId, stage: newStage });
  };

  const handleOpportunityClick = (opp: Opportunity) => {
    navigate(`/opportunities/${opp.id}`);
  };

  const handleFilterChange = (key: string, value: string | null) => {
    const params = new URLSearchParams(searchParams);
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    params.delete('offset'); // Reset pagination when filter changes
    setSearchParams(params);
  };

  const handleSort = (field: string) => {
    const params = new URLSearchParams(searchParams);
    if (sortBy === field) {
      // Toggle sort order
      params.set('sort_order', sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      params.set('sort_by', field);
      params.set('sort_order', 'asc');
    }
    setSearchParams(params);
  };

  const handlePageChange = (newOffset: number) => {
    const params = new URLSearchParams(searchParams);
    if (newOffset > 0) {
      params.set('offset', String(newOffset));
    } else {
      params.delete('offset');
    }
    setSearchParams(params);
  };

  const handleEdit = (opp: Opportunity) => {
    setEditingOpportunity(opp);
    setIsFormOpen(true);
  };

  const handleFormClose = () => {
    setIsFormOpen(false);
    setEditingOpportunity(null);
  };

  const handleFormSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['opportunities'] });
    handleFormClose();
  };

  const handleDeleteClick = (opp: Opportunity) => {
    setDeleteError(null);
    setDeleteConfirm(opp);
  };

  const handleDeleteConfirm = () => {
    if (deleteConfirm) {
      deleteMutation.mutate(deleteConfirm.id);
    }
  };

  const clearFilters = () => {
    setSearchParams({});
  };

  const hasActiveFilters = stageFilter || accountIdFilter;

  return (
    <div className="p-4 space-y-3">
      <div className="px-1 pb-1">
        <h1 className="text-base font-semibold text-slate-900 tracking-tight">Pipeline</h1>
      </div>

      <div className="bg-white rounded-xl shadow-card border border-slate-100 overflow-hidden">
        {/* Toolbar */}
        <div className="p-4 border-b border-slate-100 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            {/* View toggle */}
            <div className="inline-flex rounded-lg border border-slate-300 p-0.5">
              <button
                onClick={() => setViewMode('board')}
                className={`p-1.5 rounded-md transition-colors ${
                  viewMode === 'board'
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
                title="Board view"
              >
                <LayoutGrid className="h-4 w-4" />
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={`p-1.5 rounded-md transition-colors ${
                  viewMode === 'table'
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
                title="Table view"
              >
                <List className="h-4 w-4" />
              </button>
            </div>

            {/* Filter toggle */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`p-2 rounded-md border transition-colors ${
                showFilters || hasActiveFilters
                  ? 'border-indigo-300 bg-indigo-50 text-indigo-700'
                  : 'border-slate-300 text-slate-500 hover:text-slate-700'
              }`}
            >
              <Filter className="h-4 w-4" />
            </button>

            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="text-xs text-slate-500 hover:text-slate-700 underline"
              >
                Clear filters
              </button>
            )}
          </div>

          <button
            onClick={() => setIsFormOpen(true)}
            className="inline-flex items-center gap-1 rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 active:bg-indigo-800 transition-colors shadow-xs"
          >
            <Plus className="h-4 w-4" />
            New Opportunity
          </button>
        </div>

        {/* Filters panel */}
        {showFilters && (
          <div className="p-4 border-b border-slate-100 bg-slate-50 flex items-center gap-4">
            <div>
              <label
                htmlFor="stage-filter"
                className="block text-xs font-medium text-slate-500 mb-1"
              >
                Stage
              </label>
              <select
                id="stage-filter"
                value={stageFilter || ''}
                onChange={(e) => handleFilterChange('stage', e.target.value || null)}
                className="px-3 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">All stages</option>
                {STAGE_ORDER.map((stage) => (
                  <option key={stage} value={stage}>
                    {STAGE_LABELS[stage]}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label
                htmlFor="account-filter"
                className="block text-xs font-medium text-slate-500 mb-1"
              >
                Account
              </label>
              <select
                id="account-filter"
                value={accountIdFilter || ''}
                onChange={(e) => handleFilterChange('account_id', e.target.value || null)}
                className="px-3 py-1.5 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">All accounts</option>
                {accountsData?.data.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}

        {/* Content */}
        <div className="p-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-indigo-600" />
            </div>
          ) : isError ? (
            <div className="flex items-center justify-center py-12 text-red-600">
              Error: {(error as Error).message}
            </div>
          ) : opportunitiesData?.data.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-500">
              <TrendingUp className="h-12 w-12 text-slate-300 mb-3" />
              <p className="text-sm font-medium">No opportunities found</p>
              {hasActiveFilters && (
                <p className="text-xs mt-1">Try adjusting your filters</p>
              )}
            </div>
          ) : viewMode === 'board' ? (
            <OpportunityBoard
              opportunities={opportunitiesData?.data || []}
              accounts={accountsData?.data || []}
              onStageChange={handleStageChange}
              onOpportunityClick={handleOpportunityClick}
            />
          ) : (
            <OpportunityTable
              opportunities={opportunitiesData?.data || []}
              accounts={accountsMap}
              total={opportunitiesData?.meta.total || 0}
              offset={offset}
              limit={limit}
              sortBy={sortBy}
              sortOrder={sortOrder}
              canDelete={canDelete}
              onPageChange={handlePageChange}
              onSort={handleSort}
              onEdit={handleEdit}
              onDelete={handleDeleteClick}
            />
          )}
        </div>
      </div>

      {/* Opportunity Form Modal */}
      {isFormOpen && (
        <OpportunityForm
          opportunity={editingOpportunity}
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
