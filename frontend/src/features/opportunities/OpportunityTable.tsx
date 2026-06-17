import { Link } from 'react-router-dom';
import { Pencil, Trash2, ChevronLeft, ChevronRight, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import type { Opportunity, OpportunityStage } from './types';
import { STAGE_LABELS, STAGE_COLORS } from './types';
import type { Account } from '../accounts/types';

interface OpportunityTableProps {
  opportunities: Opportunity[];
  accounts: Map<number, Account>;
  total: number;
  offset: number;
  limit: number;
  sortBy: string | null;
  sortOrder: 'asc' | 'desc';
  canDelete: boolean;
  onPageChange: (newOffset: number) => void;
  onSort: (field: string) => void;
  onEdit: (opp: Opportunity) => void;
  onDelete: (opp: Opportunity) => void;
}

export function OpportunityTable({
  opportunities,
  accounts,
  total,
  offset,
  limit,
  sortBy,
  sortOrder,
  canDelete,
  onPageChange,
  onSort,
  onEdit,
  onDelete,
}: OpportunityTableProps) {
  const formatCurrency = (value: string | null) => {
    if (!value) return '—';
    const num = parseFloat(value);
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num);
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const SortIcon = ({ field }: { field: string }) => {
    if (sortBy !== field) {
      return <ArrowUpDown className="h-3 w-3 text-slate-400" />;
    }
    return sortOrder === 'asc' ? (
      <ArrowUp className="h-3 w-3 text-indigo-600" />
    ) : (
      <ArrowDown className="h-3 w-3 text-indigo-600" />
    );
  };

  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.ceil(total / limit);

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50">
            <tr className="border-b border-slate-100">
              <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Title
              </th>
              <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Account
              </th>
              <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Stage
              </th>
              <th
                className="px-4 py-2.5 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider cursor-pointer hover:text-slate-700"
                onClick={() => onSort('value')}
              >
                <span className="inline-flex items-center gap-1">
                  Value
                  <SortIcon field="value" />
                </span>
              </th>
              <th className="px-4 py-2.5 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Probability
              </th>
              <th
                className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider cursor-pointer hover:text-slate-700"
                onClick={() => onSort('expected_close_date')}
              >
                <span className="inline-flex items-center gap-1">
                  Close Date
                  <SortIcon field="expected_close_date" />
                </span>
              </th>
              <th
                className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider cursor-pointer hover:text-slate-700"
                onClick={() => onSort('created_at')}
              >
                <span className="inline-flex items-center gap-1">
                  Created
                  <SortIcon field="created_at" />
                </span>
              </th>
              <th className="px-4 py-2.5 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {opportunities.map((opp) => (
              <tr key={opp.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 font-medium">
                  <Link
                    to={`/opportunities/${opp.id}`}
                    className="text-indigo-600 hover:text-indigo-800 hover:underline"
                  >
                    {opp.title}
                  </Link>
                </td>
                <td className="px-4 py-3 text-slate-600">
                  {accounts.get(opp.account_id) ? (
                    <Link
                      to={`/accounts/${opp.account_id}`}
                      className="text-indigo-600 hover:underline"
                    >
                      {accounts.get(opp.account_id)?.name}
                    </Link>
                  ) : (
                    '—'
                  )}
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-medium border ${
                      STAGE_COLORS[opp.stage as OpportunityStage]
                    }`}
                  >
                    {STAGE_LABELS[opp.stage as OpportunityStage]}
                  </span>
                </td>
                <td className="px-4 py-3 text-right font-medium text-slate-900">
                  {formatCurrency(opp.value)}
                </td>
                <td className="px-4 py-3 text-right text-slate-600">
                  {opp.probability !== null ? `${opp.probability}%` : '—'}
                </td>
                <td className="px-4 py-3 text-slate-600">{formatDate(opp.expected_close_date)}</td>
                <td className="px-4 py-3 text-slate-600">{formatDate(opp.created_at)}</td>
                <td className="px-4 py-3 text-right">
                  <div className="inline-flex items-center gap-1">
                    <button
                      onClick={() => onEdit(opp)}
                      className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
                      title="Edit"
                    >
                      <Pencil className="h-4 w-4" />
                    </button>
                    {canDelete && (
                      <button
                        onClick={() => onDelete(opp)}
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
      </div>

      {/* Pagination */}
      {total > limit && (
        <div className="px-4 py-3 border-t border-slate-100 flex items-center justify-between text-sm">
          <span className="text-slate-600">
            Showing {offset + 1}–{Math.min(offset + limit, total)} of {total}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onPageChange(offset - limit)}
              disabled={offset === 0}
              className="p-1.5 rounded-md border border-slate-300 text-slate-600 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <span className="text-slate-600">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => onPageChange(offset + limit)}
              disabled={offset + limit >= total}
              className="p-1.5 rounded-md border border-slate-300 text-slate-600 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
