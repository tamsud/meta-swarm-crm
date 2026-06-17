import { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Plus,
  Search,
  Loader2,
  Mail,
  Trash2,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  X,
} from 'lucide-react';
import { listMockEmails, createMockEmail, clearMockEmails } from '../../features/mock-email/api';
import type { MockEmailListItem, MockEmailCreate } from '../../features/mock-email/types';
import { ComposeModal } from '../../features/mock-email/components/ComposeModal';
import { ROUTES } from '../../routes/config';

const DEFAULT_LIMIT = 20;

type SortField = 'subject' | 'date';
type SortDirection = 'asc' | 'desc';

function getSortParam(field: SortField, direction: SortDirection): string {
  return direction === 'desc' ? `-${field}` : field;
}

function parseSortParam(sort: string | null): { field: SortField; direction: SortDirection } {
  if (!sort) return { field: 'date', direction: 'desc' };
  if (sort === 'subject') return { field: 'subject', direction: 'asc' };
  if (sort === '-subject') return { field: 'subject', direction: 'desc' };
  if (sort === 'date') return { field: 'date', direction: 'asc' };
  return { field: 'date', direction: 'desc' };
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;

  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
  });
}

export function MockEmailPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();

  const sort = searchParams.get('sort') || '-date';
  const search = searchParams.get('search') || '';
  const offset = parseInt(searchParams.get('offset') || '0', 10);
  const limit = parseInt(searchParams.get('limit') || String(DEFAULT_LIMIT), 10);

  const { field: sortField, direction: sortDirection } = parseSortParam(sort);

  const [searchInput, setSearchInput] = useState(search);
  const [showSearchInput, setShowSearchInput] = useState(!!search);
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [clearConfirm, setClearConfirm] = useState(false);

  useEffect(() => {
    document.title = 'Mail Inbox | CRM';
  }, []);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['mock-emails', { sort, search, offset, limit }],
    queryFn: () =>
      listMockEmails({
        sort: sort || undefined,
        search: search || undefined,
        offset,
        limit,
      }),
  });

  const composeMutation = useMutation({
    mutationFn: createMockEmail,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mock-emails'] });
      setIsComposeOpen(false);
    },
  });

  const clearMutation = useMutation({
    mutationFn: clearMockEmails,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mock-emails'] });
      setClearConfirm(false);
    },
  });

  const handleSort = (field: SortField) => {
    const params = new URLSearchParams(searchParams);
    let newDirection: SortDirection = 'asc';

    if (sortField === field) {
      newDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else if (field === 'date') {
      newDirection = 'desc';
    }

    params.set('sort', getSortParam(field, newDirection));
    params.delete('offset');
    setSearchParams(params);
  };

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

  const clearSearch = () => {
    setSearchInput('');
    setShowSearchInput(false);
    const params = new URLSearchParams(searchParams);
    params.delete('search');
    params.delete('offset');
    setSearchParams(params);
  };

  const handleCompose = async (data: MockEmailCreate) => {
    await composeMutation.mutateAsync(data);
  };

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return <ArrowUpDown className="h-3 w-3" />;
    }
    return sortDirection === 'asc' ? (
      <ArrowUp className="h-3 w-3" />
    ) : (
      <ArrowDown className="h-3 w-3" />
    );
  };

  const renderRow = (email: MockEmailListItem) => {
    const isUnread = email.status === 'unread';
    const detailPath = ROUTES.ADMIN_MOCK_EMAIL_DETAIL.replace(':id', email.id);

    return (
      <tr
        key={email.id}
        className={`hover:bg-slate-50 transition-colors ${isUnread ? 'bg-indigo-50/30' : ''}`}
      >
        <td className="px-4 py-3 font-medium max-w-[220px]">
          <div className="flex items-center gap-2">
            {isUnread && (
              <span className="inline-block w-2 h-2 rounded-full bg-indigo-500 flex-shrink-0" />
            )}
            <Link
              to={detailPath}
              className={`truncate block hover:underline ${
                isUnread ? 'text-indigo-600 font-semibold' : 'text-slate-700'
              }`}
            >
              {email.subject}
            </Link>
          </div>
        </td>
        <td className="px-4 py-3 text-slate-600 whitespace-nowrap">{email.from_email}</td>
        <td className="px-4 py-3 text-slate-500 whitespace-nowrap hidden md:table-cell">
          {email.to_email}
        </td>
        <td className="px-4 py-3 text-slate-400 max-w-[260px] hidden lg:table-cell">
          <span className="truncate block text-xs">{email.preview}</span>
        </td>
        <td className="px-4 py-3 text-slate-400 whitespace-nowrap text-xs">
          {formatDate(email.created_at)}
        </td>
        <td className="px-4 py-3 whitespace-nowrap">
          {isUnread ? (
            <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-indigo-50 text-indigo-600 ring-1 ring-inset ring-indigo-200">
              Unread
            </span>
          ) : (
            <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-slate-100 text-slate-600 ring-1 ring-inset ring-slate-200">
              Read
            </span>
          )}
        </td>
        <td></td>
      </tr>
    );
  };

  return (
    <div className="p-4 space-y-3">
      <div className="px-1 pb-1">
        <h1 className="text-base font-semibold text-slate-900 tracking-tight">Mail Inbox</h1>
      </div>

      <div className="bg-white rounded-xl shadow-card border border-slate-100 overflow-hidden">
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
              <Mail className="h-12 w-12 text-slate-300 mb-3" />
              <p className="text-sm font-medium">No emails found</p>
              {search && (
                <p className="text-xs mt-1">No emails match your search for "{search}"</p>
              )}
            </div>
          ) : (
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50">
                <tr className="border-b border-slate-100">
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider cursor-pointer select-none hover:text-slate-700 group">
                    <span className="flex items-center justify-between gap-2">
                      <span
                        className="flex items-center gap-1"
                        onClick={() => handleSort('subject')}
                      >
                        Subject
                        <span className="text-slate-300 group-hover:text-slate-400">
                          {getSortIcon('subject')}
                        </span>
                      </span>
                      {showSearchInput ? (
                        <form onSubmit={handleSearch} className="flex items-center gap-1">
                          <input
                            type="text"
                            value={searchInput}
                            onChange={(e) => setSearchInput(e.target.value)}
                            placeholder="Search..."
                            className="w-28 px-2 py-0.5 text-xs border border-slate-300 rounded focus:outline-none focus:ring-1 focus:ring-indigo-500"
                            autoFocus
                          />
                          <button
                            type="button"
                            onClick={clearSearch}
                            className="p-0.5 text-slate-400 hover:text-slate-600"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </form>
                      ) : (
                        <button
                          title="Search"
                          onClick={() => setShowSearchInput(true)}
                          className="p-1 rounded-md transition-colors text-slate-400 hover:text-slate-600 hover:bg-slate-100"
                        >
                          <Search className="h-3.5 w-3.5" />
                        </button>
                      )}
                    </span>
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    From
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">
                    To
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden lg:table-cell">
                    Preview
                  </th>
                  <th
                    className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider cursor-pointer select-none hover:text-slate-700 group"
                    onClick={() => handleSort('date')}
                  >
                    <span className="flex items-center gap-1">
                      Date
                      <span className="text-slate-300 group-hover:text-slate-400">
                        {getSortIcon('date')}
                      </span>
                    </span>
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-3 py-2.5 text-right whitespace-nowrap">
                    <div className="inline-flex items-center gap-1 justify-end">
                      <button
                        onClick={() => setClearConfirm(true)}
                        className="inline-flex items-center font-medium transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1 text-slate-600 hover:bg-slate-100 active:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed px-2 py-1 text-xs rounded-md gap-1"
                      >
                        <Trash2 className="h-3.5 w-3.5 flex-shrink-0" />
                        Clear
                      </button>
                      <div className="w-px h-4 bg-slate-200 mx-0.5"></div>
                      <div className="w-px h-4 bg-slate-200 mx-0.5"></div>
                      <button
                        onClick={() => setIsComposeOpen(true)}
                        className="inline-flex items-center gap-1 rounded-md bg-indigo-600 px-2.5 py-1.5 text-xs font-medium text-white hover:bg-indigo-700 active:bg-indigo-800 transition-colors shadow-xs"
                      >
                        <Plus className="h-3 w-3" />
                        Compose
                      </button>
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data?.data.map(renderRow)}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Compose Modal */}
      {isComposeOpen && (
        <ComposeModal
          onClose={() => setIsComposeOpen(false)}
          onSubmit={handleCompose}
          isSubmitting={composeMutation.isPending}
        />
      )}

      {/* Clear Confirmation Dialog */}
      {clearConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50" onClick={() => setClearConfirm(false)} />
          <div className="relative bg-white rounded-xl shadow-lg p-6 max-w-sm w-full mx-4">
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Clear All Emails</h3>
            <p className="text-slate-600 text-sm mb-4">
              Are you sure you want to delete all mock emails? This action cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setClearConfirm(false)}
                className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => clearMutation.mutate()}
                disabled={clearMutation.isPending}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {clearMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                Clear All
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
