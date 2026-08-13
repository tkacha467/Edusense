import { useQuery } from '@tanstack/react-query';
import { dashboardApi, type DashboardData } from '../../../api/dashboardApi';

export function useDashboard() {
  return useQuery<DashboardData, Error>({
    queryKey: ['dashboardData'],
    queryFn: dashboardApi.getDashboardData,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
