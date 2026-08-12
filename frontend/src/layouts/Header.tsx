import { useAuth } from '../contexts/AuthContext';
import React, { useState } from 'react';
import { Bell, User as UserIcon, LogOut, Settings } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { NotificationCenter } from '../features/notifications/components/NotificationCenter';
import { GlobalSearch } from './GlobalSearch';
import { Link, useNavigate } from 'react-router-dom';

export function Header() {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const [profileOpen, setProfileOpen] = useState(false);

  const handleLogout = async () => {
    setProfileOpen(false);
    await logout();
    navigate('/');
  };

  return (
    <header className="flex h-16 shrink-0 items-center gap-x-4 border-b bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
      <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
        <div className="relative flex flex-1 items-center">
          <GlobalSearch />
        </div>
        <div className="flex items-center gap-x-4 lg:gap-x-6">
          
          <NotificationCenter />
          
          {/* Separator */}
          <div className="hidden lg:block lg:h-6 lg:w-px lg:bg-gray-200" aria-hidden="true" />
          
          {/* Profile dropdown */}
          <div className="relative flex items-center gap-x-4">
            <button
              onClick={() => setProfileOpen(!profileOpen)}
              className="flex items-center gap-x-3 cursor-pointer rounded-full focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 transition-all"
              aria-label="Open profile menu"
              id="header-profile-menu-button"
            >
              {currentUser?.avatarUrl ? (
                <img
                  src={currentUser.avatarUrl}
                  alt="Avatar"
                  className="h-8 w-8 rounded-full object-cover"
                />
              ) : (
                <div className="rounded-full bg-gray-100 h-8 w-8 flex items-center justify-center">
                  <UserIcon className="h-4 w-4 text-gray-500" aria-hidden="true" />
                </div>
              )}
              <span className="hidden lg:flex lg:items-center">
                <span className="text-sm font-semibold leading-6 text-gray-900" aria-hidden="true">
                  {currentUser?.fullName}
                </span>
              </span>
            </button>

            {profileOpen && (
              <>
                {/* Backdrop overlay */}
                <div className="fixed inset-0 z-40" onClick={() => setProfileOpen(false)} />
                
                {/* Dropdown menu */}
                <div className="absolute right-0 top-12 z-50 w-64 rounded-xl border bg-white shadow-xl origin-top-right animate-in fade-in zoom-in-95 duration-200">
                  {/* User info */}
                  <div className="px-4 py-3 border-b">
                    <p className="text-sm font-semibold text-gray-900">{currentUser?.fullName || 'User'}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{currentUser?.email || ''}</p>
                  </div>

                  {/* Menu items */}
                  <div className="py-1">
                    <Link
                      to="/profile"
                      onClick={() => setProfileOpen(false)}
                      className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      <UserIcon className="w-4 h-4 text-gray-400" />
                      My Profile
                    </Link>
                    <Link
                      to="/settings"
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
                      id="header-logout-button"
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
    </header>
  );
}
