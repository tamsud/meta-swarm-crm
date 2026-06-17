import { Link } from 'react-router-dom';
import { Phone, Mail, Calendar, ChevronLeft, ChevronRight } from 'lucide-react';
import type { PaginatedActivities, ActivityType } from '../types';

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

function relativeTime(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime();
  const days = Math.floor(diff / (1000 * 86400));
  if (days === 0) return 'Today';
  if (days === 1) return 'Yesterday';
  if (days < 7) return `${days}d ago`;
  const weeks = Math.floor(days / 7);
  return `${weeks}w ago`;
}

interface RecentActivityFeedProps {
  activities: PaginatedActivities;
  page: number;
  onPageChange: (page: number) => void;
}

export function RecentActivityFeed({ activities, page, onPageChange }: RecentActivityFeedProps) {
  return (
    <div className="bg-white rounded-xl border border-slate-100 p-4">
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Recent Activities</p>
        <Link to="/activities" className="text-xs text-indigo-600 hover:underline">View all</Link>
      </div>

      {activities.items.length === 0 ? (
        <p className="text-sm text-slate-400 py-4 text-center">No activities yet.</p>
      ) : (
        <div className="space-y-2">
          {activities.items.map((a) => (
            <div key={a.id} className="flex items-start gap-2.5">
              <div className={`flex-shrink-0 p-1.5 rounded-md mt-0.5 ${TYPE_COLORS[a.type]}`}>
                {TYPE_ICONS[a.type]}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-800 truncate">{a.subject}</p>
                <p className="text-xs text-slate-500 truncate">
                  {a.contact_name ?? a.opportunity_title ?? '—'}
                </p>
              </div>
              <span className="flex-shrink-0 text-xs text-slate-400">{relativeTime(a.activity_date)}</span>
            </div>
          ))}
        </div>
      )}

      {activities.total_pages > 1 && (
        <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100">
          <button
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1}
            className="p-1 rounded text-slate-400 hover:text-slate-600 disabled:opacity-40"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <span className="text-xs text-slate-500">Page {page} of {activities.total_pages}</span>
          <button
            onClick={() => onPageChange(page + 1)}
            disabled={page >= activities.total_pages}
            className="p-1 rounded text-slate-400 hover:text-slate-600 disabled:opacity-40"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
}
