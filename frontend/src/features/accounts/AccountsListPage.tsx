import { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Search, Loader2, Building2, Trash2, Pencil, ChevronLeft, ChevronRight } from 'lucide-react';
import { listAccounts, deleteAccount } from './api';
import type { Account } from './types';
import { AccountForm } from './AccountForm';
import { useAuth } from '../../context/useAuth';

const DEFAULT_LIMIT = 20;

export function AccountsListPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const { hasPermission } = useAuth();

  const search = searchParams.get('search') || '';
  const offset = parseInt(searchParams.get('offset') || '0', 10);
  const limit = parseInt(searchParams.get('limit') || String(DEFAULT_LIMIT), 10);

  const [searchInput, setSearchInput] = useState(search);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingAccount, setEditingAccount] = useState<Account | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<Account | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const canDelete = hasPermission('accounts:delete');

  useEffect(() => {
    document.title = 'Accounts | CRM';
  }, []);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['accounts', { search, offset, limit }],
    queryFn: () => listAccounts({ search: search || undefined, offset, limit }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteAccount,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      setDeleteConfirm(null);
      setDeleteError(null);
    },
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { error?: { code?: string; message?: string; contact_count?: number; opportunity_count?: number } } } };
      const errorData = axiosError.response?.data?.error;
      if (errorData?.code === 'ACCOUNT_HAS_DEPENDENTS') {
        const contactCount = errorData.contact_count || 0;
        const opportunityCount = errorData.opportunity_count || 0;
        setDeleteError(
          `Cannot delete account. It has ${contactCount} contact(s) and ${opportunityCount} opportunity(ies) linked to it.`
        );
      } else {
        setDeleteError(errorData?.message || 'Failed to delete account');
      }
    },
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams(searchParams);
    if (searchInput.trim()) {
      params.set('search', searchInput.trim());
    } else {
      params.delete('search');
    }
    params.delete('offset');
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

  const handleEdit = (account: Account) => {
    setEditingAccount(account);
    setIsFormOpen(true);
  };

  const handleFormClose = () => {
    setIsFormOpen(false);
    setEditingAccount(null);
  };

  const handleFormSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['accounts'] });
    handleFormClose();
  };

  const handleDeleteClick = (account: Account) => {
    setDeleteError(null);
    setDeleteConfirm(account);
  };

  const handleDeleteConfirm = () => {
    if (deleteConfirm) {
      deleteMutation.mutate(deleteConfirm.id);
    }
  };

  const total = data?.meta.total || 0;
  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.ceil(total / limit);

  return (
    <div className="p-4 space-y-3">
      <div className="px-1 pb-1">
        <h1 className="text-base font-semibold text-slate-900 tracking-tight">Accounts</h1>
      </div>

      <div className="bg-white rounded-xl shadow-card border border-slate-100 overflow-hidden">
        {/* Search and New button row */}
        <div className="p-4 border-b border-slate-100 flex items-center gap-3">
          <form onSubmit={handleSearch} className="flex-1 max-w-sm">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search accounts..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </form>
          <button
            onClick={() => setIsFormOpen(true)}
            className="inline-flex items-center gap-1 rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 active:bg-indigo-800 transition-colors shadow-xs"
          >
            <Plus className="h-4 w-4" />
            New Account
          </button>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-indigo-600" />
            </div>
          ) : isError ? (
            <div className="flex items-center justify-center py-12 text-red-600">
              Error: {(error as Error).message}
            </div>
          ) : data?.data.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-500">
              <Building2 className="h-12 w-12 text-slate-300 mb-3" />
              <p className="text-sm font-medium">No accounts found</p>
              {search && <p className="text-xs mt-1">Try adjusting your search criteria</p>}
            </div>
          ) : (
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50">
                <tr className="border-b border-slate-100">
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Industry
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Website
                  </th>
                  <th className="px-4 py-2.5 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data?.data.map((account) => (
                  <tr key={account.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-medium">
                      <Link
                        to={`/accounts/${account.id}`}
                        className="text-indigo-600 hover:text-indigo-800 hover:underline"
                      >
                        {account.name}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-slate-600">{account.industry || '—'}</td>
                    <td className="px-4 py-3 text-slate-600">
                      {account.website ? (
                        <a
                          href={account.website}
                          target="_blank"
                          rel="noreferrer"
                          className="text-indigo-600 hover:underline"
                        >
                          {account.website}
                        </a>
                      ) : (
                        '—'
                      )}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="inline-flex items-center gap-1">
                        <button
                          onClick={() => handleEdit(account)}
                          className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
                          title="Edit"
                        >
                          <Pencil className="h-4 w-4" />
                        </button>
                        {canDelete && (
                          <button
                            onClick={() => handleDeleteClick(account)}
                            className="p-1.5 rounded-md text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Pagination */}
        {data && data.meta.total > limit && (
          <div className="px-4 py-3 border-t border-slate-100 flex items-center justify-between text-sm">
            <span className="text-slate-600">
              Showing {offset + 1}–{Math.min(offset + limit, total)} of {total}
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => handlePageChange(offset - limit)}
                disabled={offset === 0}
                className="p-1.5 rounded-md border border-slate-300 text-slate-600 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="text-slate-600">
                Page {currentPage} of {totalPages}
              </span>
              <button
                onClick={() => handlePageChange(offset + limit)}
                disabled={offset + limit >= total}
                className="p-1.5 rounded-md border border-slate-300 text-slate-600 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Account Form Modal */}
      {isFormOpen && (
        <AccountForm
          account={editingAccount}
          onClose={handleFormClose}
          onSuccess={handleFormSuccess}
        />
      )}

      {/* Delete Confirmation Dialog */}
      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50" onClick={() => setDeleteConfirm(null)} />
          <div className="relative bg-white rounded-xl shadow-lg p-6 max-w-sm w-full mx-4">
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Delete Account</h3>
            <p className="text-slate-600 text-sm mb-4">
              Are you sure you want to delete "{deleteConfirm.name}"? This action cannot be undone.
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
