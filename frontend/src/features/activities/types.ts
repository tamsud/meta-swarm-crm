export type ActivityType = 'call' | 'email' | 'meeting';

export interface Activity {
  id: number;
  type: ActivityType;
  subject: string;
  notes: string | null;
  activity_date: string;
  contact_id: number | null;
  opportunity_id: number | null;
  created_by_user_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface ActivityCreate {
  type: ActivityType;
  subject: string;
  notes?: string;
  activity_date?: string;
  contact_id?: number | null;
  opportunity_id?: number | null;
}

export interface ActivityUpdate {
  type?: ActivityType;
  subject?: string;
  notes?: string;
  activity_date?: string;
  contact_id?: number | null;
  opportunity_id?: number | null;
}

export interface ActivitiesListResponse {
  success: boolean;
  data: Activity[];
  meta: {
    count: number;
    total: number;
    offset: number;
    limit: number;
  };
}

export interface ActivityResponse {
  success: boolean;
  data: Activity;
}
