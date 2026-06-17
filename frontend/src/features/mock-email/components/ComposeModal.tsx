import { useState } from 'react';
import { X, Loader2 } from 'lucide-react';
import type { MockEmailCreate } from '../types';

interface ComposeModalProps {
  onClose: () => void;
  onSubmit: (data: MockEmailCreate) => Promise<void>;
  isSubmitting: boolean;
}

export function ComposeModal({ onClose, onSubmit, isSubmitting }: ComposeModalProps) {
  const [toEmail, setToEmail] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [errors, setErrors] = useState<{ to_email?: string; subject?: string }>({});

  const validate = (): boolean => {
    const newErrors: { to_email?: string; subject?: string } = {};

    if (!toEmail.trim()) {
      newErrors.to_email = 'Recipient email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(toEmail)) {
      newErrors.to_email = 'Invalid email format';
    }

    if (!subject.trim()) {
      newErrors.subject = 'Subject is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    await onSubmit({
      to_email: toEmail.trim(),
      subject: subject.trim(),
      body: body.trim() || undefined,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-lg w-full max-w-lg mx-4">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h2 className="text-lg font-semibold text-slate-900">Compose Email</h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label htmlFor="to_email" className="block text-sm font-medium text-slate-700 mb-1">
              To Email <span className="text-red-500">*</span>
            </label>
            <input
              id="to_email"
              type="email"
              value={toEmail}
              onChange={(e) => setToEmail(e.target.value)}
              className={`w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                errors.to_email ? 'border-red-300' : 'border-slate-300'
              }`}
              placeholder="recipient@example.com"
            />
            {errors.to_email && (
              <p className="mt-1 text-xs text-red-600">{errors.to_email}</p>
            )}
          </div>

          <div>
            <label htmlFor="subject" className="block text-sm font-medium text-slate-700 mb-1">
              Subject <span className="text-red-500">*</span>
            </label>
            <input
              id="subject"
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className={`w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                errors.subject ? 'border-red-300' : 'border-slate-300'
              }`}
              placeholder="Email subject"
            />
            {errors.subject && (
              <p className="mt-1 text-xs text-red-600">{errors.subject}</p>
            )}
          </div>

          <div>
            <label htmlFor="body" className="block text-sm font-medium text-slate-700 mb-1">
              Body
            </label>
            <textarea
              id="body"
              value={body}
              onChange={(e) => setBody(e.target.value)}
              rows={5}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
              placeholder="Email body (optional)"
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
