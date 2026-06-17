import { useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Loader2, Mail, AlertCircle } from 'lucide-react';
import { getMockEmail } from '../../features/mock-email/api';
import { ROUTES } from '../../routes/config';

function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
}

export function MockEmailDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const {
    data: email,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['mock-email', id],
    queryFn: () => getMockEmail(id!),
    enabled: !!id,
  });

  useEffect(() => {
    if (email) {
      document.title = `${email.subject} | Mail Inbox | CRM`;
    } else {
      document.title = 'Mail Inbox | CRM';
    }
  }, [email]);

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
    const is404 =
      (error as { response?: { status?: number } })?.response?.status === 404;

    return (
      <div className="p-4 space-y-3">
        <div className="px-1 pb-1">
          <Link
            to={ROUTES.ADMIN_MOCK_EMAIL}
            className="inline-flex items-center gap-1.5 text-sm text-slate-600 hover:text-slate-800 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Inbox
          </Link>
        </div>
        <div className="bg-white rounded-xl shadow-card border border-slate-100 p-8">
          <div className="flex flex-col items-center justify-center text-center">
            <AlertCircle className="h-12 w-12 text-red-400 mb-3" />
            <h2 className="text-lg font-semibold text-slate-900 mb-1">
              {is404 ? 'Email Not Found' : 'Error Loading Email'}
            </h2>
            <p className="text-slate-500 text-sm mb-4">
              {is404
                ? 'This email may have been deleted or does not exist.'
                : (error as Error).message}
            </p>
            <button
              onClick={() => navigate(ROUTES.ADMIN_MOCK_EMAIL)}
              className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors"
            >
              Return to Inbox
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!email) return null;

  return (
    <div className="p-4 space-y-3">
      <div className="px-1 pb-1">
        <Link
          to={ROUTES.ADMIN_MOCK_EMAIL}
          className="inline-flex items-center gap-1.5 text-sm text-slate-600 hover:text-slate-800 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Inbox
        </Link>
      </div>

      <div className="bg-white rounded-xl shadow-card border border-slate-100 overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                <Mail className="h-5 w-5 text-indigo-600" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-slate-900">{email.subject}</h1>
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1 text-sm text-slate-600">
                  <span>
                    <span className="text-slate-400">From:</span> {email.from_email}
                  </span>
                  <span>
                    <span className="text-slate-400">To:</span> {email.to_email}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex flex-col items-end gap-1">
              <span className="text-xs text-slate-400">{formatDateTime(email.created_at)}</span>
              {email.status === 'unread' ? (
                <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-indigo-50 text-indigo-600 ring-1 ring-inset ring-indigo-200">
                  Unread
                </span>
              ) : (
                <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-slate-100 text-slate-600 ring-1 ring-inset ring-slate-200">
                  Read
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="px-6 py-5">
          {email.body ? (
            <div className="prose prose-sm prose-slate max-w-none">
              <p className="whitespace-pre-wrap text-slate-700 leading-relaxed">{email.body}</p>
            </div>
          ) : (
            <p className="text-slate-400 italic text-sm">No message body</p>
          )}
        </div>
      </div>
    </div>
  );
}
