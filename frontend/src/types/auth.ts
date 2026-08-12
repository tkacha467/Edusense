export type Role = 'student' | 'teacher' | 'admin';

export interface User {
  id: string;
  email: string;
  fullName: string;
  role: Role;
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
  role: 'teacher';
  department: string;
  employeeId: string;
}

export interface AuthSession {
  token: string;
  user: User;
  expiresAt: number;
}

