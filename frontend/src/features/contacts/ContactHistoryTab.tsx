import { Activity } from 'lucide-react';

interface ContactHistoryTabProps {
  contactId: number;
}

export function ContactHistoryTab({ contactId: _contactId }: ContactHistoryTabProps) {
  return (
    <div className="flex flex-col items-center justify-center py-8 text-slate-500">
      <Activity className="h-10 w-10 text-slate-300 mb-3" />
      <p className="text-sm font-medium">Coming soon</p>
      <p className="text-xs mt-1">Activities module will display interaction history here</p>
    </div>
  );
}
