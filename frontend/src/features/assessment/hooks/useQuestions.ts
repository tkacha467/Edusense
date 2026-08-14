import { useQuery } from '@tanstack/react-query';
import { assessmentApi } from '../api/assessmentApi';
import type { Question } from '../types/question';

export function useQuestions(sessionId?: string) {
  return useQuery<Question[], Error>({
    queryKey: ['assessmentQuestions', sessionId],
    queryFn: () => assessmentApi.getQuestions(sessionId!),
    enabled: !!sessionId,
    retry: 1,
    staleTime: Infinity, // keep questions cached statically for the duration of session
  });
}
