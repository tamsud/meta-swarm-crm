import type { LucideIcon } from 'lucide-react';
import {
  LayoutDashboard,
  Building2,
  Users,
  Target,
  TrendingUp,
  Activity,
  UserCog,
  Mail,
  Database,
} from 'lucide-react';

export const ROUTES = {
  DASHBOARD: '/',
  ACCOUNTS: '/accounts',
  ACCOUNT_DETAIL: '/accounts/:id',
  CONTACTS: '/contacts',
  LEADS: '/leads',
  OPPORTUNITIES: '/opportunities',
  ACTIVITIES: '/activities',
  ADMIN_USERS: '/admin/users',
  ADMIN_MOCK_EMAIL: '/admin/mock-email',
  ADMIN_SEED: '/admin/seed',
  PROFILE: '/profile',
  LOGIN: '/login',
} as const;

export interface NavItemConfig {
  path: string;
  label: string;
  icon: LucideIcon;
}

export const NAV_ITEMS: NavItemConfig[] = [
  { path: ROUTES.DASHBOARD, label: 'Dashboard', icon: LayoutDashboard },
  { path: ROUTES.ACCOUNTS, label: 'Accounts', icon: Building2 },
  { path: ROUTES.CONTACTS, label: 'Contacts', icon: Users },
  { path: ROUTES.LEADS, label: 'Leads', icon: Target },
  { path: ROUTES.OPPORTUNITIES, label: 'Pipeline', icon: TrendingUp },
  { path: ROUTES.ACTIVITIES, label: 'Activities', icon: Activity },
];

export const ADMIN_NAV_ITEMS: NavItemConfig[] = [
  { path: ROUTES.ADMIN_USERS, label: 'Users', icon: UserCog },
  { path: ROUTES.ADMIN_MOCK_EMAIL, label: 'Mock Email', icon: Mail },
  { path: ROUTES.ADMIN_SEED, label: 'Seed Manager', icon: Database },
];
