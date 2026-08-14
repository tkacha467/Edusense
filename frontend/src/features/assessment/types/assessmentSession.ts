export type AssessmentSessionStatus = 'pending' | 'in_progress' | 'completed' | 'abandoned';
export type AssessmentDifficulty = 'beginner' | 'intermediate' | 'advanced';
export type GenerationMethod = 'ai' | 'curriculum';

export interface AssessmentSession {
  id: string;
  student_id: string;
  subject_id: string;
  topic_id?: string;
  title: string;
  difficulty_level: AssessmentDifficulty;
  total_questions: number;
  time_limit_seconds?: number;
  generation_method: GenerationMethod;
  status: AssessmentSessionStatus;
  scored_marks?: number;
  percentage?: number;
  time_taken_seconds?: number;
  started_at?: string;
  completed_at?: string;
}

export interface AssessmentSessionCreatePayload {
  subjectId: string;
  topicId?: string;
  difficulty?: AssessmentDifficulty;
  totalQuestions?: number;
}
