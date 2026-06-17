export type OpportunityStage =
  | 'prospecting'
  | 'proposal'
  | 'negotiation'
  | 'closed_won'
  | 'closed_lost';

export const STAGE_ORDER: OpportunityStage[] = [
  'prospecting',
  'proposal',
  'negotiation',
  'closed_won',
  'closed_lost',
];

export const STAGE_LABELS: Record<OpportunityStage, string> = {
  prospecting: 'Prospecting',
  proposal: 'Proposal',
  negotiation: 'Negotiation',
  closed_won: 'Closed Won',
  closed_lost: 'Closed Lost',
};

export const STAGE_COLORS: Record<OpportunityStage, string> = {
  prospecting: 'bg-blue-100 text-blue-800 border-blue-200',
  proposal: 'bg-purple-100 text-purple-800 border-purple-200',
  negotiation: 'bg-amber-100 text-amber-800 border-amber-200',
  closed_won: 'bg-green-100 text-green-800 border-green-200',
  closed_lost: 'bg-slate-100 text-slate-800 border-slate-200',
};

export interface Opportunity {
  id: number;
  title: string;
  account_id: number;
  contact_id: number | null;
  stage: OpportunityStage;
  value: string | null; // Decimal comes as string from API
  probability: number | null;
  expected_close_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface OpportunityCreate {
  title: string;
  account_id: number;
  contact_id?: number;
  stage?: OpportunityStage;
  value?: number;
  probability?: number;
  expected_close_date?: string;
}

export interface OpportunityUpdate {
  title?: string;
  account_id?: number;
  contact_id?: number;
  stage?: OpportunityStage;
  value?: number;
  probability?: number;
  expected_close_date?: string;
}

export interface OpportunitiesListResponse {
  success: boolean;
  data: Opportunity[];
  meta: {
    total: number;
    count: number;
    offset: number;
    limit: number;
  };
}

export interface OpportunityResponse {
  success: boolean;
  data: Opportunity;
}
