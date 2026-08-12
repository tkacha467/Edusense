import { useAuth } from './AuthContext';
import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { Notification } from '../types';
import apiClient from '../api/apiClient';

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  isDrawerOpen: boolean;
  toggleDrawer: () => void;
  markAsRead: (id: string) => void;
  clearAll: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { currentUser } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  useEffect(() => {
    if (currentUser?.id) {
      apiClient.get('/notifications/me')
        .then(res => setNotifications(res.data.items || res.data || []))
        .catch(err => console.error('Failed to fetch notifications:', err));
    } else {
      setNotifications([]);
    }
  }, [currentUser?.id]);

  const unreadCount = notifications.filter(n => !n.isRead).length;

  const toggleDrawer = () => setIsDrawerOpen(prev => !prev);

  const markAsRead = async (id: string) => {
    try {
      await apiClient.put(`/notifications/${id}/read`);
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, isRead: true } : n));
    } catch (e) {
      console.error('Failed to mark notification as read:', e);
    }
  };

  const clearAll = async () => {
    try {
      // No standard 'clear all' endpoint in REST usually, but assuming /notifications/clear
      await apiClient.post('/notifications/clear');
      setNotifications([]);
    } catch (e) {
      console.error('Failed to clear notifications:', e);
      setNotifications([]);
    }
  };

  return (
    <NotificationContext.Provider value={{
      notifications,
      unreadCount,
      isDrawerOpen,
      toggleDrawer,
      markAsRead,
      clearAll
    }}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};



