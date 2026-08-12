import { useAuth } from '../contexts/AuthContext';
import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { BrainCircuit, BookOpen, Target, User, Bell, LogOut, Settings, ChevronDown } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { NotificationCenter } from '../features/notifications/components/NotificationCenter';

export function StudentLayout() {
  const { currentUser, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [profileOpen, setProfileOpen] = useState(false);

  const navItems = [
    { path: '/student/dashboard', label: 'My Progress', icon: Target },
    { path: '/student/plan', label: 'Study Plan', icon: BookOpen },
  ];

  const handleLogout = async () => {
    setProfileOpen(false);
    await logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Top Navigation */}
      <header className="sticky top-0 z-40 w-full bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            
            {/* Logo */}
            <div className="flex items-center gap-2">
              <div className="bg-primary/10 p-1.5 rounded-lg">
                <BrainCircuit className="h-6 w-6 text-primary" />
              </div>
              <span className="text-xl font-bold tracking-tight text-gray-900 hidden sm:block">EduSense</span>
            </div>

            {/* Navigation Links */}
            <nav className="flex space-x-1 sm:space-x-4">
              {navItems.map((item) => {
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive 
                        ? 'bg-primary/10 text-primary' 
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }`}
                  >
                    <item.icon className="w-4 h-4" />
                    <span className="hidden sm:inline">{item.label}</span>
                  </Link>
                );
              })}
            </nav>

            {/* User Actions */}
            <div className="flex items-center gap-3">
              <NotificationCenter />

              {/* Profile Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setProfileOpen(!profileOpen)}
                  className="flex items-center gap-2 cursor-pointer rounded-full focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 transition-all"
                  aria-label="Open profile menu"
                  id="profile-menu-button"
                >
                  {currentUser?.avatarUrl ? (
                    <img
                      src={currentUser.avatarUrl}
                      alt="Avatar"
                      className="w-9 h-9 rounded-full object-cover border-2 border-emerald-200 hover:border-emerald-400 transition-colors"
                    />
                  ) : (
                    <div className="w-9 h-9 rounded-full bg-emerald-100 border-2 border-emerald-200 flex items-center justify-center text-emerald-700 hover:border-emerald-400 transition-colors">
                      <span className="text-sm font-bold uppercase">{(currentUser?.fullName || 'User').charAt(0)}</span>
                    </div>
                  )}
                </button>

                {profileOpen && (
                  <>
                    {/* Backdrop overlay to close dropdown on outside click */}
                    <div className="fixed inset-0 z-40" onClick={() => setProfileOpen(false)} />
                    
                    {/* Dropdown menu */}
                    <div className="absolute right-0 top-12 z-50 w-64 rounded-xl border bg-white shadow-xl origin-top-right animate-in fade-in zoom-in-95 duration-200">
                      {/* User info header */}
                      <div className="px-4 py-3 border-b">
                        <p className="text-sm font-semibold text-gray-900">{currentUser?.fullName || 'User'}</p>
                        <p className="text-xs text-gray-500 mt-0.5">{currentUser?.email || ''}</p>
                      </div>

                      {/* Menu items */}
                      <div className="py-1">
                        <Link
                          to="/student/profile"
                          onClick={() => setProfileOpen(false)}
                          className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                        >
                          <User className="w-4 h-4 text-gray-400" />
                          My Profile
                        </Link>
                        <Link
                          to="/student/settings"
                          onClick={() => setProfileOpen(false)}
                          className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                        >
                          <Settings className="w-4 h-4 text-gray-400" />
                          Settings
                        </Link>
                      </div>

                      {/* Logout */}
                      <div className="border-t py-1">
                        <button
                          onClick={handleLogout}
                          className="flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors w-full text-left cursor-pointer"
                          id="logout-button"
                        >
                          <LogOut className="w-4 h-4" />
                          Logout
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>

          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

    </div>
  );
}


