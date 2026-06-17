import api from '../../lib/api';

export interface SeedSummary {
  [entity: string]: { created: number; skipped: number };
}

export interface ClearSummary {
  [entity: string]: number;
}

interface SeedResponse {
  success: boolean;
  data: { summary: SeedSummary };
}

interface ClearResponse {
  success: boolean;
  data: { deleted: ClearSummary };
}

export async function seedData(): Promise<SeedSummary> {
  const response = await api.post<SeedResponse>('/seed');
  return response.data.data.summary;
}

export async function clearData(): Promise<ClearSummary> {
  const response = await api.delete<ClearResponse>('/seed');
  return response.data.data.deleted;
}
