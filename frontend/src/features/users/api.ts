import api from '../../lib/api';
import type {
  User,
  UserCreate,
  UserUpdate,
  UsersListResponse,
  UserResponse,
  Role,
  RolesListResponse,
} from './types';

export interface ListUsersParams {
  search?: string;
  role_id?: number;
  offset?: number;
  limit?: number;
}

export async function listUsers(params: ListUsersParams = {}): Promise<UsersListResponse> {
  const response = await api.get<UsersListResponse>('/users', { params });
  return response.data;
}

export async function getUser(id: number): Promise<User> {
  const response = await api.get<UserResponse>(`/users/${id}`);
  return response.data.data;
}

export async function createUser(data: UserCreate): Promise<User> {
  const response = await api.post<UserResponse>('/users', data);
  return response.data.data;
}

export async function updateUser(id: number, data: UserUpdate): Promise<User> {
  const response = await api.patch<UserResponse>(`/users/${id}`, data);
  return response.data.data;
}

export async function listRoles(): Promise<Role[]> {
  const response = await api.get<RolesListResponse>('/roles');
  return response.data.data;
}

export async function getCurrentUser(): Promise<User> {
  const response = await api.get<UserResponse>('/users/me');
  return response.data.data;
}

export async function updateCurrentUser(data: UserUpdate): Promise<User> {
  const response = await api.patch<UserResponse>('/users/me', data);
  return response.data.data;
}
