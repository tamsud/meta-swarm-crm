import { Menu, ChevronDown } from 'lucide-react';

interface TopBarProps {
  onMobileMenuClick: () => void;
}

export function TopBar({ onMobileMenuClick }: TopBarProps) {
  const user = { email: 'admin@crm.local' };
  const initial = user.email.charAt(0).toUpperCase();

  return (
    <header className="h-12 bg-white border-b border-slate-100 shadow-xs flex items-center justify-between px-4">
      <button
        type="button"
        className="md:hidden p-2 -ml-2 text-slate-600 hover:text-slate-900"
        onClick={onMobileMenuClick}
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5" />
      </button>

      <div className="flex-1" />

      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-sm font-medium">
          {initial}
        </div>
        <span className="hidden sm:block text-sm text-slate-700">{user.email}</span>
        <ChevronDown className="h-4 w-4 text-slate-400" />
      </div>
    </header>
  );
}
