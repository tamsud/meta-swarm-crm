export type ActivityType = 'call' | 'email' | 'meeting';

export interface KpiData {
  total_accounts: number;
  active_leads: number;
  open_pipeline: number;
  weighted_value: number;
  win_rate: number;
}

export interface StageBreakdown {
  stage: string;
  count: number;
  value: number;
}

export interface ClosedCard {
  count: number;
  value: number;
}

export interface ClosedData {
  won: ClosedCard;
  lost: ClosedCard;
}

export interface ActivitySummary {
  id: number;
  type: ActivityType;
  subject: string;
  contact_name: string | null;
  opportunity_title: string | null;
  activity_date: string;
}

export interface PaginatedActivities {
  items: ActivitySummary[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface DashboardSummary {
  kpis: KpiData;
  stage_breakdown: StageBreakdown[];
  closed: ClosedData;
  recent_activities: PaginatedActivities;
}
