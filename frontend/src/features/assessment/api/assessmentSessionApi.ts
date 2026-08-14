import apiClient from '../../../api/apiClient';
import type { 
  AssessmentSession, 
  AssessmentSessionCreatePayload 
} from '../types/assessmentSession';

export const assessmentSessionApi = {
  createSession: async (payload: AssessmentSessionCreatePayload): Promise<AssessmentSession> => {
    const response = await apiClient.post<any>('/assessments/generate', {
      subject_id: payload.subjectId,
      topic_id: payload.topicId,
      title: 'Adaptive Assessment',
      difficulty_level: payload.difficulty || 'intermediate',
      total_questions: payload.totalQuestions || 5,
      generation_method: 'ai'
    });
    return response.data;
  },

  startSession: async (sessionId: string): Promise<AssessmentSession> => {
    const response = await apiClient.post<any>(`/assessments/${sessionId}/start`);
    return response.data;
  },

  getSession: async (sessionId: string): Promise<AssessmentSession> => {
    // Audit Note: Direct GET /assessments/{id} does not exist in backend.
    // Bypassing by fetching session history and finding the matching session id.
    const response = await apiClient.get<any>('/assessments/history', {
      params: { page: 1, page_size: 100 }
    });
    const items = response.data?.items || response.data || [];
    const found = items.find((item: any) => item.id === sessionId);
    if (!found) {
      throw new Error(`Assessment session '${sessionId}' not found in history.`);
    }
    return found;
  },

  getCurrentSession: async (): Promise<AssessmentSession | null> => {
    // Audit Note: Direct GET /assessments/active does not exist in backend.
    // Fetching session history and looking for any session with status 'in_progress'.
    const response = await apiClient.get<any>('/assessments/history', {
      params: { page: 1, page_size: 100 }
    });
    const items = response.data?.items || response.data || [];
    const active = items.find((item: any) => item.status === 'in_progress');
    return active || null;
  },

  cancelSession: async (sessionId: string): Promise<AssessmentSession> => {
    const response = await apiClient.post<any>(`/assessments/${sessionId}/abandon`);
    return response.data;
  },

  completeSession: async (sessionId: string, responses: any[]): Promise<any> => {
    const response = await apiClient.post<any>(`/assessments/${sessionId}/submit`, { responses });
    return response.data;
  }
};
