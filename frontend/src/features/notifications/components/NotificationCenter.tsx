import React, { useState, useEffect } from 'react';
import { Bell, Check, Trash2 } from 'lucide-react';
import { Button } from '../../../components/ui/Button';
import { cn } from '../../../utils/cn';
import { useAuth } from '../../../contexts/AuthContext';

interface NotificationItem {
  id: string;
  title: string;
  message: string;
  time: string;
  read: boolean;
}

interface RawNotification {
  id: string;
  userId: string;
  title: string;
  message: string;
  isRead: boolean;
  type: string;
  createdAt: string;
}

export function NotificationCenter() {
  const { currentUser } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);

  // Load notifications from localStorage
  const loadNotifications = () => {
    if (!currentUser) return;
    try {
      const dataStr = localStorage.getItem('edu_mock_notifications');
      if (dataStr) {
        const allNotifs: RawNotification[] = JSON.parse(dataStr);
        const userNotifs = allNotifs
          .filter((n) => n.userId === currentUser.id)
          .map((n) => {
            // format relative time or simple time
            const date = new Date(n.createdAt);
            const timeStr = isNaN(date.getTime())
              ? 'Just now'
              : date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            return {
              id: n.id,
              title: n.title,
              message: n.message,
              time: timeStr,
              read: n.isRead,
            };
          });
        setNotifications(userNotifs);
      }
    } catch (e) {
      console.error('Failed to load notifications', e);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, [currentUser]);

  // Save changes to localStorage helper
  const updateStoredNotifications = (updateFn: (all: RawNotification[]) => RawNotification[]) => {
    try {
      const dataStr = localStorage.getItem('edu_mock_notifications');
      if (dataStr) {
        const allNotifs: RawNotification[] = JSON.parse(dataStr);
        const updated = updateFn(allNotifs);
        localStorage.setItem('edu_mock_notifications', JSON.stringify(updated));
      }
    } catch (e) {
      console.error('Failed to update notifications in storage', e);
    }
  };

  const markAsRead = (id: string) => {
    setNotifications(notifications.map(n => n.id === id ? { ...n, read: true } : n));
    updateStoredNotifications((all) =>
      all.map((n) => (n.id === id ? { ...n, isRead: true } : n))
    );
  };

  const markAllAsRead = () => {
    setNotifications(notifications.map(n => ({ ...n, read: true })));
    updateStoredNotifications((all) =>
      all.map((n) => (n.userId === currentUser?.id ? { ...n, isRead: true } : n))
    );
  };

  const clearAll = () => {
    setNotifications([]);
    updateStoredNotifications((all) =>
      all.filter((n) => n.userId !== currentUser?.id)
    );
  };


  const unreadCount = notifications.filter(n => !n.read).length;

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
                <Button variant="ghost" size="sm" onClick={markAllAsRead} className="h-8 text-xs">
                  <Check className="h-3 w-3 mr-1" /> Mark all read
                </Button>
                <Button variant="ghost" size="icon" onClick={clearAll} className="h-8 w-8 text-xs text-muted-foreground hover:text-destructive">
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            </div>
            
            <div className="max-h-[60vh] overflow-y-auto">
              {notifications.length === 0 ? (
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
                        !notification.read && "bg-blue-50/50"
                      )}
                      onClick={() => markAsRead(notification.id)}
                    >
                      {!notification.read && (
                        <div className="absolute left-2 top-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-primary" />
                      )}
                      <div className="pl-3">
                        <div className="flex justify-between items-start mb-1">
                          <p className={cn("text-sm font-medium", !notification.read ? "text-gray-900" : "text-gray-700")}>
                            {notification.title}
                          </p>
                          <span className="text-xs text-muted-foreground whitespace-nowrap ml-2">{notification.time}</span>
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
