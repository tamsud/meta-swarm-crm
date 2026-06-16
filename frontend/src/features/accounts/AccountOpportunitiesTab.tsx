import { TrendingUp } from 'lucide-react';

interface AccountOpportunitiesTabProps {
  accountId: number;
}

export function AccountOpportunitiesTab({ accountId: _accountId }: AccountOpportunitiesTabProps) {
  return (
    <div className="flex flex-col items-center justify-center py-8 text-slate-500">
      <TrendingUp className="h-10 w-10 text-slate-300 mb-3" />
      <p className="text-sm font-medium">Opportunities</p>
      <p className="text-xs mt-1">Coming soon</p>
    </div>
  );
}
