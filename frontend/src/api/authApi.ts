import apiClient, { ApiError } from './apiClient';
import type { AuthSession, User, UserRoleType } from '../types';
import { UserRole } from '../types';

export const login = async (email: string, password: string, expectedRole?: UserRoleType): Promise<AuthSession> => {
  try {
    // Generate dev token for user login sync
    const devToken = `dev-token-uid_${email.replace(/[^a-zA-Z0-9]/g, '_')}`;
    localStorage.setItem('edu_auth_token', devToken);

    const response = await apiClient.post('/auth/login', {}, {
      headers: { Authorization: `Bearer ${devToken}` }
    });

    const data = response.data;
    const userRole = data.user.role; // This will be 'faculty' or 'student'
    if (expectedRole && userRole !== expectedRole && !(expectedRole === UserRole.FACULTY && (userRole === UserRole.ADMIN || userRole === UserRole.SUPER_ADMIN))) {
      throw new ApiError(`Please use the ${userRole === UserRole.FACULTY ? 'teacher' : userRole} login portal.`, 403);
    }

    const profileId = data.profile_id || data.user.id;
    const userId = data.user.id;

    const session: AuthSession = {
      token: devToken,
      user: {
        id: profileId,
        profileId: profileId,
        userId: userId,
        email: data.user.email,
        fullName: data.user.display_name || data.user.email.split('@')[0],
        role: data.user.role === UserRole.STUDENT ? UserRole.STUDENT : UserRole.FACULTY,
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
    const message = err?.response?.data?.detail || err?.response?.data?.message || err?.message || 'Login failed';
    throw new ApiError(message, err?.response?.status || 401);
  }
};

export interface RegisterUserData {
  email: string;
  fullName?: string;
  name?: string;
  password?: string;
  role?: UserRoleType;
  department?: string;
  institution_id?: string;
  department_id?: string;
}

export const register = async (userData: RegisterUserData): Promise<AuthSession> => {
  try {
    const uid = `uid_${userData.email.replace(/[^a-zA-Z0-9]/g, '_')}`;
    const devToken = `dev-token-${uid}`;

    const response = await apiClient.post('/auth/register', {
      firebase_uid: uid,
      email: userData.email,
      display_name: userData.fullName || userData.name || userData.email.split('@')[0],
      role: userData.role || UserRole.STUDENT,
      institution_id: userData.institution_id,
      department_id: userData.department_id
    }, {
      headers: { Authorization: `Bearer ${devToken}` }
    });

    const data = response.data;
    const profileId = data.profile_id || data.user.id;
    const userId = data.user.id;

    const session: AuthSession = {
      token: devToken,
      user: {
        id: profileId,
        profileId: profileId,
        userId: userId,
        email: data.user.email,
        fullName: data.user.display_name || data.user.email.split('@')[0],
        role: data.user.role === UserRole.STUDENT ? UserRole.STUDENT : UserRole.FACULTY,
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
    const message = err?.response?.data?.detail || err?.response?.data?.message || err?.message || 'Registration failed';
    throw new ApiError(message, err?.response?.status || 400);
  }
};

export const getCurrentUser = async (): Promise<AuthSession> => {
  try {
    const token = localStorage.getItem('edu_auth_token') || sessionStorage.getItem('edu_auth_token');
    const response = await apiClient.get('/auth/me', {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    });
    const data = response.data;
    const profileId = data.profile_id || data.user.id;
    const userId = data.user.id;

    const session: AuthSession = {
      token: token || '',
      user: {
        id: profileId,
        profileId: profileId,
        userId: userId,
        email: data.user.email,
        fullName: data.user.display_name || data.user.email.split('@')[0],
        role: data.user.role === UserRole.STUDENT ? UserRole.STUDENT : UserRole.FACULTY,
        createdAt: data.user.created_at,
        onboardingCompleted: data.onboarding_completed
      },
      expiresAt: Date.now() + 24 * 60 * 60 * 1000
    };
    localStorage.setItem('edu_user', JSON.stringify(session.user));
    return session;
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    const message = err?.response?.data?.detail || err?.response?.data?.message || err?.message || 'Failed to fetch current user';
    throw new ApiError(message, err?.response?.status || 401);
  }
};

export const logout = async (userId: string): Promise<void> => {
  localStorage.removeItem('edu_auth_token');
  localStorage.removeItem('edu_user');
  localStorage.removeItem('edu_session');
  sessionStorage.removeItem('edu_session');
};

export const forgotPassword = async (email: string): Promise<{ success: boolean; message: string }> => {
  return { success: true, message: 'If an account exists, verification instructions have been sent.' };
};

export const resetPassword = async (email: string, newPassword: string): Promise<void> => {
  return;
};

export const updateProfile = async (userId: string, updates: Partial<User>): Promise<User> => {
  const stored = localStorage.getItem('edu_user');
  const user = stored ? JSON.parse(stored) : { id: userId, email: '', name: '', role: 'student' };
  
  // Choose endpoint based on role (student or teacher)
  const endpoint = user.role === UserRole.FACULTY ? '/faculty/me/profile' : '/students/me/profile';
  
  try {
    // Note: Profile update endpoints usually take profile-specific fields. 
    // Here we pass the updates, which might be ignored by backend if they are User fields.
    await apiClient.put(endpoint, updates);
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    const message = err?.response?.data?.detail || err?.response?.data?.message || err?.message || 'Profile update failed';
    throw new ApiError(message, err?.response?.status || 400);
  }
  
  const updated = { ...user, ...updates };
  localStorage.setItem('edu_user', JSON.stringify(updated));
  return updated;
};
