import { useMutation, useQueryClient } from '@tanstack/react-query';
import { assessmentApi } from '../api/assessmentApi';
import { AssessmentAnswer } from '../types/answer';

export function useSaveAnswer(sessionId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (answer: AssessmentAnswer) => assessmentApi.saveAnswer(sessionId, answer),
    onSuccess: (_, variables) => {
      // Optimistically update responses cache
      queryClient.setQueryData(['assessmentResponses', sessionId], (old: Record<string, string> = {}) => {
        return {
          ...old,
          [variables.question_id]: variables.selected_option_id
        };
      });
    }
  });
}
