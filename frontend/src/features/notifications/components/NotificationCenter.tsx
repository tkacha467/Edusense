import React, { useState } from 'react';
import { Bell, Check, Trash2 } from 'lucide-react';
import { Button } from '../../../components/ui/Button';
import { cn } from '../../../utils/cn';
import { useAuth } from '../../../contexts/AuthContext';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notificationApi } from '../../../api/notificationApi';

export function NotificationCenter() {
  const { currentUser } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const queryClient = useQueryClient();

  const { data: notificationsData, isLoading: isLoadingNotifications, isError: isNotificationsError } = useQuery({
    queryKey: ['notifications'],
    queryFn: async () => {
      const res = await notificationApi.getNotifications();
      return res.data;
    },
    enabled: !!currentUser,
    refetchInterval: 30000,
  });

  const { data: unreadCountData } = useQuery({
    queryKey: ['notificationsUnread'],
    queryFn: async () => {
      const res = await notificationApi.getUnreadCount();
      return res.data.unread_count;
    },
    enabled: !!currentUser,
    refetchInterval: 30000,
  });

  const markAsReadMutation = useMutation({
    mutationFn: (id: string) => notificationApi.markAsRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      queryClient.invalidateQueries({ queryKey: ['notificationsUnread'] });
    }
  });

  const markAllAsReadMutation = useMutation({
    mutationFn: () => notificationApi.markAllAsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      queryClient.invalidateQueries({ queryKey: ['notificationsUnread'] });
    }
  });

  const notifications = notificationsData || [];
  const unreadCount = unreadCountData || 0;

  const markAsRead = (id: string) => {
    markAsReadMutation.mutate(id);
  };

  const markAllAsRead = () => {
    markAllAsReadMutation.mutate();
  };

  const clearAll = () => {
    markAllAsReadMutation.mutate();
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return isNaN(date.getTime())
      ? 'Just now'
      : date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="relative">
      <Button variant="ghost" size="icon" onClick={() => setIsOpen(!isOpen)} className="relative">
        <span className="sr-only">View notifications</span>
        <Bell className="h-5 w-5 text-gray-500" aria-hidden="true" />
        {unreadCount > 0 && (
          <span className="absolute top-1.5 right-1.5 block h-2 w-2 rounded-full bg-destructive ring-2 ring-white" />
        )}
      </Button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          <div className="absolute right-0 top-12 z-50 w-80 sm:w-96 rounded-xl border bg-white shadow-xl origin-top-right animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between border-b px-4 py-3">
              <h3 className="font-semibold text-gray-900">Notifications</h3>
              <div className="flex gap-2">
                <Button variant="ghost" size="sm" onClick={markAllAsRead} className="h-8 text-xs" disabled={markAllAsReadMutation.isPending || notifications.length === 0}>
                  <Check className="h-3 w-3 mr-1" /> Mark all read
                </Button>
                <Button variant="ghost" size="icon" onClick={clearAll} className="h-8 w-8 text-xs text-muted-foreground hover:text-destructive" disabled={markAllAsReadMutation.isPending || notifications.length === 0}>
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            </div>
            
            <div className="max-h-[60vh] overflow-y-auto">
              {isLoadingNotifications ? (
                <div className="p-8 text-center text-sm text-muted-foreground flex flex-col items-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-2"></div>
                  Loading notifications...
                </div>
              ) : isNotificationsError ? (
                <div className="p-8 text-center text-sm text-red-500 flex flex-col items-center">
                  Failed to load notifications.
                  <Button variant="outline" size="sm" className="mt-2" onClick={() => queryClient.invalidateQueries({ queryKey: ['notifications'] })}>Retry</Button>
                </div>
              ) : notifications.length === 0 ? (
                <div className="p-8 text-center text-sm text-muted-foreground flex flex-col items-center">
                  <Bell className="h-8 w-8 text-gray-300 mb-2" />
                  No new notifications
                </div>
              ) : (
                <div className="divide-y">
                  {notifications.map((notification) => (
                    <div 
                      key={notification.id} 
                      className={cn(
                        "p-4 hover:bg-gray-50 transition-colors cursor-pointer relative group",
                        !notification.is_read && "bg-blue-50/50"
                      )}
                      onClick={() => markAsRead(notification.id)}
                    >
                      {!notification.is_read && (
                        <div className="absolute left-2 top-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-primary" />
                      )}
                      <div className="pl-3">
                        <div className="flex justify-between items-start mb-1">
                          <p className={cn("text-sm font-medium", !notification.is_read ? "text-gray-900" : "text-gray-700")}>
                            {notification.title}
                          </p>
                          <span className="text-xs text-muted-foreground whitespace-nowrap ml-2">{formatTime(notification.created_at)}</span>
                        </div>
                        <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed">
                          {notification.message}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
