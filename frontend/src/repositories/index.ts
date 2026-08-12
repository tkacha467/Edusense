import { ApiRepository } from './BaseRepository';
import type { 
  User, 
  LearningPreferences, 
  Subject, 
  Skill, 
  AssessmentSession, 
  GeneratedQuestion, 
  StudentResponse, 
  KnowledgeProfile, 
  PredictionResult, 
  RecommendationPlan, 
  StudySession, 
  Notification 
} from '../types';

export const UserRepository = new ApiRepository<User>('students');
export const PreferencesRepository = new ApiRepository<LearningPreferences>('onboarding/preferences');
export const SubjectRepository = new ApiRepository<Subject>('learning/subjects');
export const SkillRepository = new ApiRepository<Skill>('learning/skills');

export const AssessmentSessionRepository = new ApiRepository<AssessmentSession>('assessments');
export const QuestionRepository = new ApiRepository<GeneratedQuestion>('assessments/questions');
export const ResponseRepository = new ApiRepository<StudentResponse>('assessments/responses');

export const KnowledgeProfileRepository = new ApiRepository<KnowledgeProfile>('knowledge/profiles');
export const PredictionRepository = new ApiRepository<PredictionResult>('knowledge/at-risk');
export const RecommendationRepository = new ApiRepository<RecommendationPlan>('recommendations');

export const StudySessionRepository = new ApiRepository<StudySession>('study-plans');
export const NotificationRepository = new ApiRepository<Notification>('notifications');
