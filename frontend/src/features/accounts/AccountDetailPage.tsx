import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Loader2, Building2, Pencil, Globe, Phone, MapPin, Briefcase } from 'lucide-react';
import { getAccount } from './api';
import { AccountForm } from './AccountForm';
import { AccountContactsTab } from './AccountContactsTab';
import { AccountOpportunitiesTab } from './AccountOpportunitiesTab';
import { ROUTES } from '../../routes/config';

type TabKey = 'contacts' | 'opportunities';

export function AccountDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabKey>('contacts');
  const [isFormOpen, setIsFormOpen] = useState(false);

  const accountId = id ? parseInt(id, 10) : NaN;

  useEffect(() => {
    document.title = 'Account | CRM';
  }, []);

  const { data: account, isLoading, isError, error } = useQuery({
    queryKey: ['account', accountId],
    queryFn: () => getAccount(accountId),
    enabled: !isNaN(accountId),
  });

  useEffect(() => {
    if (account) {
      document.title = `${account.name} | CRM`;
    }
  }, [account]);

  const handleFormClose = () => {
    setIsFormOpen(false);
  };

  const handleFormSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['account', accountId] });
    queryClient.invalidateQueries({ queryKey: ['accounts'] });
    setIsFormOpen(false);
  };

  if (isNaN(accountId)) {
    return (
      <div className="p-4">
        <div className="bg-white rounded-xl shadow-card border border-slate-100 p-8 text-center">
          <Building2 className="h-12 w-12 text-slate-300 mx-auto mb-3" />
          <h2 className="text-lg font-semibold text-slate-900 mb-2">Invalid Account ID</h2>
          <p className="text-slate-500 mb-4">The account ID provided is not valid.</p>
          <Link
            to={ROUTES.ACCOUNTS}
            className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-800"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Accounts
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
          <Building2 className="h-12 w-12 text-slate-300 mx-auto mb-3" />
          <h2 className="text-lg font-semibold text-slate-900 mb-2">
            {is404 ? 'Account Not Found' : 'Error Loading Account'}
          </h2>
          <p className="text-slate-500 mb-4">
            {is404
              ? 'The account you are looking for does not exist.'
              : (error as Error).message}
          </p>
          <Link
            to={ROUTES.ACCOUNTS}
            className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-800"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Accounts
          </Link>
        </div>
      </div>
    );
  }

  if (!account) {
    return null;
  }

  const tabs: { key: TabKey; label: string }[] = [
    { key: 'contacts', label: 'Contacts' },
    { key: 'opportunities', label: 'Opportunities' },
  ];

  return (
    <div className="p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate(ROUTES.ACCOUNTS)}
          className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          title="Back to Accounts"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div className="flex-1">
          <h1 className="text-lg font-semibold text-slate-900">{account.name}</h1>
          {account.industry && (
            <p className="text-sm text-slate-500">{account.industry}</p>
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

      {/* Account Info Card */}
      <div className="bg-white rounded-xl shadow-card border border-slate-100 p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <InfoItem icon={Briefcase} label="Industry" value={account.industry} />
          <InfoItem
            icon={Globe}
            label="Website"
            value={account.website}
            href={account.website || undefined}
          />
          <InfoItem icon={Phone} label="Phone" value={account.phone} />
          <InfoItem icon={MapPin} label="Address" value={account.address} />
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
          {activeTab === 'contacts' && <AccountContactsTab accountId={accountId} />}
          {activeTab === 'opportunities' && <AccountOpportunitiesTab accountId={accountId} />}
        </div>
      </div>

      {/* Account Form Modal */}
      {isFormOpen && (
        <AccountForm
          account={account}
          onClose={handleFormClose}
          onSuccess={handleFormSuccess}
        />
      )}
    </div>
  );
}

interface InfoItemProps {
  icon: typeof Building2;
  label: string;
  value: string | null;
  href?: string;
}

function InfoItem({ icon: Icon, label, value, href }: InfoItemProps) {
  return (
    <div className="flex items-start gap-3">
      <div className="p-2 bg-slate-50 rounded-lg">
        <Icon className="h-4 w-4 text-slate-500" />
      </div>
      <div>
        <p className="text-xs text-slate-500 uppercase tracking-wider">{label}</p>
        {href && value ? (
          <a
            href={href}
            target="_blank"
            rel="noreferrer"
            className="text-sm text-indigo-600 hover:underline"
          >
            {value}
          </a>
        ) : (
          <p className="text-sm text-slate-900">{value || '—'}</p>
        )}
      </div>
    </div>
  );
}
