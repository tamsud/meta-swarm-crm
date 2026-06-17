import { Mail } from 'lucide-react';

interface ContactEmailsTabProps {
  contactId: number;
}

export function ContactEmailsTab({ contactId: _contactId }: ContactEmailsTabProps) {
  return (
    <div className="flex flex-col items-center justify-center py-8 text-slate-500">
      <Mail className="h-10 w-10 text-slate-300 mb-3" />
      <p className="text-sm font-medium">Coming soon</p>
      <p className="text-xs mt-1">Activities module will display email history here</p>
    </div>
  );
}
