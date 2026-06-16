import { Link, useLocation } from 'react-router-dom';
import clsx from 'clsx';
import type { LucideIcon } from 'lucide-react';

interface NavItemProps {
  path: string;
  label: string;
  icon: LucideIcon;
  collapsed?: boolean;
}

export function NavItem({ path, label, icon: Icon, collapsed }: NavItemProps) {
  const location = useLocation();
  const isActive = location.pathname === path;

  return (
    <Link
      to={path}
      aria-current={isActive ? 'page' : undefined}
      className={clsx(
        'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
        isActive
          ? 'bg-indigo-50 text-indigo-700'
          : 'text-indigo-100/80 hover:bg-indigo-700 hover:text-white'
      )}
    >
      <Icon className="h-4 w-4 flex-shrink-0" />
      {!collapsed && <span>{label}</span>}
    </Link>
  );
}
