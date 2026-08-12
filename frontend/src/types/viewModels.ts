import type { Notification, StudentProfile, TeacherProfile, PredictionResult } from './index';

export interface StudentDashboardViewModel {
  profile: StudentProfile;
  learningState: 'NEW' | 'ONBOARDING' | 'AI_ENABLED';
  streak: number;
  minutesToday: number;
  completedTopics: string[];
  studyPlan: Array<{ title: string; type: string; time: string; status: string }>;
  alerts: Array<{ topic: string; retention: number }>;
  predictions: PredictionResult[];
  unreadNotificationsCount: number;
}

export interface FacultyDashboardViewModel {
  profile: TeacherProfile;
  activeStudents: number;
  atRiskStudents: number;
  averageClassRetention: number;
  recentActivity: Array<{ id: string; studentName: string; action: string; time: string }>;
  unreadNotificationsCount: number;
}

export interface AssessmentViewModel {
  sessionId: string;
  skillName: string;
  currentQuestionIndex: number;
  totalQuestions: number;
  timeRemainingSeconds: number;
  difficulty: number;
  currentQuestion: {
    text: string;
    options: string[];
  };
}
