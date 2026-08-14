import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { assessmentApi } from '../api/assessmentApi';
import { assessmentSessionApi } from '../api/assessmentSessionApi';
import type { AssessmentAnswer } from '../types/answer';
import type { AssessmentResult } from '../types/assessment';
import type { AssessmentSession } from '../types/assessmentSession';

export function useAssessment(sessionId?: string) {
  const queryClient = useQueryClient();

  const { data: questions, isLoading: isLoadingQuestions, error: questionsError } = useQuery({
    queryKey: ['assessmentQuestions', sessionId],
    queryFn: () => assessmentApi.getQuestions(sessionId!),
    enabled: !!sessionId,
    staleTime: Infinity,
  });

  const generateSession = useMutation<AssessmentSession, Error, { subjectId: string; totalQuestions?: number; topicId?: string; difficulty?: string }>({
    mutationFn: (data) => assessmentSessionApi.createSession({
      subjectId: data.subjectId,
      totalQuestions: data.totalQuestions || 5,
      topicId: data.topicId,
      difficulty: data.difficulty || 'adaptive'
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessmentSession'] });
      queryClient.invalidateQueries({ queryKey: ['assessmentHistory'] });
      queryClient.invalidateQueries({ queryKey: ['activeAssessmentSession'] });
    }
  });

  const startSession = useMutation<AssessmentSession, Error, string>({
    mutationFn: (id) => assessmentSessionApi.startSession(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessmentSession'] });
      queryClient.invalidateQueries({ queryKey: ['activeAssessmentSession'] });
    }
  });

  const submitAssessment = useMutation<AssessmentResult, Error, { sessionId: string; responses: AssessmentAnswer[] }>({
    mutationFn: (data) => assessmentApi.submitAssessment(data.sessionId, data.responses),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessmentSession'] });
      queryClient.invalidateQueries({ queryKey: ['assessmentHistory'] });
      queryClient.invalidateQueries({ queryKey: ['activeAssessmentSession'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardData'] });
    }
  });

  // Restore draft answers from local storage
  const getDraftResponses = (sid: string): Record<string, string> => {
    const raw = localStorage.getItem(`edusense_draft_answers_${sid}`);
    return raw ? JSON.parse(raw) : {};
  };

  return {
    questions,
    isLoadingQuestions,
    questionsError,
    generateSession,
    startSession,
    submitAssessment,
    getDraftResponses
  };
}
