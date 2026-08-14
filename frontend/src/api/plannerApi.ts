import apiClient from './apiClient';

export interface StudyTask {
  id: string;
  study_plan_id: string;
  topic_id?: string;
  skill_id?: string;
  title: string;
  task_type: 'REVISION' | 'LEARNING' | 'ASSESSMENT';
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'PENDING' | 'SKIPPED' | 'COMPLETED';
  estimated_minutes?: number;
  scheduled_date?: string;
  completed_at?: string;
  order_index: number;
}

export interface StudyPlan {
  id: string;
  student_id: string;
  subject_id?: string;
  title: string;
  description?: string;
  plan_type: string;
  status: string;
  start_date?: string;
  end_date?: string;
  tasks?: StudyTask[];
}

export const plannerApi = {
  getTodayTasks: async (): Promise<StudyTask[]> => {
    const res = await apiClient.get<StudyTask[]>('/recommendations/today');
    return res.data;
  },
  
  getUpcomingTasks: async (): Promise<StudyTask[]> => {
    const res = await apiClient.get<StudyTask[]>('/recommendations/upcoming');
    return res.data;
  },

  generatePlan: async (subjectId?: string): Promise<StudyPlan> => {
    const res = await apiClient.post<StudyPlan>('/recommendations/generate', null, {
      params: { subject_id: subjectId }
    });
    return res.data;
  },

  getStudyPlans: async (): Promise<StudyPlan[]> => {
    const res = await apiClient.get<StudyPlan[]>('/study-plans');
    return res.data;
  },

  completeTask: async (taskId: string): Promise<StudyTask> => {
    const res = await apiClient.put<StudyTask>(`/study-tasks/${taskId}/complete`);
    return res.data;
  },

  skipTask: async (taskId: string): Promise<StudyTask> => {
    const res = await apiClient.put<StudyTask>(`/study-tasks/${taskId}/skip`);
    return res.data;
  }
};
