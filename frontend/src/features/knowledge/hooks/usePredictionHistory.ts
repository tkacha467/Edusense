import { useQuery } from '@tanstack/react-query';
import apiClient from '../../../api/apiClient';

export interface PredictionSnapshot {
  id: string;
  student_id: str;
  skill_id: str;
  interaction_order: number;
  past_attempts: number;
  past_correct: number;
  past_accuracy: number;
  rolling_accuracy: number;
  mastered: boolean;
  forget_probability: number;
  retention_score: number;
  confidence_score?: number;
  model_version: string;
  triggered_by: string;
  predicted_at: string;
}

export function usePredictionHistory(skillId?: string) {
  return useQuery<PredictionSnapshot[], Error>({
    queryKey: ['predictionHistory', skillId],
    queryFn: async () => {
      const response = await apiClient.get<PredictionSnapshot[]>(`/knowledge/skills/${skillId}/trend`);
      return response.data;
    },
    enabled: !!skillId
  });
}
