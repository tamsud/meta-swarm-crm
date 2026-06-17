import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Phone, Mail, Calendar, Activity, Loader2, Plus } from 'lucide-react';
import { listActivities } from '../activities/api';
import { ActivityForm } from '../activities/ActivityForm';
import type { ActivityType } from '../activities/types';

const TYPE_ICONS: Record<ActivityType, React.ReactNode> = {
  call: <Phone className="h-3.5 w-3.5" />,
  email: <Mail className="h-3.5 w-3.5" />,
  meeting: <Calendar className="h-3.5 w-3.5" />,
};

const TYPE_COLORS: Record<ActivityType, string> = {
  call: 'bg-blue-100 text-blue-600',
  email: 'bg-purple-100 text-purple-600',
  meeting: 'bg-green-100 text-green-600',
};

interface OpportunityActivityListProps {
  opportunityId: number;
}

export function OpportunityActivityList({ opportunityId }: OpportunityActivityListProps) {
  const queryClient = useQueryClient();
  const [isFormOpen, setIsFormOpen] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['activities', { opportunity_id: opportunityId }],
    queryFn: () => listActivities({ opportunity_id: opportunityId, limit: 50 }),
  });

  const activities = data?.data ?? [];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-slate-700">Activities</p>
        <button
          onClick={() => setIsFormOpen(true)}
          className="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-lg hover:bg-indigo-100 transition-colors"
        >
          <Plus className="h-3.5 w-3.5" /> Log Activity
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-6">
          <Loader2 className="h-5 w-5 animate-spin text-indigo-500" />
        </div>
      ) : activities.length === 0 ? (
        <div className="flex flex-col items-center py-6 text-slate-400">
          <Activity className="h-8 w-8 text-slate-300 mb-2" />
          <p className="text-xs">No activities logged yet.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {activities.map((a) => (
            <div key={a.id} className="flex items-start gap-2.5 py-2 border-b border-slate-100 last:border-0">
              <div className={`flex-shrink-0 p-1.5 rounded-md mt-0.5 ${TYPE_COLORS[a.type]}`}>
                {TYPE_ICONS[a.type]}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-900">{a.subject}</p>
                {a.notes && <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">{a.notes}</p>}
                <p className="text-xs text-slate-400 mt-0.5">
                  {new Date(a.activity_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {isFormOpen && (
        <ActivityForm
          prefillOpportunityId={opportunityId}
          onClose={() => setIsFormOpen(false)}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['activities', { opportunity_id: opportunityId }] });
            setIsFormOpen(false);
          }}
        />
      )}
    </div>
  );
}
