import apiClient from './apiClient';

export interface SubjectResponse {
  id: string;
  name: string;
  code: string;
  description: string;
  category: string;
  semester: number;
  is_active: boolean;
  topic_count: number;
}

export interface TopicResponse {
  id: string;
  subject_id: string;
  name: string;
  description: string;
  difficulty_level: string;
  order_index: number;
  is_active: boolean;
  subject_name?: string;
}

export interface TopicSkillResponse {
  topic_id?: string;
  skill_id?: string;
  relevance_weight?: number;
  id?: string;
  name?: string;
  description?: string;
  category?: string;
}

export const learningApi = {
  getSubjects: async (): Promise<SubjectResponse[]> => {
    const response = await apiClient.get<SubjectResponse[]>('/learning/subjects');
    return response.data;
  },

  getTopics: async (subjectId: string): Promise<TopicResponse[]> => {
    const response = await apiClient.get<TopicResponse[]>(`/learning/subjects/${subjectId}/topics`);
    return response.data;
  },

  getSkills: async (topicId: string): Promise<TopicSkillResponse[]> => {
    const response = await apiClient.get<TopicSkillResponse[]>(`/learning/topics/${topicId}/skills`);
    return response.data;
  }
};
