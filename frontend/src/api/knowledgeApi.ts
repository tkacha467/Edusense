import apiClient from './apiClient';

export interface KnowledgeProfile {
  id: string;
  student_id: string;
  topic_id: string;
  skill_id: string;
  mastery_level: number;
  retention_score: number;
  forget_probability: number;
  mastered: boolean;
  skill?: {
    id: string;
    name: string;
  };
}

export interface PredictionPayload {
  skill_id: string;
}

export interface PredictionResult {
  student_id: string;
  skill_id: string;
  forget_probability: number;
  retention_score: number;
  days_since_review: number;
  risk_level: string;
  recommended_action: string;
}

export const knowledgeApi = {
  getProfiles: () => apiClient.get<KnowledgeProfile[]>('/knowledge/profiles'),
  predict: (data: PredictionPayload) => apiClient.post<PredictionResult>('/knowledge/predict', data),
};
