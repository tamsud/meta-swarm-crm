import api from '../../lib/api';
import type { Lead, LeadCreate, LeadUpdate, LeadsListResponse, LeadResponse, ConvertResponse } from './types';
import type { LeadStatus } from './types';

export interface ListLeadsParams {
  status?: LeadStatus | 'converted';
  search?: string;
  offset?: number;
  limit?: number;
}

export async function listLeads(params: ListLeadsParams = {}): Promise<LeadsListResponse> {
  const response = await api.get<LeadsListResponse>('/leads', { params });
  return response.data;
}

export async function getLead(id: number): Promise<Lead> {
  const response = await api.get<LeadResponse>(`/leads/${id}`);
  return response.data.data;
}

export async function createLead(data: LeadCreate): Promise<Lead> {
  const response = await api.post<LeadResponse>('/leads', data);
  return response.data.data;
}

export async function updateLead(id: number, data: LeadUpdate): Promise<Lead> {
  const response = await api.patch<LeadResponse>(`/leads/${id}`, data);
  return response.data.data;
}

export async function deleteLead(id: number): Promise<void> {
  await api.delete(`/leads/${id}`);
}

export async function convertLead(id: number): Promise<{ id: number; title: string }> {
  const response = await api.post<ConvertResponse>(`/leads/${id}/convert`);
  return response.data.data;
}
