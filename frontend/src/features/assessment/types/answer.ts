export interface AssessmentAnswer {
  question_id: string;
  selected_option_id: string;
  time_taken_seconds?: number;
}

export type AssessmentResponses = Record<string, string>; // Maps questionId to selectedOptionId
