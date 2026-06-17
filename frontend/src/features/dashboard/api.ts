import { useQuery } from '@tanstack/react-query';
import api from '../../lib/api';
import type { DashboardSummary } from './types';

interface DashboardResponse {
  success: boolean;
  data: DashboardSummary;
}

async function fetchDashboardSummary(activityPage: number): Promise<DashboardSummary> {
  const response = await api.get<DashboardResponse>('/dashboard/summary', {
    params: { activity_page: activityPage },
  });
  return response.data.data;
}

export function useDashboardSummary(activityPage: number) {
  return useQuery({
    queryKey: ['dashboard', activityPage],
    queryFn: () => fetchDashboardSummary(activityPage),
  });
}
