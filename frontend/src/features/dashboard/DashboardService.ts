import apiClient from '../../api/apiClient';

export class DashboardService {
  async getDashboardData() {
    try {
      const [profilesRes, recommendationsRes, historyRes, notificationsRes] = await Promise.all([
        apiClient.get('/knowledge/profiles').catch(() => ({ data: [] })),
        apiClient.get('/recommendations/today').catch(() => ({ data: [] })),
        apiClient.get('/assessments/history').catch(() => ({ data: { items: [] } })),
        apiClient.get('/notifications/unread-count').catch(() => ({ data: { unread_count: 0 } }))
      ]);

      return {
        knowledgeProfiles: profilesRes.data || [],
        todayTasks: recommendationsRes.data || [],
        assessmentHistory: historyRes.data?.items || historyRes.data || [],
        unreadNotificationsCount: notificationsRes.data?.unread_count || 0
      };
    } catch (e) {
      return {
        knowledgeProfiles: [],
        todayTasks: [],
        assessmentHistory: [],
        unreadNotificationsCount: 0
      };
    }
  }
}

export const dashboardService = new DashboardService();
