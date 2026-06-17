import { useState, useEffect } from 'react';
import { Loader2, RefreshCw } from 'lucide-react';
import { useDashboardSummary } from '../features/dashboard/api';
import { KpiGrid } from '../features/dashboard/components/KpiGrid';
import { PipelineBarChart } from '../features/dashboard/components/PipelineBarChart';
import { ClosedDealsPanel } from '../features/dashboard/components/ClosedDealsPanel';
import { RecentActivityFeed } from '../features/dashboard/components/RecentActivityFeed';

export function DashboardPage() {
  const [activityPage, setActivityPage] = useState(1);

  useEffect(() => { document.title = 'Dashboard | CRM'; }, []);

  const { data, isLoading, isError, refetch } = useDashboardSummary(activityPage);

  if (isLoading) {
    return (
      <div className="p-4 space-y-3">
        <div className="px-1 pb-1">
          <h1 className="text-base font-semibold text-slate-900 tracking-tight">Dashboard</h1>
        </div>
        <div className="flex items-center justify-center py-24">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
        </div>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="p-4 space-y-3">
        <div className="px-1 pb-1">
          <h1 className="text-base font-semibold text-slate-900 tracking-tight">Dashboard</h1>
        </div>
        <div className="bg-white rounded-xl border border-slate-100 p-8 flex flex-col items-center gap-3">
          <p className="text-sm text-slate-500">Failed to load dashboard data.</p>
          <button
            onClick={() => refetch()}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm border border-slate-300 rounded-lg hover:bg-slate-50 text-slate-600"
          >
            <RefreshCw className="h-4 w-4" /> Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      <div className="px-1 pb-1">
        <h1 className="text-base font-semibold text-slate-900 tracking-tight">Dashboard</h1>
      </div>

      <KpiGrid kpis={data.kpis} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <PipelineBarChart stages={data.stage_breakdown} />
        <ClosedDealsPanel closed={data.closed} />
      </div>

      <RecentActivityFeed
        activities={data.recent_activities}
        page={activityPage}
        onPageChange={setActivityPage}
      />
    </div>
  );
}
