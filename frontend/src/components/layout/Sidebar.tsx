import { ChevronLeft, BarChart3 } from 'lucide-react';
import clsx from 'clsx';
import { NavItem } from './NavItem';
import { NAV_ITEMS, ADMIN_NAV_ITEMS } from '../../routes/config';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  return (
    <aside
      className={clsx(
        'hidden md:flex flex-col bg-indigo-900 px-3 py-4 relative transition-all duration-200',
        collapsed ? 'w-[68px]' : 'w-60'
      )}
    >
      <button
        type="button"
        onClick={onToggle}
        className="absolute -right-3 top-6 w-6 h-6 rounded-full bg-indigo-700 hover:bg-indigo-600 flex items-center justify-center text-white shadow-md z-10"
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        <ChevronLeft
          className={clsx(
            'h-4 w-4 transition-transform duration-200',
            collapsed && 'rotate-180'
          )}
        />
      </button>

      <div className="flex items-center gap-2 px-3 py-2 mb-4">
        <BarChart3 className="h-6 w-6 text-white flex-shrink-0" />
        {!collapsed && (
          <span className="text-white font-semibold text-lg">Sales CRM</span>
        )}
      </div>

      <nav className="flex flex-col gap-1">
        {NAV_ITEMS.map((item) => (
          <NavItem
            key={item.path}
            path={item.path}
            label={item.label}
            icon={item.icon}
            collapsed={collapsed}
          />
        ))}
      </nav>

      <div className="border-t border-indigo-700 my-4" />

      {!collapsed && (
        <span className="px-3 py-1 text-xs font-semibold text-indigo-400 uppercase tracking-wider">
          Admin
        </span>
      )}

      <nav className="flex flex-col gap-1 mt-1">
        {ADMIN_NAV_ITEMS.map((item) => (
          <NavItem
            key={item.path}
            path={item.path}
            label={item.label}
            icon={item.icon}
            collapsed={collapsed}
          />
        ))}
      </nav>

      <div className="flex-1" />
    </aside>
  );
}
