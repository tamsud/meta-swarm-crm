import { useMutation, useQueryClient } from '@tanstack/react-query';
import { CheckCircle, Loader2 } from 'lucide-react';
import { updateLead } from './api';
import type { Lead, LeadStatus } from './types';
import { VALID_TRANSITIONS } from './types';

const STATUS_LABELS: Record<string, string> = {
  new: 'New',
  contacted: 'Contacted',
  qualified: 'Qualified',
  lost: 'Lost',
  converted: 'Converted',
};

const STATUS_COLORS: Record<string, string> = {
  new: 'bg-slate-100 text-slate-700',
  contacted: 'bg-blue-100 text-blue-700',
  qualified: 'bg-green-100 text-green-700',
  lost: 'bg-red-100 text-red-700',
  converted: 'bg-indigo-100 text-indigo-700',
};

interface LeadStatusControlProps {
  lead: Lead;
}

export function LeadStatusControl({ lead }: LeadStatusControlProps) {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (newStatus: LeadStatus) => updateLead(lead.id, { status: newStatus }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lead', lead.id] });
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });

  const isConverted = !!lead.converted_opportunity_id;
  const currentStatus = isConverted ? 'converted' : lead.status;
  const validNextStates = isConverted ? [] : (VALID_TRANSITIONS[lead.status] ?? []);

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <span className="text-xs font-medium text-slate-500">Status:</span>
        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[currentStatus] ?? 'bg-slate-100 text-slate-700'}`}>
          {isConverted && <CheckCircle className="h-3 w-3" />}
          {STATUS_LABELS[currentStatus]}
        </span>
      </div>
      {!isConverted && validNextStates.length > 0 && (
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500">Move to:</span>
          {validNextStates.map((nextStatus) => (
            <button
              key={nextStatus}
              onClick={() => mutation.mutate(nextStatus)}
              disabled={mutation.isPending}
              className={`px-2.5 py-1 rounded-full text-xs font-medium border transition-colors disabled:opacity-50 ${
                nextStatus === 'lost'
                  ? 'border-red-300 text-red-700 hover:bg-red-50'
                  : 'border-indigo-300 text-indigo-700 hover:bg-indigo-50'
              }`}
            >
              {mutation.isPending ? <Loader2 className="h-3 w-3 animate-spin inline" /> : STATUS_LABELS[nextStatus]}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
