import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { User, AuthSession, UserRoleType } from '../types';
import { 
  login as apiLogin, 
  register as apiRegister,
  logout as apiLogout,
  forgotPassword as apiForgotPassword,
  resetPassword as apiResetPassword,
  updateProfile as apiUpdateProfile,
  getCurrentUser as apiGetCurrentUser
} from '../api/authApi';
import { useToast } from './ToastContext';

interface AuthContextType {
  currentUser: User | null;
  role: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, pass: string, rememberMe: boolean, expectedRole?: UserRoleType) => Promise<void>;
  register: (userData: any) => Promise<AuthSession>;
  logout: () => Promise<void>;
  forgotPassword: (email: string) => Promise<void>;
  resetPassword: (email: string, newPassword: string) => Promise<void>;
  restoreSession: () => void;
  updateProfile: (updates: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  const restoreSession = async () => {
    setLoading(true);
    try {
      let stored = sessionStorage.getItem('edu_session');
      if (!stored) {
        stored = localStorage.getItem('edu_session');
      }

      if (stored) {
        const session: AuthSession = JSON.parse(stored);
        if (session.expiresAt > Date.now()) {
          if (!session.user.profileId) {
            try {
              const freshSession = await apiGetCurrentUser();
              setCurrentUser(freshSession.user);
              if (localStorage.getItem('edu_session')) {
                localStorage.setItem('edu_session', JSON.stringify(freshSession));
              } else {
                sessionStorage.setItem('edu_session', JSON.stringify(freshSession));
              }
              setLoading(false);
              return;
            } catch (err) {
              console.warn("Failed to refresh user info via /auth/me", err);
            }
          }
          setCurrentUser(session.user);
        } else {
          sessionStorage.removeItem('edu_session');
          localStorage.removeItem('edu_session');
          setCurrentUser(null);
        }
      } else {
        setCurrentUser(null);
      }
    } catch (e) {
      console.error('Failed to restore session', e);
      setCurrentUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    restoreSession();
  }, []);

  const login = async (email: string, pass: string, rememberMe: boolean, expectedRole?: UserRoleType) => {
    const session = await apiLogin(email, pass, expectedRole);
    
    sessionStorage.removeItem('edu_session');
    localStorage.removeItem('edu_session');
    sessionStorage.removeItem('edu_auth_token');
    localStorage.removeItem('edu_auth_token');

    if (rememberMe) {
      localStorage.setItem('edu_session', JSON.stringify(session));
      localStorage.setItem('edu_auth_token', session.token);
    } else {
      sessionStorage.setItem('edu_session', JSON.stringify(session));
      sessionStorage.setItem('edu_auth_token', session.token);
    }
    
    setCurrentUser(session.user);
  };

  const register = async (userData: any): Promise<AuthSession> => {
    const session = await apiRegister(userData);
    
    sessionStorage.removeItem('edu_session');
    localStorage.removeItem('edu_session');
    sessionStorage.removeItem('edu_auth_token');
    localStorage.removeItem('edu_auth_token');

    localStorage.setItem('edu_session', JSON.stringify(session));
    localStorage.setItem('edu_auth_token', session.token);
    setCurrentUser(session.user);
    return session;
  };

  const logout = async () => {
    try {
      if (currentUser) {
        await apiLogout(currentUser.id);
      }
    } catch (e) {
      console.error(e);
    } finally {
      sessionStorage.removeItem('edu_session');
      localStorage.removeItem('edu_session');
      sessionStorage.removeItem('edu_auth_token');
      localStorage.removeItem('edu_auth_token');
      localStorage.removeItem('edu_user');
      setCurrentUser(null);
      showToast('Logged out successfully', 'success');
    }
  };

  const forgotPassword = async (email: string) => {
    const res = await apiForgotPassword(email);
    showToast(res.message, 'info');
  };

  const resetPassword = async (email: string, newPassword: string) => {
    await apiResetPassword(email, newPassword);
    showToast('Password reset successfully. Please login.', 'success');
  };

  const updateProfile = async (updates: Partial<User>) => {
    if (!currentUser) return;
    const updatedUser = await apiUpdateProfile(currentUser.id, updates);
    setCurrentUser(updatedUser);
    
    const sessionKey = 'edu_session';
    const stored = sessionStorage.getItem(sessionKey) || localStorage.getItem(sessionKey);
    if (stored) {
      const session = JSON.parse(stored);
      session.user = updatedUser;
      if (sessionStorage.getItem(sessionKey)) {
        sessionStorage.setItem(sessionKey, JSON.stringify(session));
      } else {
        localStorage.setItem(sessionKey, JSON.stringify(session));
      }
    }
  };

  return (
    <AuthContext.Provider value={{
      currentUser,
      role: currentUser?.role || null,
      isAuthenticated: !!currentUser,
      loading,
      login,
      register,
      logout,
      forgotPassword,
      resetPassword,
      restoreSession,
      updateProfile
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};


