import { useQuery } from '@tanstack/react-query';
import { Phone, Mail, Calendar, Activity, Loader2 } from 'lucide-react';
import { listActivities } from '../activities/api';
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

interface ContactHistoryTabProps {
  contactId: number;
}

export function ContactHistoryTab({ contactId }: ContactHistoryTabProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['activities', { contact_id: contactId }],
    queryFn: () => listActivities({ contact_id: contactId, limit: 50 }),
  });

  const activities = data?.data ?? [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-5 w-5 animate-spin text-indigo-500" />
      </div>
    );
  }

  if (activities.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-slate-500">
        <Activity className="h-10 w-10 text-slate-300 mb-3" />
        <p className="text-sm font-medium">No activity history yet</p>
        <p className="text-xs mt-1 text-slate-400">Log a call, email, or meeting to track engagement.</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-slate-100">
      {activities.map((a) => (
        <div key={a.id} className="flex items-start gap-3 py-3 px-1">
          <div className={`flex-shrink-0 p-1.5 rounded-md mt-0.5 ${TYPE_COLORS[a.type]}`}>
            {TYPE_ICONS[a.type]}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-900">{a.subject}</p>
            {a.notes && <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">{a.notes}</p>}
            <p className="text-xs text-slate-400 mt-1">
              {new Date(a.activity_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
