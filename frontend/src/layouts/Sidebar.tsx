import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, BrainCircuit, Activity, FileText, User, Settings, Sparkles, Shield } from 'lucide-react';
import { cn } from '../utils/cn';
import { useAuth } from '../contexts/AuthContext';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Prediction', href: '/prediction', icon: BrainCircuit },
  { name: 'Model Monitoring', href: '/faculty/model-monitoring', icon: Activity },
  { name: 'Analytics', href: '/analytics', icon: Activity },
  { name: 'Reports', href: '/reports', icon: FileText },
  { name: 'AI Assistant', href: '/assistant', icon: Sparkles },
];

const secondaryNavigation = [
  { name: 'Profile', href: '/profile', icon: User },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const { role } = useAuth();

  const menuItems = [...navigation];
  if (role === 'admin' || role === 'super_admin') {
    menuItems.push({ name: 'Admin Panel', href: '/admin/dashboard', icon: Shield });
  }
  return (
    <div className="flex h-full w-64 flex-col border-r bg-white">
      <div className="flex h-16 items-center gap-2 px-6 border-b">
        <div className="bg-primary/10 p-1.5 rounded-lg text-primary">
          <BrainCircuit className="h-5 w-5" />
        </div>
        <span className="text-lg font-bold tracking-tight">EduSense</span>
      </div>
      
      <div className="flex-1 overflow-y-auto py-6 flex flex-col gap-6">
        <div className="px-4">
          <h3 className="px-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
            Main Menu
          </h3>
          <nav className="flex flex-col gap-1">
            {menuItems.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-colors relative group",
                    isActive
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-gray-100 hover:text-foreground"
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    {isActive && (
                      <div className="absolute left-0 top-1.5 bottom-1.5 w-1 bg-primary rounded-r-full" />
                    )}
                    <item.icon className={cn("h-4 w-4", isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground")} />
                    {item.name}
                  </>
                )}
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="px-4 mt-auto">
          <h3 className="px-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
            Preferences
          </h3>
          <nav className="flex flex-col gap-1">
            {secondaryNavigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors relative group",
                    isActive
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-gray-100 hover:text-foreground"
                  )
                }
              >
                <item.icon className="h-4 w-4" />
                {item.name}
              </NavLink>
            ))}
          </nav>
        </div>
      </div>
    </div>
  );
}
