import api from '../../lib/api';
import type {
  Contact,
  ContactCreate,
  ContactUpdate,
  ContactsListResponse,
  ContactResponse,
} from './types';

export interface ListContactsParams {
  search?: string;
  account_id?: number;
  sort?: string;
  offset?: number;
  limit?: number;
}

export async function listContacts(params: ListContactsParams = {}): Promise<ContactsListResponse> {
  const response = await api.get<ContactsListResponse>('/contacts', { params });
  return response.data;
}

export async function getContact(id: number): Promise<Contact> {
  const response = await api.get<ContactResponse>(`/contacts/${id}`);
  return response.data.data;
}

export async function createContact(data: ContactCreate): Promise<Contact> {
  const response = await api.post<ContactResponse>('/contacts', data);
  return response.data.data;
}

export async function updateContact(id: number, data: ContactUpdate): Promise<Contact> {
  const response = await api.patch<ContactResponse>(`/contacts/${id}`, data);
  return response.data.data;
}

export async function deleteContact(id: number): Promise<void> {
  await api.delete(`/contacts/${id}`);
}
