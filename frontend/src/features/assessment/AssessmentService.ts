import apiClient from '../../api/apiClient';
import type { AssessmentSession } from '../../types';

export class AssessmentService {
  async generateSession(subjectId: string, topicId?: string, difficulty: string = 'intermediate', totalQuestions: number = 3): Promise<any> {
    const response = await apiClient.post('/assessments/generate', {
      subject_id: subjectId,
      topic_id: topicId,
      title: 'Adaptive Assessment',
      difficulty_level: difficulty,
      total_questions: totalQuestions,
      generation_method: 'ai'
    });
    return response.data;
  }

  async startSession(sessionId: string): Promise<any> {
    const response = await apiClient.post(`/assessments/${sessionId}/start`);
    return response.data;
  }

  async getQuestions(sessionId: string): Promise<any[]> {
    const response = await apiClient.get(`/assessments/${sessionId}/questions`);
    return response.data;
  }

  async submitAssessment(sessionId: string, responses: any[]): Promise<any> {
    const response = await apiClient.post(`/assessments/${sessionId}/submit`, { responses });
    return response.data;
  }
}

export const assessmentService = new AssessmentService();
