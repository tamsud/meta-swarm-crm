import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Users, Plus, Loader2, Mail, Phone, Briefcase } from 'lucide-react';
import { listContacts } from '../contacts/api';
import { ContactForm } from '../contacts/ContactForm';
import { ROUTES } from '../../routes/config';

interface AccountContactsTabProps {
  accountId: number;
}

export function AccountContactsTab({ accountId }: AccountContactsTabProps) {
  const queryClient = useQueryClient();
  const [isFormOpen, setIsFormOpen] = useState(false);

  const { data, isLoading, isError } = useQuery({
    queryKey: ['contacts', { account_id: accountId }],
    queryFn: () => listContacts({ account_id: accountId, limit: 100 }),
  });

  const handleFormSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['contacts', { account_id: accountId }] });
    setIsFormOpen(false);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin text-indigo-600" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex items-center justify-center py-12 text-red-600">
        Failed to load contacts
      </div>
    );
  }

  const contacts = data?.data || [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">{contacts.length} contact{contacts.length !== 1 ? 's' : ''}</p>
        <button
          onClick={() => setIsFormOpen(true)}
          className="inline-flex items-center gap-1 rounded-md bg-indigo-600 px-2.5 py-1.5 text-xs font-medium text-white hover:bg-indigo-700 transition-colors"
        >
          <Plus className="h-3 w-3" />
          Add Contact
        </button>
      </div>

      {contacts.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8 text-slate-500">
          <Users className="h-10 w-10 text-slate-300 mb-3" />
          <p className="text-sm font-medium">No contacts yet</p>
          <p className="text-xs mt-1">Add contacts to this account</p>
        </div>
      ) : (
        <div className="divide-y divide-slate-100">
          {contacts.map((contact) => (
            <Link
              key={contact.id}
              to={ROUTES.CONTACT_DETAIL.replace(':id', String(contact.id))}
              className="flex items-center gap-4 py-3 px-2 -mx-2 rounded-lg hover:bg-slate-50 transition-colors"
            >
              <div className="flex-shrink-0 h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                <span className="text-sm font-medium text-indigo-600">
                  {contact.first_name[0]}{contact.last_name[0]}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-900 truncate">
                  {contact.first_name} {contact.last_name}
                </p>
                <div className="flex items-center gap-3 mt-0.5">
                  {contact.job_title && (
                    <span className="flex items-center gap-1 text-xs text-slate-500">
                      <Briefcase className="h-3 w-3" />
                      {contact.job_title}
                    </span>
                  )}
                  {contact.email && (
                    <span className="flex items-center gap-1 text-xs text-slate-500">
                      <Mail className="h-3 w-3" />
                      {contact.email}
                    </span>
                  )}
                  {contact.phone && (
                    <span className="flex items-center gap-1 text-xs text-slate-500">
                      <Phone className="h-3 w-3" />
                      {contact.phone}
                    </span>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {isFormOpen && (
        <ContactForm
          defaultAccountId={accountId}
          onClose={() => setIsFormOpen(false)}
          onSuccess={handleFormSuccess}
        />
      )}
    </div>
  );
}
