import { Activity } from 'lucide-react';

interface OpportunityActivityListProps {
  opportunityId: number;
}

export function OpportunityActivityList({ opportunityId: _opportunityId }: OpportunityActivityListProps) {
  return (
    <div className="flex flex-col items-center justify-center py-8 text-slate-500">
      <Activity className="h-10 w-10 text-slate-300 mb-3" />
      <p className="text-sm font-medium">Activities</p>
      <p className="text-xs mt-1 text-center max-w-xs">
        Activities will appear here once the Activities module is complete.
      </p>
    </div>
  );
}
