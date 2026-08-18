import apiClient from '../../../api/apiClient';
import type { Question } from '../types/question';
import type { AssessmentAnswer } from '../types/answer';
import type { AssessmentResult } from '../types/assessment';

export interface NextQuestionResponse {
  completed: boolean;
  question_number?: number;
  question?: Question;
}

export const assessmentApi = {
  getQuestions: async (sessionId: string): Promise<Question[]> => {
    const response = await apiClient.get<Question[]>(`/assessments/${sessionId}/questions`);
    return response.data;
  },

  saveAnswer: async (sessionId: string, answer: AssessmentAnswer): Promise<{ success: boolean }> => {
    const key = `edusense_draft_answers_${sessionId}`;
    const raw = localStorage.getItem(key);
    const answers = raw ? JSON.parse(raw) : {};
    answers[answer.question_id] = answer.selected_option_id;
    localStorage.setItem(key, JSON.stringify(answers));
    return { success: true };
  },

  submitAssessment: async (sessionId: string, responses: AssessmentAnswer[]): Promise<AssessmentResult> => {
    const response = await apiClient.post<AssessmentResult>(`/assessments/${sessionId}/submit`, {
      responses: responses.map(r => ({
        question_id: r.question_id,
        selected_option_id: r.selected_option_id,
        time_taken_seconds: r.time_taken_seconds || 15
      }))
    });
    localStorage.removeItem(`edusense_draft_answers_${sessionId}`);
    return response.data;
  },

  // --- Adaptive Assessment API ---
  startAdaptiveSession: async (subjectId: string, totalQuestions: number = 5): Promise<{ id: string }> => {
    const response = await apiClient.post<{ id: string }>('/assessments/start', {
      subject_id: subjectId,
      total_questions: totalQuestions,
      title: 'Adaptive Cognitive Assessment'
    });
    return response.data;
  },

  getNextQuestion: async (sessionId: string): Promise<NextQuestionResponse> => {
    const response = await apiClient.get<NextQuestionResponse>(`/assessments/${sessionId}/next`);
    return response.data;
  },

  submitSingleAnswer: async (
    sessionId: string, 
    questionId: string, 
    selectedOptionId: string, 
    timeTakenSeconds: number = 15
  ): Promise<{ is_correct: boolean; correct_option_id: string }> => {
    const response = await apiClient.post<{ is_correct: boolean; correct_option_id: string }>(
      `/assessments/${sessionId}/answer`, 
      {
        question_id: questionId,
        selected_option_id: selectedOptionId,
        time_taken_seconds: timeTakenSeconds
      }
    );
    return response.data;
  },

  finishAdaptiveSession: async (sessionId: string): Promise<AssessmentResult> => {
    const response = await apiClient.post<AssessmentResult>(`/assessments/${sessionId}/finish`);
    return response.data;
  },

  getAdaptiveSummary: async (sessionId: string): Promise<AssessmentResult> => {
    const response = await apiClient.get<AssessmentResult>(`/assessments/${sessionId}/summary`);
    return response.data;
  }
};
