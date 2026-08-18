export const UserRole = {
  STUDENT: 'student',
  FACULTY: 'faculty',
  ADMIN: 'admin',
  SUPER_ADMIN: 'super_admin'
} as const;

export type UserRoleType = typeof UserRole[keyof typeof UserRole];

export interface User {
  id: string;
  profileId?: string;
  userId?: string;
  email: string;
  fullName: string;
  role: UserRoleType;
  avatarUrl?: string;
  bio?: string;
  createdAt: string;
  lastLogin?: string;
  password?: string;
  onboardingCompleted?: boolean;
}

export type LearningState = 'NEW' | 'ACTIVE' | 'AI_ENABLED';

export interface StudentProfile extends User {
  role: 'student';
  grade?: string;
  schoolType?: string;
  skillsTracking?: string[];
  
  // Progress & Analytics Tracking
  learningState: LearningState;
  streak: number;
  minutesToday: number;
  completedTopics: string[];
  studyPlan: Array<{
    title: string;
    type: 'Practice' | 'Review' | 'Quiz' | 'Learn';
    time: string;
    status: 'ready' | 'urgent' | 'completed';
  }>;
  alerts: Array<{
    topic: string;
    retention: number;
  }>;
  predictions: Array<{
    name: string;
    retention: number;
  }>;
}

export interface TeacherProfile extends User {
  role: typeof UserRole.FACULTY;
  department: string;
  employeeId: string;
}

export interface AuthSession {
  token: string;
  user: User;
  expiresAt: number;
}

