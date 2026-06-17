import api from '../../lib/api';
import type { Activity, ActivityCreate, ActivityUpdate, ActivitiesListResponse, ActivityResponse } from './types';
import type { ActivityType } from './types';

export interface ListActivitiesParams {
  type?: ActivityType;
  contact_id?: number;
  opportunity_id?: number;
  offset?: number;
  limit?: number;
}

export async function listActivities(params: ListActivitiesParams = {}): Promise<ActivitiesListResponse> {
  const response = await api.get<ActivitiesListResponse>('/activities', { params });
  return response.data;
}

export async function getActivity(id: number): Promise<Activity> {
  const response = await api.get<ActivityResponse>(`/activities/${id}`);
  return response.data.data;
}

export async function createActivity(data: ActivityCreate): Promise<Activity> {
  const response = await api.post<ActivityResponse>('/activities', data);
  return response.data.data;
}

export async function updateActivity(id: number, data: ActivityUpdate): Promise<Activity> {
  const response = await api.patch<ActivityResponse>(`/activities/${id}`, data);
  return response.data.data;
}

export async function deleteActivity(id: number): Promise<void> {
  await api.delete(`/activities/${id}`);
}
