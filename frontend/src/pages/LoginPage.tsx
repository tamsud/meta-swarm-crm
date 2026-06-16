import { useEffect, useState } from 'react';
import { BarChart3, CheckCircle } from 'lucide-react';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  useEffect(() => {
    document.title = 'Sign in | CRM';
  }, []);

  return (
    <div className="flex min-h-screen">
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-indigo-900 to-indigo-800 p-12 flex-col justify-between">
        <div className="flex items-center gap-3">
          <BarChart3 className="h-8 w-8 text-white" />
          <span className="text-white font-bold text-2xl">Sales CRM</span>
        </div>

        <div className="space-y-6">
          <h1 className="text-4xl font-bold text-white leading-tight">
            Manage your sales pipeline with confidence
          </h1>
          <p className="text-indigo-200 text-lg">
            Track leads, close deals, and grow your business with our powerful CRM platform.
          </p>

          <div className="space-y-4 pt-4">
            <div className="flex items-center gap-3 text-indigo-100">
              <CheckCircle className="h-5 w-5 text-indigo-300" />
              <span>Lead and contact management</span>
            </div>
            <div className="flex items-center gap-3 text-indigo-100">
              <CheckCircle className="h-5 w-5 text-indigo-300" />
              <span>Visual sales pipeline</span>
            </div>
            <div className="flex items-center gap-3 text-indigo-100">
              <CheckCircle className="h-5 w-5 text-indigo-300" />
              <span>Activity tracking and reminders</span>
            </div>
          </div>
        </div>

        <div className="text-indigo-300 text-sm">
          © 2026 Sales CRM. All rights reserved.
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-8 bg-white">
        <div className="w-full max-w-md space-y-8">
          <div className="lg:hidden flex items-center gap-3 justify-center mb-8">
            <BarChart3 className="h-8 w-8 text-indigo-600" />
            <span className="text-indigo-900 font-bold text-2xl">Sales CRM</span>
          </div>

          <div className="text-center">
            <h2 className="text-2xl font-bold text-slate-900">Welcome back</h2>
            <p className="text-slate-500 mt-2">Sign in to your account to continue</p>
          </div>

          <form className="space-y-6" onSubmit={(e) => e.preventDefault()}>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-1">
                Email address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-700 mb-1">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled
              className="w-full py-2 px-4 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Sign in
            </button>
          </form>

          <div className="border-t border-slate-200 pt-6">
            <p className="text-sm text-slate-600 text-center mb-3">Demo accounts:</p>
            <div className="space-y-2 text-sm text-slate-500">
              <p><strong>Admin:</strong> admin@crm.local / admin123</p>
              <p><strong>Manager:</strong> manager@crm.local / manager123</p>
              <p><strong>Sales Rep:</strong> rep@crm.local / rep123</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
