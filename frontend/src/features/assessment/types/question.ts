export interface QuestionOption {
  id: string;
  option_label: string;
  option_text: string;
  order_index: number;
}

export interface Question {
  id: string;
  question_text: string;
  question_type: 'MCQ' | 'TEXT';
  difficulty_level: 'EASY' | 'MEDIUM' | 'HARD';
  marks: number;
  hint?: string;
  order_index: number;
  options: QuestionOption[];
}
