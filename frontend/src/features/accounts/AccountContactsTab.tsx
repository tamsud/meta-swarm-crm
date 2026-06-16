import { Users } from 'lucide-react';

interface AccountContactsTabProps {
  accountId: number;
}

export function AccountContactsTab({ accountId: _accountId }: AccountContactsTabProps) {
  return (
    <div className="flex flex-col items-center justify-center py-8 text-slate-500">
      <Users className="h-10 w-10 text-slate-300 mb-3" />
      <p className="text-sm font-medium">Contacts</p>
      <p className="text-xs mt-1">Coming soon</p>
    </div>
  );
}
