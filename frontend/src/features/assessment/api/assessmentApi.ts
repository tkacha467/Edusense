import apiClient from '../../../api/apiClient';
import { Question } from '../types/question';
import { AssessmentAnswer } from '../types/answer';
import { AssessmentResult } from '../types/assessment';

export const assessmentApi = {
  getQuestions: async (sessionId: string): Promise<Question[]> => {
    const response = await apiClient.get<Question[]>(`/assessments/${sessionId}/questions`);
    return response.data;
  },

  saveAnswer: async (sessionId: string, answer: AssessmentAnswer): Promise<{ success: boolean }> => {
    // Audit Note: POST /assessment-sessions/{session_id}/answers does not exist on the backend.
    // Simulating progress caching in local storage as a fallback.
    const key = `edusense_draft_answers_${sessionId}`;
    const raw = localStorage.getItem(key);
    const answers = raw ? JSON.parse(raw) : {};
    answers[answer.question_id] = answer.selected_option_id;
    localStorage.setItem(key, JSON.stringify(answers));
    
    console.log(`[Draft Saved Locally] Session: ${sessionId}, Question: ${answer.question_id}, Option: ${answer.selected_option_id}`);
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
    // Clear draft answers on success
    localStorage.removeItem(`edusense_draft_answers_${sessionId}`);
    return response.data;
  }
};
