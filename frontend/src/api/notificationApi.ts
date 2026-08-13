import apiClient from './apiClient';

export interface NotificationItem {
  id: string;
  user_id: string;
  title: string;
  message: string;
  notification_type: string;
  priority: string;
  is_read: boolean;
  action_url?: string;
  created_at: string;
}

export const notificationApi = {
  getNotifications: () => apiClient.get<NotificationItem[]>('/notifications/me'),
  getUnreadCount: () => apiClient.get<{unread_count: number}>('/notifications/unread-count'),
  markAsRead: (id: string) => apiClient.put<NotificationItem>(`/notifications/${id}/read`),
  markAllAsRead: () => apiClient.put<{message: string; count: number}>('/notifications/read-all'),
};
