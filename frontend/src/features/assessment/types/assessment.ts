import { Question } from './question';

export interface AssessmentDetails {
  id: string;
  student_id: string;
  subject_id: string;
  title: string;
  total_questions: number;
  time_limit_seconds: number;
  status: 'pending' | 'in_progress' | 'completed' | 'abandoned';
  questions: Question[];
  started_at?: string;
  completed_at?: string;
}

export interface AssessmentResult {
  assessment_session_id: string;
  total_questions: number;
  correct_answers: number;
  scored_marks: number;
  total_marks: number;
  percentage: number;
  time_taken_seconds: number;
}
