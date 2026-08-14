import { useQuery } from '@tanstack/react-query';
import apiClient from '../../../api/apiClient';

export interface RevisionTask {
  id: string;
  study_plan_id: string;
  topic_id: string;
  skill_id: string;
  title: string;
  task_type: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';
  estimated_minutes: number;
  scheduled_date: string;
  order_index: number;
  skill?: {
    id: string;
    name: string;
    description?: string;
  };
  topic?: {
    id: string;
    name: string;
  };
}

export function useRevisionQueue() {
  return useQuery<RevisionTask[], Error>({
    queryKey: ['revisionQueue'],
    queryFn: async () => {
      const response = await apiClient.get<RevisionTask[]>('/recommendations/today');
      return response.data;
    }
  });
}
