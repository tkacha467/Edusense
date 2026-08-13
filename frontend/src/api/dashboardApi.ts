import apiClient from './apiClient';

export interface DashboardKnowledgeProfile {
  id: string;
  topic_id: string;
  skill_id: string;
  forget_probability: number;
  retention_score: number;
  mastered: boolean;
  topic_name?: string;
}

export interface DashboardTask {
  id: string;
  task_title: string;
  task_type: string;
  estimated_minutes: number;
  is_completed: boolean;
  priority: string;
}

export interface DashboardAssessmentHistory {
  id: string;
  title: string;
  percentage: number;
  started_at: string;
  completed_at?: string;
  status: string;
}

export interface DashboardData {
  knowledgeProfiles: DashboardKnowledgeProfile[];
  todayTasks: DashboardTask[];
  assessmentHistory: DashboardAssessmentHistory[];
  unreadNotificationsCount: number;
}

export const dashboardApi = {
  getDashboardData: async (): Promise<DashboardData> => {
    try {
      const [profilesRes, recommendationsRes, historyRes, notificationsRes] = await Promise.all([
        apiClient.get<DashboardKnowledgeProfile[]>('/knowledge/profiles').catch(() => ({ data: [] })),
        apiClient.get<DashboardTask[]>('/recommendations/today').catch(() => ({ data: [] })),
        apiClient.get<{items: DashboardAssessmentHistory[]}>('/assessments/history').catch(() => ({ data: { items: [] } })),
        apiClient.get<{unread_count: number}>('/notifications/unread-count').catch(() => ({ data: { unread_count: 0 } }))
      ]);

      return {
        knowledgeProfiles: profilesRes.data || [],
        todayTasks: recommendationsRes.data || [],
        assessmentHistory: historyRes.data?.items || (historyRes.data as any) || [],
        unreadNotificationsCount: notificationsRes.data?.unread_count || 0
      };
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw error;
    }
  }
};
