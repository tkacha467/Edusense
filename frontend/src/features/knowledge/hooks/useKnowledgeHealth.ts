import { useQuery } from '@tanstack/react-query';
import apiClient from '../../../api/apiClient';

interface KnowledgeHealthData {
  health_score: number;
  rating: string;
  total_skills_tracked: number;
}

export function useKnowledgeHealth() {
  return useQuery<KnowledgeHealthData, Error>({
    queryKey: ['knowledgeHealth'],
    queryFn: async () => {
      const response = await apiClient.get<KnowledgeHealthData>('/knowledge/health');
      return response.data;
    }
  });
}
