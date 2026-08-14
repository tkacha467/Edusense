import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { assessmentSessionApi } from '../api/assessmentSessionApi';
import { AssessmentSessionService } from '../services/AssessmentSessionService';
import type { 
  AssessmentSession, 
  AssessmentSessionCreatePayload 
} from '../types/assessmentSession';

export function useAssessmentSession(sessionId?: string) {
  return useQuery<AssessmentSession, Error>({
    queryKey: ['assessmentSession', sessionId],
    queryFn: () => assessmentSessionApi.getSession(sessionId!),
    enabled: !!sessionId,
    retry: 1,
    staleTime: 5000,
  });
}

export function useCreateSession() {
  const queryClient = useQueryClient();

  return useMutation<AssessmentSession, Error, AssessmentSessionCreatePayload>({
    mutationFn: (payload) => AssessmentSessionService.initializeSession(payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['assessmentSession'] });
      queryClient.invalidateQueries({ queryKey: ['assessmentHistory'] });
      queryClient.invalidateQueries({ queryKey: ['activeAssessmentSession'] });
    }
  });
}

export function useResumeSession() {
  return useQuery<AssessmentSession | null, Error>({
    queryKey: ['activeAssessmentSession'],
    queryFn: () => AssessmentSessionService.recoverActiveSession(),
    retry: 1,
    staleTime: 30000,
  });
}

export function useCancelSession() {
  const queryClient = useQueryClient();

  return useMutation<AssessmentSession, Error, string>({
    mutationFn: (sessionId) => AssessmentSessionService.cancelSession(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessmentSession'] });
      queryClient.invalidateQueries({ queryKey: ['assessmentHistory'] });
      queryClient.invalidateQueries({ queryKey: ['activeAssessmentSession'] });
    }
  });
}

export function useCompleteSession() {
  const queryClient = useQueryClient();

  return useMutation<any, Error, { sessionId: string; responses: any[] }>({
    mutationFn: (data) => AssessmentSessionService.completeSession(data.sessionId, data.responses),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessmentSession'] });
      queryClient.invalidateQueries({ queryKey: ['assessmentHistory'] });
      queryClient.invalidateQueries({ queryKey: ['activeAssessmentSession'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardData'] });
    }
  });
}
