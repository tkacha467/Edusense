import { useQuery } from '@tanstack/react-query';
import {
  fetchProfileSummary,
  fetchDashboardSummary,
  fetchKnowledgeHealth,
  fetchRevisionQueue,
  fetchWeakSkills,
  fetchRecentActivities,
} from '../api/dashboardApi';
import type { RevisionQueueQueryParams } from '../api/dashboardApi';

export const useProfileSummary = () => {
  return useQuery({
    queryKey: ['dashboard', 'profile-summary'],
    queryFn: fetchProfileSummary,
    staleTime: 5 * 60 * 1000,
  });
};

export const useDashboardSummary = () => {
  return useQuery({
    queryKey: ['dashboard', 'summary'],
    queryFn: fetchDashboardSummary,
    staleTime: 60 * 1000,
  });
};

export const useKnowledgeHealth = () => {
  return useQuery({
    queryKey: ['dashboard', 'knowledge-health'],
    queryFn: fetchKnowledgeHealth,
    staleTime: 2 * 60 * 1000,
  });
};

export const useRevisionQueue = (params: RevisionQueueQueryParams = {}) => {
  return useQuery({
    queryKey: ['dashboard', 'revision-queue', params],
    queryFn: () => fetchRevisionQueue(params),
    staleTime: 30 * 1000,
  });
};

export const useWeakSkills = (limit: number = 5) => {
  return useQuery({
    queryKey: ['dashboard', 'weak-skills', limit],
    queryFn: () => fetchWeakSkills(limit),
    staleTime: 2 * 60 * 1000,
  });
};

export const useRecentActivities = (limit: number = 10) => {
  return useQuery({
    queryKey: ['dashboard', 'recent-activities', limit],
    queryFn: () => fetchRecentActivities(limit),
    staleTime: 60 * 1000,
  });
};

import { dashboardApi } from '../../../api/dashboardApi';
import type { DashboardData } from '../../../api/dashboardApi';

export function useDashboard() {
  return useQuery<DashboardData, Error>({
    queryKey: ['dashboardData'],
    queryFn: dashboardApi.getDashboardData,
    staleTime: 5 * 60 * 1000,
  });
}
