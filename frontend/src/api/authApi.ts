import apiClient, { ApiError } from './apiClient';
import type { AuthSession, User } from '../types';

export const login = async (email: string, password: string, expectedRole?: 'student' | 'teacher'): Promise<AuthSession> => {
  try {
    // Generate dev token for user login sync
    const devToken = `dev-token-uid_${email.replace(/[^a-zA-Z0-9]/g, '_')}`;
    localStorage.setItem('edu_auth_token', devToken);

    const response = await apiClient.post('/auth/login', {}, {
      headers: { Authorization: `Bearer ${devToken}` }
    });

    const data = response.data;
    const userRole = data.user.role;
    if (expectedRole && userRole !== expectedRole) {
      throw new ApiError(`Please use the ${userRole} login portal.`, 403);
    }

    const session: AuthSession = {
      token: devToken,
      user: {
        id: data.user.id,
        email: data.user.email,
        fullName: data.user.display_name || data.user.email.split('@')[0],
        role: data.user.role === 'student' ? 'student' : 'teacher',
        createdAt: data.user.created_at,
        onboardingCompleted: data.onboarding_completed
      },
      expiresAt: Date.now() + 24 * 60 * 60 * 1000
    };

    localStorage.setItem('edu_auth_token', devToken);
    localStorage.setItem('edu_user', JSON.stringify(session.user));
    return session;
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(err.message || 'Login failed', 401);
  }
};

export interface RegisterUserData {
  email: string;
  fullName?: string;
  name?: string;
  password?: string;
  role?: 'student' | 'teacher' | 'admin';
  department?: string;
}

export const register = async (userData: RegisterUserData): Promise<User> => {
  try {
    const uid = `uid_${userData.email.replace(/[^a-zA-Z0-9]/g, '_')}`;
    const devToken = `dev-token-${uid}`;

    const response = await apiClient.post('/auth/register', {
      firebase_uid: uid,
      email: userData.email,
      display_name: userData.fullName || userData.name || userData.email.split('@')[0],
      role: userData.role || 'student'
    }, {
      headers: { Authorization: `Bearer ${devToken}` }
    });

    const data = response.data;
    const user: User = {
      id: data.id,
      email: data.email,
      fullName: data.display_name || data.email.split('@')[0],
      role: data.role === 'student' ? 'student' : 'teacher',
      createdAt: data.created_at,
      onboardingCompleted: false
    };

    localStorage.setItem('edu_auth_token', devToken);
    localStorage.setItem('edu_user', JSON.stringify(user));
    return user;
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(err.message || 'Registration failed', 400);
  }
};

export const logout = async (userId: string): Promise<void> => {
  localStorage.removeItem('edu_auth_token');
  localStorage.removeItem('edu_user');
};

export const forgotPassword = async (email: string): Promise<{ success: boolean; message: string }> => {
  return { success: true, message: 'If an account exists, verification instructions have been sent.' };
};

export const verifyOtp = async (email: string, otp: string): Promise<boolean> => {
  return true;
};

export const resetPassword = async (email: string, newPassword: string): Promise<void> => {
  return;
};

export const updateProfile = async (userId: string, updates: Partial<User>): Promise<User> => {
  const stored = localStorage.getItem('edu_user');
  const user = stored ? JSON.parse(stored) : { id: userId, email: '', name: '', role: 'student' };
  
  // Choose endpoint based on role (student or teacher)
  const endpoint = user.role === 'teacher' ? '/faculty/me/profile' : '/students/me/profile';
  
  try {
    // Note: Profile update endpoints usually take profile-specific fields. 
    // Here we pass the updates, which might be ignored by backend if they are User fields.
    await apiClient.put(endpoint, updates);
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(err.message || 'Profile update failed', 400);
  }
  
  const updated = { ...user, ...updates };
  localStorage.setItem('edu_user', JSON.stringify(updated));
  return updated;
};
