import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import { Building2, User, Calendar, Percent } from 'lucide-react';
import type { Opportunity } from './types';

interface OpportunityCardProps {
  opportunity: Opportunity;
  accountName?: string;
  contactName?: string;
  onClick?: () => void;
}

export function OpportunityCard({
  opportunity,
  accountName,
  contactName,
  onClick,
}: OpportunityCardProps) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: opportunity.id,
    data: opportunity,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    opacity: isDragging ? 0.5 : 1,
  };

  const formatCurrency = (value: string | null) => {
    if (!value) return null;
    const num = parseFloat(value);
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num);
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return null;
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      onClick={onClick}
      className="bg-white rounded-lg border border-slate-200 p-3 shadow-sm hover:shadow-md transition-shadow cursor-grab active:cursor-grabbing"
    >
      <h4 className="font-medium text-slate-900 text-sm mb-2 line-clamp-2">
        {opportunity.title}
      </h4>

      {opportunity.value && (
        <div className="text-lg font-semibold text-indigo-600 mb-2">
          {formatCurrency(opportunity.value)}
        </div>
      )}

      <div className="space-y-1.5 text-xs text-slate-500">
        {accountName && (
          <div className="flex items-center gap-1.5">
            <Building2 className="h-3 w-3" />
            <span className="truncate">{accountName}</span>
          </div>
        )}

        {contactName && (
          <div className="flex items-center gap-1.5">
            <User className="h-3 w-3" />
            <span className="truncate">{contactName}</span>
          </div>
        )}

        <div className="flex items-center gap-3">
          {opportunity.probability !== null && (
            <div className="flex items-center gap-1">
              <Percent className="h-3 w-3" />
              <span>{opportunity.probability}%</span>
            </div>
          )}

          {opportunity.expected_close_date && (
            <div className="flex items-center gap-1">
              <Calendar className="h-3 w-3" />
              <span>{formatDate(opportunity.expected_close_date)}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
