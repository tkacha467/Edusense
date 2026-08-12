export type SkillLevel = 'Beginner' | 'Intermediate' | 'Advanced';
export type LearningStyle = 'Visual' | 'Reading' | 'Practice' | 'Mixed';
export type LearningGoal = 'Placement' | 'Exam' | 'Interview' | 'Upskilling' | 'Research';

export interface LearningPreferences {
  id: string;
  userId: string;
  institution: string;
  semester: string;
  branch: string;
  preferredLanguage: string;
  subjects: string[];
  skills: string[];
  currentSkillLevel: SkillLevel;
  learningGoal: LearningGoal;
  weeklyStudyHours: number;
  learningStyle: LearningStyle;
  createdAt: string;
  updatedAt: string;
}

export interface Subject {
  id: string;
  name: string;
  description: string;
  icon?: string;
}

export interface Skill {
  id: string;
  subjectId: string;
  name: string;
  description: string;
}

export interface GeneratedQuestion {
  id: string;
  assessmentSessionId: string;
  skillId: string;
  difficulty: number; // 1-10
  questionText: string;
  options: string[];
  correctOptionIndex: number;
  explanation: string;
  hint: string;
}

export interface StudentResponse {
  id: string;
  assessmentSessionId: string;
  questionId: string;
  selectedOptionIndex: number;
  isCorrect: boolean;
  timeSpentSeconds: number;
  createdAt: string;
}

export interface AssessmentSession {
  id: string;
  userId: string;
  subjectId: string;
  skillId: string;
  targetDifficulty: number;
  status: 'pending' | 'in_progress' | 'completed';
  score?: number;
  startedAt: string;
  completedAt?: string;
}

export interface KnowledgeProfile {
  id: string;
  userId: string;
  skillId: string;
  masteryLevel: number; // 0-100
  lastAssessedAt: string;
  
  // Extended metadata for AI/ML tracking
  retentionScore: number;
  confidenceScore: number;
  revisionCount: number;
  predictionMetadata?: {
    nextOptimalReview: string;
    decayRate: number;
    forgetProbability: number;
    predictionTimestamp: string;
  };
  masteryHistory?: Array<{
    date: string;
    level: number;
  }>;
}

export interface StudentActivity {
  id: string;
  userId: string;
  activityType: 'LOGIN' | 'ASSESSMENT' | 'STUDY' | 'REVIEW' | 'MODULE_COMPLETE';
  durationMinutes?: number;
  metadata?: Record<string, any>;
  createdAt: string;
}

export interface PredictionResult {
  id: string;
  userId: string;
  skillId: string;
  forgetProbability: number; // 0-100
  retentionStrength: number; // 0-100
  predictedDecayDate: string;
  createdAt: string;
}

export interface RecommendationPlan {
  id: string;
  userId: string;
  priorityTopics: Array<{ skillId: string; reason: string; urgency: 'high' | 'medium' | 'low' }>;
  reviewSchedule: Array<{ date: string; skillId: string }>;
  learningSuggestions: string[];
  createdAt: string;
}

export interface StudySession {
  id: string;
  userId: string;
  durationMinutes: number;
  focusSkillIds: string[];
  startedAt: string;
  completedAt: string;
}



