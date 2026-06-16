import api from '../../lib/api';
import type {
  Account,
  AccountCreate,
  AccountUpdate,
  AccountsListResponse,
  AccountResponse,
} from './types';

export interface ListAccountsParams {
  search?: string;
  offset?: number;
  limit?: number;
}

export async function listAccounts(params: ListAccountsParams = {}): Promise<AccountsListResponse> {
  const response = await api.get<AccountsListResponse>('/accounts', { params });
  return response.data;
}

export async function getAccount(id: number): Promise<Account> {
  const response = await api.get<AccountResponse>(`/accounts/${id}`);
  return response.data.data;
}

export async function createAccount(data: AccountCreate): Promise<Account> {
  const response = await api.post<AccountResponse>('/accounts', data);
  return response.data.data;
}

export async function updateAccount(id: number, data: AccountUpdate): Promise<Account> {
  const response = await api.patch<AccountResponse>(`/accounts/${id}`, data);
  return response.data.data;
}

export async function deleteAccount(id: number): Promise<void> {
  await api.delete(`/accounts/${id}`);
}
