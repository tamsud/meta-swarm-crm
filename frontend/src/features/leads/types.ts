export type LeadStatus = 'new' | 'contacted' | 'qualified' | 'lost';

export interface Lead {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  company: string | null;
  status: LeadStatus;
  source: string | null;
  notes: string | null;
  created_by_user_id: number | null;
  converted_opportunity_id: number | null;
  converted_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface LeadCreate {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  company?: string;
  status?: LeadStatus;
  source?: string;
  notes?: string;
}

export interface LeadUpdate {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  company?: string;
  status?: LeadStatus;
  source?: string;
  notes?: string;
}

export interface LeadsListResponse {
  success: boolean;
  data: Lead[];
  meta: {
    count: number;
    total: number;
    offset: number;
    limit: number;
  };
}

export interface LeadResponse {
  success: boolean;
  data: Lead;
}

export interface OpportunityRef {
  id: number;
  title: string;
}

export interface ConvertResponse {
  success: boolean;
  data: OpportunityRef;
}

export const VALID_TRANSITIONS: Record<LeadStatus, LeadStatus[]> = {
  new: ['contacted', 'lost'],
  contacted: ['qualified', 'lost'],
  qualified: ['lost'],
  lost: [],
};
