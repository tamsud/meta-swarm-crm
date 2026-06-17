import api from '../../lib/api';
import type {
  MockEmail,
  MockEmailCreate,
  MockEmailsListResponse,
  MockEmailResponse,
  ClearMockEmailsResponse,
} from './types';

export interface ListMockEmailsParams {
  sort?: string;
  search?: string;
  offset?: number;
  limit?: number;
}

export async function listMockEmails(params: ListMockEmailsParams = {}): Promise<MockEmailsListResponse> {
  const response = await api.get<MockEmailsListResponse>('/mock-emails', { params });
  return response.data;
}

export async function getMockEmail(id: string): Promise<MockEmail> {
  const response = await api.get<MockEmailResponse>(`/mock-emails/${id}`);
  return response.data.data;
}

export async function createMockEmail(data: MockEmailCreate): Promise<MockEmail> {
  const response = await api.post<MockEmailResponse>('/mock-emails', data);
  return response.data.data;
}

export async function markAsRead(id: string): Promise<MockEmail> {
  const response = await api.patch<MockEmailResponse>(`/mock-emails/${id}/read`);
  return response.data.data;
}

export async function clearMockEmails(): Promise<number> {
  const response = await api.delete<ClearMockEmailsResponse>('/mock-emails');
  return response.data.data.deleted_count;
}
