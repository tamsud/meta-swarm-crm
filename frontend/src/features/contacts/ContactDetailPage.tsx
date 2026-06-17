import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Loader2, Users, Pencil, Mail, Phone, Briefcase, Building2, User, Clock } from 'lucide-react';
import { getContact } from './api';
import { ContactForm } from './ContactForm';
import { ContactHistoryTab } from './ContactHistoryTab';
import { ContactEmailsTab } from './ContactEmailsTab';
import { listActivities } from '../activities/api';
import { ROUTES } from '../../routes/config';

type TabKey = 'overview' | 'history' | 'emails';

export function ContactDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabKey>('overview');
  const [isFormOpen, setIsFormOpen] = useState(false);

  const contactId = id ? parseInt(id, 10) : NaN;

  useEffect(() => {
    document.title = 'Contact | CRM';
  }, []);

  const { data: contact, isLoading, isError, error } = useQuery({
    queryKey: ['contact', contactId],
    queryFn: () => getContact(contactId),
    enabled: !isNaN(contactId),
  });

  const { data: recentActivityData } = useQuery({
    queryKey: ['activities', { contact_id: contactId, limit: 1 }],
    queryFn: () => listActivities({ contact_id: contactId, limit: 1 }),
    enabled: !isNaN(contactId),
  });

  const daysSinceLastContact = (() => {
    const latest = recentActivityData?.data?.[0];
    if (!latest) return null;
    return Math.floor((Date.now() - new Date(latest.activity_date).getTime()) / (1000 * 86400));
  })();

  useEffect(() => {
    if (contact) {
      document.title = `${contact.first_name} ${contact.last_name} | CRM`;
    }
  }, [contact]);

  const handleFormClose = () => {
    setIsFormOpen(false);
  };

  const handleFormSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['contact', contactId] });
    queryClient.invalidateQueries({ queryKey: ['contacts'] });
    setIsFormOpen(false);
  };

  if (isNaN(contactId)) {
    return (
      <div className="p-4">
        <div className="bg-white rounded-xl shadow-card border border-slate-100 p-8 text-center">
          <Users className="h-12 w-12 text-slate-300 mx-auto mb-3" />
          <h2 className="text-lg font-semibold text-slate-900 mb-2">Invalid Contact ID</h2>
          <p className="text-slate-500 mb-4">The contact ID provided is not valid.</p>
          <Link
            to={ROUTES.CONTACTS}
            className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-800"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Contacts
          </Link>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="p-4">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-indigo-600" />
        </div>
      </div>
    );
  }

  if (isError) {
    const axiosError = error as { response?: { status?: number } };
    const is404 = axiosError.response?.status === 404;

    return (
      <div className="p-4">
        <div className="bg-white rounded-xl shadow-card border border-slate-100 p-8 text-center">
          <Users className="h-12 w-12 text-slate-300 mx-auto mb-3" />
          <h2 className="text-lg font-semibold text-slate-900 mb-2">
            {is404 ? 'Contact Not Found' : 'Error Loading Contact'}
          </h2>
          <p className="text-slate-500 mb-4">
            {is404
              ? 'The contact you are looking for does not exist.'
              : (error as Error).message}
          </p>
          <Link
            to={ROUTES.CONTACTS}
            className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-800"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Contacts
          </Link>
        </div>
      </div>
    );
  }

  if (!contact) {
    return null;
  }

  const tabs: { key: TabKey; label: string }[] = [
    { key: 'overview', label: 'Overview' },
    { key: 'history', label: 'History' },
    { key: 'emails', label: 'Emails' },
  ];

  // Build header text
  const headerText = contact.account
    ? `${contact.first_name} ${contact.last_name}, ${contact.account.name}`
    : `${contact.first_name} ${contact.last_name}`;

  return (
    <div className="p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate(ROUTES.CONTACTS)}
          className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          title="Back to Contacts"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div className="flex-1">
          <h1 className="text-lg font-semibold text-slate-900">{headerText}</h1>
          {contact.job_title && (
            <p className="text-sm text-slate-500">{contact.job_title}</p>
          )}
        </div>
        <button
          onClick={() => setIsFormOpen(true)}
          className="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 active:bg-indigo-800 transition-colors shadow-xs"
        >
          <Pencil className="h-4 w-4" />
          Edit
        </button>
      </div>

      {/* Profile Sidebar Card */}
      <div className="bg-white rounded-xl shadow-card border border-slate-100 p-4">
        <div className="flex items-start gap-4">
          {/* Avatar Placeholder */}
          <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0">
            <User className="w-8 h-8 text-indigo-600" />
          </div>

          {/* Contact Info */}
          <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4">
            <InfoItem icon={Briefcase} label="Job Title" value={contact.job_title} />
            <InfoItem
              icon={Mail}
              label="Email"
              value={contact.email}
              href={`mailto:${contact.email}`}
            />
            <InfoItem
              icon={Phone}
              label="Phone"
              value={contact.phone}
              href={contact.phone ? `tel:${contact.phone}` : undefined}
            />
            <InfoItem
              icon={Building2}
              label="Account"
              value={contact.account?.name || null}
              linkTo={contact.account ? `${ROUTES.ACCOUNTS}/${contact.account.id}` : undefined}
            />
            <InfoItem
              icon={Clock}
              label="Last Contact"
              value={daysSinceLastContact === null ? 'Never contacted' : daysSinceLastContact === 0 ? 'Today' : `${daysSinceLastContact} day${daysSinceLastContact === 1 ? '' : 's'} ago`}
            />
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-card border border-slate-100 overflow-hidden">
        <div className="border-b border-slate-100">
          <nav className="flex" role="tablist">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                role="tab"
                aria-selected={activeTab === tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.key
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-4">
          {activeTab === 'overview' && <ContactOverviewTab contact={contact} />}
          {activeTab === 'history' && <ContactHistoryTab contactId={contactId} />}
          {activeTab === 'emails' && <ContactEmailsTab contactId={contactId} />}
        </div>
      </div>

      {/* Contact Form Modal */}
      {isFormOpen && (
        <ContactForm
          contact={contact}
          onClose={handleFormClose}
          onSuccess={handleFormSuccess}
        />
      )}
    </div>
  );
}

interface InfoItemProps {
  icon: typeof Users;
  label: string;
  value: string | null;
  href?: string;
  linkTo?: string;
}

function InfoItem({ icon: Icon, label, value, href, linkTo }: InfoItemProps) {
  return (
    <div className="flex items-start gap-3">
      <div className="p-2 bg-slate-50 rounded-lg">
        <Icon className="h-4 w-4 text-slate-500" />
      </div>
      <div>
        <p className="text-xs text-slate-500 uppercase tracking-wider">{label}</p>
        {linkTo && value ? (
          <Link to={linkTo} className="text-sm text-indigo-600 hover:underline">
            {value}
          </Link>
        ) : href && value ? (
          <a href={href} className="text-sm text-indigo-600 hover:underline">
            {value}
          </a>
        ) : (
          <p className="text-sm text-slate-900">{value || '—'}</p>
        )}
      </div>
    </div>
  );
}

interface ContactOverviewTabProps {
  contact: {
    first_name: string;
    last_name: string;
    email: string;
    phone: string | null;
    job_title: string | null;
    account: { id: number; name: string } | null;
    created_at: string;
    updated_at: string;
  };
}

function ContactOverviewTab({ contact }: ContactOverviewTabProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Full Name</p>
          <p className="text-sm text-slate-900">{contact.first_name} {contact.last_name}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Email</p>
          <a href={`mailto:${contact.email}`} className="text-sm text-indigo-600 hover:underline">
            {contact.email}
          </a>
        </div>
        <div>
          <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Phone</p>
          {contact.phone ? (
            <a href={`tel:${contact.phone}`} className="text-sm text-indigo-600 hover:underline">
              {contact.phone}
            </a>
          ) : (
            <p className="text-sm text-slate-500">—</p>
          )}
        </div>
        <div>
          <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Job Title</p>
          <p className="text-sm text-slate-900">{contact.job_title || '—'}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Account</p>
          {contact.account ? (
            <Link
              to={`${ROUTES.ACCOUNTS}/${contact.account.id}`}
              className="text-sm text-indigo-600 hover:underline"
            >
              {contact.account.name}
            </Link>
          ) : (
            <p className="text-sm text-slate-500">—</p>
          )}
        </div>
        <div>
          <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Created</p>
          <p className="text-sm text-slate-900">{formatDate(contact.created_at)}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Last Updated</p>
          <p className="text-sm text-slate-900">{formatDate(contact.updated_at)}</p>
        </div>
      </div>
    </div>
  );
}
