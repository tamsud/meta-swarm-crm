import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ArrowLeft,
  Loader2,
  TrendingUp,
  Pencil,
  Trash2,
  Building2,
  User,
  Calendar,
  DollarSign,
  Percent,
} from 'lucide-react';
import { getOpportunity, updateOpportunity, deleteOpportunity } from './api';
import { getAccount } from '../accounts/api';
import { OpportunityForm } from './OpportunityForm';
import { OpportunityActivityList } from './OpportunityActivityList';
import { ROUTES } from '../../routes/config';
import { STAGE_ORDER, STAGE_LABELS, STAGE_COLORS } from './types';
import type { OpportunityStage } from './types';
import { useAuth } from '../../context/useAuth';

export function OpportunityDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { hasPermission } = useAuth();

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const opportunityId = id ? parseInt(id, 10) : NaN;
  const canDelete = hasPermission('opportunities:delete');

  useEffect(() => {
    document.title = 'Opportunity | CRM';
  }, []);

  const {
    data: opportunity,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['opportunity', opportunityId],
    queryFn: () => getOpportunity(opportunityId),
    enabled: !isNaN(opportunityId),
  });

  // Fetch the linked account
  const { data: account } = useQuery({
    queryKey: ['account', opportunity?.account_id],
    queryFn: () => getAccount(opportunity!.account_id),
    enabled: !!opportunity?.account_id,
  });

  useEffect(() => {
    if (opportunity) {
      document.title = `${opportunity.title} | CRM`;
    }
  }, [opportunity]);

  // Stage change mutation
  const stageMutation = useMutation({
    mutationFn: (stage: OpportunityStage) => updateOpportunity(opportunityId, { stage }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['opportunity', opportunityId] });
      queryClient.invalidateQueries({ queryKey: ['opportunities'] });
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: () => deleteOpportunity(opportunityId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['opportunities'] });
      navigate(ROUTES.OPPORTUNITIES);
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

  const handleStageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    stageMutation.mutate(e.target.value as OpportunityStage);
  };

  const handleFormClose = () => {
    setIsFormOpen(false);
  };

  const handleFormSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['opportunity', opportunityId] });
    queryClient.invalidateQueries({ queryKey: ['opportunities'] });
    setIsFormOpen(false);
  };

  const handleDeleteConfirm = () => {
    deleteMutation.mutate();
  };

  const formatCurrency = (value: string | null) => {
    if (!value) return null;
    const num = parseFloat(value);
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(num);
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return null;
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (isNaN(opportunityId)) {
    return (
      <div className="p-4">
        <div className="bg-white rounded-xl shadow-card border border-slate-100 p-8 text-center">
          <TrendingUp className="h-12 w-12 text-slate-300 mx-auto mb-3" />
          <h2 className="text-lg font-semibold text-slate-900 mb-2">Invalid Opportunity ID</h2>
          <p className="text-slate-500 mb-4">The opportunity ID provided is not valid.</p>
          <Link
            to={ROUTES.OPPORTUNITIES}
            className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-800"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Pipeline
          </Link>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="p-4">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-indigo-600" />
        </div>
      </div>
    );
  }

  if (isError) {
    const axiosError = error as { response?: { status?: number } };
    const is404 = axiosError.response?.status === 404;

    return (
      <div className="p-4">
        <div className="bg-white rounded-xl shadow-card border border-slate-100 p-8 text-center">
          <TrendingUp className="h-12 w-12 text-slate-300 mx-auto mb-3" />
          <h2 className="text-lg font-semibold text-slate-900 mb-2">
            {is404 ? 'Opportunity Not Found' : 'Error Loading Opportunity'}
          </h2>
          <p className="text-slate-500 mb-4">
            {is404
              ? 'The opportunity you are looking for does not exist.'
              : (error as Error).message}
          </p>
          <Link
            to={ROUTES.OPPORTUNITIES}
            className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-800"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Pipeline
          </Link>
        </div>
      </div>
    );
  }

  if (!opportunity) {
    return null;
  }

  return (
    <div className="p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate(ROUTES.OPPORTUNITIES)}
          className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          title="Back to Pipeline"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div className="flex-1">
          <h1 className="text-lg font-semibold text-slate-900">{opportunity.title}</h1>
          <p className="text-sm text-slate-500">
            {account?.name && (
              <Link to={`/accounts/${opportunity.account_id}`} className="text-indigo-600 hover:underline">
                {account.name}
              </Link>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsFormOpen(true)}
            className="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 active:bg-indigo-800 transition-colors shadow-xs"
          >
            <Pencil className="h-4 w-4" />
            Edit
          </button>
          {canDelete && (
            <button
              onClick={() => setDeleteConfirm(true)}
              className="inline-flex items-center gap-2 rounded-md border border-red-300 bg-white px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
            >
              <Trash2 className="h-4 w-4" />
              Delete
            </button>
          )}
        </div>
      </div>

      {/* Opportunity Info Card */}
      <div className="bg-white rounded-xl shadow-card border border-slate-100 p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Stage Dropdown */}
          <div className="flex items-start gap-3">
            <div className="p-2 bg-slate-50 rounded-lg">
              <TrendingUp className="h-4 w-4 text-slate-500" />
            </div>
            <div className="flex-1">
              <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Stage</p>
              <select
                value={opportunity.stage}
                onChange={handleStageChange}
                disabled={stageMutation.isPending}
                className={`px-2 py-1 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                  STAGE_COLORS[opportunity.stage as OpportunityStage]
                }`}
              >
                {STAGE_ORDER.map((stage) => (
                  <option key={stage} value={stage}>
                    {STAGE_LABELS[stage]}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Value */}
          <div className="flex items-start gap-3">
            <div className="p-2 bg-slate-50 rounded-lg">
              <DollarSign className="h-4 w-4 text-slate-500" />
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider">Value</p>
              <p className="text-sm text-slate-900 font-semibold">
                {formatCurrency(opportunity.value) || '---'}
              </p>
            </div>
          </div>

          {/* Probability */}
          <div className="flex items-start gap-3">
            <div className="p-2 bg-slate-50 rounded-lg">
              <Percent className="h-4 w-4 text-slate-500" />
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider">Probability</p>
              <p className="text-sm text-slate-900">
                {opportunity.probability !== null ? `${opportunity.probability}%` : '---'}
              </p>
            </div>
          </div>

          {/* Account */}
          <div className="flex items-start gap-3">
            <div className="p-2 bg-slate-50 rounded-lg">
              <Building2 className="h-4 w-4 text-slate-500" />
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider">Account</p>
              <Link
                to={`/accounts/${opportunity.account_id}`}
                className="text-sm text-indigo-600 hover:underline"
              >
                {account?.name || `Account #${opportunity.account_id}`}
              </Link>
            </div>
          </div>

          {/* Contact (if linked) */}
          {opportunity.contact_id && (
            <div className="flex items-start gap-3">
              <div className="p-2 bg-slate-50 rounded-lg">
                <User className="h-4 w-4 text-slate-500" />
              </div>
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider">Contact</p>
                <Link
                  to={`/contacts/${opportunity.contact_id}`}
                  className="text-sm text-indigo-600 hover:underline"
                >
                  Contact #{opportunity.contact_id}
                </Link>
              </div>
            </div>
          )}

          {/* Expected Close Date */}
          <div className="flex items-start gap-3">
            <div className="p-2 bg-slate-50 rounded-lg">
              <Calendar className="h-4 w-4 text-slate-500" />
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider">Expected Close</p>
              <p className="text-sm text-slate-900">
                {formatDate(opportunity.expected_close_date) || '---'}
              </p>
            </div>
          </div>
        </div>

        {/* Timestamps */}
        <div className="mt-4 pt-4 border-t border-slate-100 text-xs text-slate-500">
          <span>Created: {formatDate(opportunity.created_at)}</span>
          <span className="mx-3">|</span>
          <span>Updated: {formatDate(opportunity.updated_at)}</span>
        </div>
      </div>

      {/* Activities Section */}
      <div className="bg-white rounded-xl shadow-card border border-slate-100 overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-100">
          <h2 className="text-sm font-semibold text-slate-900">Activities</h2>
        </div>
        <div className="p-4">
          <OpportunityActivityList opportunityId={opportunityId} />
        </div>
      </div>

      {/* Edit Form Modal */}
      {isFormOpen && (
        <OpportunityForm
          opportunity={opportunity}
          onClose={handleFormClose}
          onSuccess={handleFormSuccess}
        />
      )}

      {/* Delete Confirmation Dialog */}
      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50" onClick={() => setDeleteConfirm(false)} />
          <div className="relative bg-white rounded-xl shadow-lg p-6 max-w-sm w-full mx-4">
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Delete Opportunity</h3>
            <p className="text-slate-600 text-sm mb-4">
              Are you sure you want to delete "{opportunity.title}"? This action cannot be undone.
            </p>
            {deleteError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{deleteError}</p>
              </div>
            )}
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setDeleteConfirm(false);
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
