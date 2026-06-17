import api from '../../lib/api';
import type {
  Opportunity,
  OpportunityCreate,
  OpportunityUpdate,
  OpportunitiesListResponse,
  OpportunityResponse,
  OpportunityStage,
} from './types';

export interface ListOpportunitiesParams {
  stage?: OpportunityStage;
  account_id?: number;
  contact_id?: number;
  offset?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export async function listOpportunities(
  params: ListOpportunitiesParams = {}
): Promise<OpportunitiesListResponse> {
  const response = await api.get<OpportunitiesListResponse>('/opportunities', { params });
  return response.data;
}

export async function getOpportunity(id: number): Promise<Opportunity> {
  const response = await api.get<OpportunityResponse>(`/opportunities/${id}`);
  return response.data.data;
}

export async function createOpportunity(data: OpportunityCreate): Promise<Opportunity> {
  const response = await api.post<OpportunityResponse>('/opportunities', data);
  return response.data.data;
}

export async function updateOpportunity(
  id: number,
  data: OpportunityUpdate
): Promise<Opportunity> {
  const response = await api.patch<OpportunityResponse>(`/opportunities/${id}`, data);
  return response.data.data;
}

export async function deleteOpportunity(id: number): Promise<void> {
  await api.delete(`/opportunities/${id}`);
}
