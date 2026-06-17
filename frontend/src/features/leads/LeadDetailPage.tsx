import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Loader2, ArrowRight } from 'lucide-react';
import { getLead, deleteLead } from './api';
import { LeadForm } from './LeadForm';
import { LeadStatusControl } from './LeadStatusControl';
import { LeadConvertModal } from './LeadConvertModal';
import { ROUTES } from '../../routes/config';

export function LeadDetailPage() {
  const { id } = useParams<{ id: string }>();
  const leadId = parseInt(id ?? '0', 10);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [isEditing, setIsEditing] = useState(false);
  const [isConverting, setIsConverting] = useState(false);

  useEffect(() => { document.title = 'Lead Detail | CRM'; }, []);

  const { data: lead, isLoading, isError } = useQuery({
    queryKey: ['lead', leadId],
    queryFn: () => getLead(leadId),
    enabled: leadId > 0,
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteLead(leadId),
    onSuccess: () => navigate(ROUTES.LEADS),
  });

  useEffect(() => {
    if (lead) document.title = `${lead.first_name} ${lead.last_name} | CRM`;
  }, [lead]);

  if (isLoading) {
    return <div className="flex items-center justify-center h-64"><Loader2 className="h-6 w-6 animate-spin text-indigo-600" /></div>;
  }
  if (isError || !lead) {
    return <div className="p-4 text-red-600 text-sm">Lead not found.</div>;
  }

  const isConverted = !!lead.converted_opportunity_id;
  const canConvert = lead.status === 'qualified' && !isConverted;

  return (
    <div className="p-4 space-y-4 max-w-3xl">
      <div className="flex items-center gap-3">
        <Link to={ROUTES.LEADS} className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100">
          <ArrowLeft className="h-4 w-4" />
        </Link>
        <h1 className="text-base font-semibold text-slate-900">{lead.first_name} {lead.last_name}</h1>
      </div>

      <div className="bg-white rounded-xl border border-slate-100 p-5 space-y-4">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-xs text-slate-500">Email</p>
            <a href={`mailto:${lead.email}`} className="text-sm text-indigo-600 hover:underline">{lead.email}</a>
          </div>
          <div className="flex gap-2">
            <button onClick={() => setIsEditing(true)} className="px-3 py-1.5 text-sm border border-slate-300 rounded-lg hover:bg-slate-50 text-slate-600">Edit</button>
            {canConvert && (
              <button onClick={() => setIsConverting(true)} className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">Convert</button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          {[
            ['Phone', lead.phone ?? '—'],
            ['Company', lead.company ?? '—'],
            ['Source', lead.source ?? '—'],
            ['Created', new Date(lead.created_at).toLocaleDateString()],
          ].map(([label, value]) => (
            <div key={label}>
              <p className="text-xs text-slate-500 mb-0.5">{label}</p>
              <p className="text-slate-900">{value}</p>
            </div>
          ))}
        </div>

        {lead.notes && (
          <div>
            <p className="text-xs text-slate-500 mb-1">Notes</p>
            <p className="text-sm text-slate-700 whitespace-pre-wrap">{lead.notes}</p>
          </div>
        )}

        <div className="pt-2 border-t border-slate-100">
          <LeadStatusControl lead={lead} />
        </div>

        {isConverted && lead.converted_opportunity_id && (
          <div className="flex items-center gap-2 p-3 bg-indigo-50 rounded-lg border border-indigo-100">
            <span className="text-sm text-indigo-700 font-medium">Converted to Opportunity</span>
            <Link
              to={`/opportunities/${lead.converted_opportunity_id}`}
              className="inline-flex items-center gap-1 text-sm text-indigo-600 hover:underline ml-auto"
            >
              View Opportunity <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        )}

        <div className="pt-2 border-t border-slate-100 flex justify-end">
          <button
            onClick={() => deleteMutation.mutate()}
            disabled={deleteMutation.isPending}
            className="px-3 py-1.5 text-sm text-red-600 border border-red-200 rounded-lg hover:bg-red-50 disabled:opacity-50 flex items-center gap-1.5"
          >
            {deleteMutation.isPending && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
            Delete Lead
          </button>
        </div>
      </div>

      {isEditing && (
        <LeadForm
          lead={lead}
          onClose={() => setIsEditing(false)}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['lead', leadId] });
            setIsEditing(false);
          }}
        />
      )}

      {isConverting && (
        <LeadConvertModal
          leadId={leadId}
          leadName={`${lead.first_name} ${lead.last_name}`}
          onClose={() => setIsConverting(false)}
        />
      )}
    </div>
  );
}
