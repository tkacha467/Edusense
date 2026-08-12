import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { User, AuthSession } from '../types';
import { 
  login as apiLogin, 
  register as apiRegister,
  logout as apiLogout,
  forgotPassword as apiForgotPassword,
  verifyOtp as apiVerifyOtp,
  resetPassword as apiResetPassword,
  updateProfile as apiUpdateProfile
} from '../api/authApi';
import { useToast } from './ToastContext';

interface AuthContextType {
  currentUser: User | null;
  role: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, pass: string, rememberMe: boolean, expectedRole?: 'student' | 'teacher') => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => Promise<void>;
  forgotPassword: (email: string) => Promise<void>;
  verifyOtp: (email: string, otp: string) => Promise<boolean>;
  resetPassword: (email: string, newPassword: string) => Promise<void>;
  restoreSession: () => void;
  updateProfile: (updates: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  const restoreSession = () => {
    setLoading(true);
    try {
      // 1. Check sessionStorage (highest priority - active tab session)
      let stored = sessionStorage.getItem('edu_session');
      
      // 2. Fallback to localStorage (remember me session)
      if (!stored) {
        stored = localStorage.getItem('edu_session');
      }

      if (stored) {
        const session: AuthSession = JSON.parse(stored);
        if (session.expiresAt > Date.now()) {
          setCurrentUser(session.user);
        } else {
          // Auto logout after expiration
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

  const login = async (email: string, pass: string, rememberMe: boolean, expectedRole?: 'student' | 'teacher') => {
    const session = await apiLogin(email, pass, expectedRole);
    
    // Clear any old sessions
    sessionStorage.removeItem('edu_session');
    localStorage.removeItem('edu_session');

    // Store based on Remember Me
    if (rememberMe) {
      localStorage.setItem('edu_session', JSON.stringify(session));
    } else {
      sessionStorage.setItem('edu_session', JSON.stringify(session));
    }
    
    setCurrentUser(session.user);
  };

  const register = async (userData: any) => {
    await apiRegister(userData);
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
      setCurrentUser(null);
      showToast('Logged out successfully', 'success');
    }
  };

  const forgotPassword = async (email: string) => {
    const res = await apiForgotPassword(email);
    showToast(res.message, 'info');
  };

  const verifyOtp = async (email: string, otp: string) => {
    return await apiVerifyOtp(email, otp);
  };

  const resetPassword = async (email: string, newPassword: string) => {
    await apiResetPassword(email, newPassword);
    showToast('Password reset successfully. Please login.', 'success');
  };

  const updateProfile = async (updates: Partial<User>) => {
    if (!currentUser) return;
    const updatedUser = await apiUpdateProfile(currentUser.id, updates);
    setCurrentUser(updatedUser);
    
    // Also update session in Storage
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
      verifyOtp,
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


