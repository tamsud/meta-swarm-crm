import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Phone, Mail, Calendar, Loader2, Activity, Pencil, Trash2 } from 'lucide-react';
import { listActivities, deleteActivity } from './api';
import type { ActivityType, Activity as ActivityModel } from './types';
import { ActivityForm } from './ActivityForm';
import { useAuth } from '../../context/useAuth';

const TYPE_ICONS: Record<ActivityType, React.ReactNode> = {
  call: <Phone className="h-4 w-4" />,
  email: <Mail className="h-4 w-4" />,
  meeting: <Calendar className="h-4 w-4" />,
};

const TYPE_COLORS: Record<ActivityType, string> = {
  call: 'bg-blue-100 text-blue-700',
  email: 'bg-purple-100 text-purple-700',
  meeting: 'bg-green-100 text-green-700',
};

function formatRelativeDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 86400));
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function groupByDate(activities: ActivityModel[]): [string, ActivityModel[]][] {
  const groups = new Map<string, ActivityModel[]>();
  for (const a of activities) {
    const key = new Date(a.activity_date).toLocaleDateString('en-US', {
      weekday: 'long', month: 'long', day: 'numeric', year: 'numeric',
    });
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(a);
  }
  return Array.from(groups.entries());
}

export function ActivitiesPage() {
  const queryClient = useQueryClient();
  const { hasPermission } = useAuth();
  const [typeFilter, setTypeFilter] = useState<ActivityType | undefined>();
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingActivity, setEditingActivity] = useState<ActivityModel | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<ActivityModel | null>(null);

  useEffect(() => { document.title = 'Activities | CRM'; }, []);

  const { data, isLoading, isError } = useQuery({
    queryKey: ['activities', { type: typeFilter }],
    queryFn: () => listActivities({ type: typeFilter, limit: 100 }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteActivity,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['activities'] });
      setDeleteConfirm(null);
    },
  });

  const activities = data?.data ?? [];
  const groups = groupByDate(activities);
  const canManage = hasPermission('activities:manage-own');

  return (
    <div className="p-4 space-y-3">
      <div className="px-1 pb-1 flex items-center justify-between">
        <h1 className="text-base font-semibold text-slate-900 tracking-tight">Activities</h1>
        {canManage && (
          <button
            onClick={() => { setEditingActivity(null); setIsFormOpen(true); }}
            className="inline-flex items-center gap-1 rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors shadow-xs"
          >
            <Plus className="h-4 w-4" />
            Log Activity
          </button>
        )}
      </div>

      {/* Filter chips */}
      <div className="flex items-center gap-2">
        {(['all', 'call', 'email', 'meeting'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTypeFilter(t === 'all' ? undefined : t as ActivityType)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
              (t === 'all' && !typeFilter) || t === typeFilter
                ? 'bg-indigo-600 text-white'
                : 'bg-white border border-slate-300 text-slate-600 hover:bg-slate-50'
            }`}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      <div className="space-y-4">
        {isLoading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-6 w-6 animate-spin text-indigo-600" />
          </div>
        ) : isError ? (
          <div className="bg-white rounded-xl border border-slate-100 p-8 text-center text-red-600 text-sm">
            Failed to load activities.
          </div>
        ) : activities.length === 0 ? (
          <div className="bg-white rounded-xl border border-slate-100 p-12 flex flex-col items-center text-slate-500">
            <Activity className="h-12 w-12 text-slate-300 mb-3" />
            <p className="text-sm font-medium">No activities yet</p>
            <p className="text-xs mt-1">Log a call, email, or meeting to get started.</p>
          </div>
        ) : (
          groups.map(([date, items]) => (
            <div key={date} className="space-y-2">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-1">{date}</p>
              <div className="bg-white rounded-xl border border-slate-100 divide-y divide-slate-100">
                {items.map((activity) => (
                  <div key={activity.id} className="px-4 py-3 flex items-start gap-3 hover:bg-slate-50 transition-colors">
                    <div className={`mt-0.5 flex-shrink-0 p-1.5 rounded-lg ${TYPE_COLORS[activity.type]}`}>
                      {TYPE_ICONS[activity.type]}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900">{activity.subject}</p>
                      {activity.notes && (
                        <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">{activity.notes}</p>
                      )}
                      <p className="text-xs text-slate-400 mt-1">{formatRelativeDate(activity.activity_date)}</p>
                    </div>
                    {canManage && (
                      <div className="flex items-center gap-1 flex-shrink-0">
                        <button
                          onClick={() => { setEditingActivity(activity); setIsFormOpen(true); }}
                          className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100"
                        >
                          <Pencil className="h-3.5 w-3.5" />
                        </button>
                        <button
                          onClick={() => setDeleteConfirm(activity)}
                          className="p-1.5 rounded-md text-slate-400 hover:text-red-600 hover:bg-red-50"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>

      {isFormOpen && (
        <ActivityForm
          activity={editingActivity}
          onClose={() => { setIsFormOpen(false); setEditingActivity(null); }}
          onSuccess={() => { setIsFormOpen(false); setEditingActivity(null); }}
        />
      )}

      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50" onClick={() => setDeleteConfirm(null)} />
          <div className="relative bg-white rounded-xl shadow-lg p-6 max-w-sm w-full mx-4">
            <h3 className="text-base font-semibold text-slate-900 mb-2">Delete Activity</h3>
            <p className="text-sm text-slate-600 mb-4">
              Delete "{deleteConfirm.subject}"? This cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button onClick={() => setDeleteConfirm(null)} className="px-4 py-2 text-sm text-slate-700 hover:bg-slate-100 rounded-lg">Cancel</button>
              <button
                onClick={() => deleteMutation.mutate(deleteConfirm.id)}
                disabled={deleteMutation.isPending}
                className="px-4 py-2 text-sm text-white bg-red-600 hover:bg-red-700 rounded-lg disabled:opacity-50 flex items-center gap-2"
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
