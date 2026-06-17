import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Loader2, ArrowRight } from 'lucide-react';
import { convertLead } from './api';

interface LeadConvertModalProps {
  leadId: number;
  leadName: string;
  onClose: () => void;
}

export function LeadConvertModal({ leadId, leadName, onClose }: LeadConvertModalProps) {
  const queryClient = useQueryClient();
  const [convertedOpp, setConvertedOpp] = useState<{ id: number; title: string } | null>(null);
  const [apiError, setApiError] = useState<{ message: string; opportunityId?: number } | null>(null);

  const mutation = useMutation({
    mutationFn: () => convertLead(leadId),
    onSuccess: (opp) => {
      queryClient.invalidateQueries({ queryKey: ['lead', leadId] });
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      setConvertedOpp(opp);
    },
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { error?: { message?: string; opportunity_id?: number } } } };
      const errorData = axiosError.response?.data?.error;
      setApiError({
        message: errorData?.message ?? 'Conversion failed',
        opportunityId: errorData?.opportunity_id,
      });
    },
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-xl p-6 max-w-sm w-full mx-4">
        {convertedOpp ? (
          <div className="text-center space-y-3">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto">
              <ArrowRight className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="text-base font-semibold text-slate-900">Lead Converted!</h3>
            <p className="text-sm text-slate-600">
              "{leadName}" has been converted to an opportunity.
            </p>
            <Link
              to={`/opportunities/${convertedOpp.id}`}
              onClick={onClose}
              className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors"
            >
              View Opportunity <ArrowRight className="h-4 w-4" />
            </Link>
            <div>
              <button onClick={onClose} className="mt-1 text-sm text-slate-500 hover:text-slate-700">Close</button>
            </div>
          </div>
        ) : (
          <>
            <h3 className="text-base font-semibold text-slate-900 mb-2">Convert Lead</h3>
            <p className="text-sm text-slate-600 mb-4">
              This will create an Account, Contact, and Opportunity from "{leadName}". This action cannot be undone.
            </p>
            {apiError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                {apiError.message}
                {apiError.opportunityId && (
                  <div className="mt-1">
                    <Link to={`/opportunities/${apiError.opportunityId}`} onClick={onClose} className="underline font-medium">
                      View existing opportunity →
                    </Link>
                  </div>
                )}
              </div>
            )}
            <div className="flex justify-end gap-3">
              <button onClick={onClose} className="px-4 py-2 text-sm text-slate-700 hover:bg-slate-100 rounded-lg">Cancel</button>
              <button
                onClick={() => mutation.mutate()}
                disabled={mutation.isPending}
                className="px-4 py-2 text-sm text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg disabled:opacity-50 flex items-center gap-2"
              >
                {mutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                Convert
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
