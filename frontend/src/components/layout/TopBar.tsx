import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Menu, ChevronDown, User, LogOut } from 'lucide-react';
import { useAuth } from '../../context/useAuth';
import { ROUTES } from '../../routes/config';

interface TopBarProps {
  onMobileMenuClick: () => void;
}

export function TopBar({ onMobileMenuClick }: TopBarProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const displayName = user?.display_name || user?.email || 'User';
  const initial = displayName.charAt(0).toUpperCase();

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    navigate(ROUTES.LOGIN);
  };

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

      <div className="relative" ref={menuRef}>
        <button
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="flex items-center gap-2 rounded-lg px-2 py-1.5 hover:bg-slate-100 transition-colors"
        >
          <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-sm font-medium">
            {initial}
          </div>
          <span className="hidden sm:block text-sm text-slate-700 max-w-[150px] truncate">
            {displayName}
          </span>
          <ChevronDown className={`h-4 w-4 text-slate-400 transition-transform ${isMenuOpen ? 'rotate-180' : ''}`} />
        </button>

        {isMenuOpen && (
          <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-slate-100 py-1 z-50">
            <Link
              to={ROUTES.PROFILE}
              onClick={() => setIsMenuOpen(false)}
              className="flex items-center gap-2 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
            >
              <User className="h-4 w-4" />
              Profile
            </Link>
            <div className="h-px bg-slate-100 my-1" />
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
            >
              <LogOut className="h-4 w-4" />
              Sign Out
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
