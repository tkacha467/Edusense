import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { assessmentService } from '../AssessmentService';

export function useAssessment(sessionId?: string) {
  const queryClient = useQueryClient();

  const generateSession = useMutation({
    mutationFn: (data: { subjectId: string; topicId?: string; difficulty?: string; totalQuestions?: number }) => 
      assessmentService.generateSession(data.subjectId, data.topicId, data.difficulty, data.totalQuestions),
  });

  const startSession = useMutation({
    mutationFn: (sid: string) => assessmentService.startSession(sid),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['assessmentQuestions', variables] });
    }
  });

  const { data: questions, isLoading: isLoadingQuestions, error: questionsError } = useQuery({
    queryKey: ['assessmentQuestions', sessionId],
    queryFn: () => assessmentService.getQuestions(sessionId!),
    enabled: !!sessionId,
  });

  const submitAssessment = useMutation({
    mutationFn: (data: { sessionId: string; responses: any[] }) => 
      assessmentService.submitAssessment(data.sessionId, data.responses),
    onSuccess: (result) => {
      // Invalidate queries so Dashboard and Revisions refresh immediately
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['knowledgeProfile'] });
      queryClient.invalidateQueries({ queryKey: ['studyPlans'] });
    }
  });

  return {
    generateSession,
    startSession,
    questions,
    isLoadingQuestions,
    questionsError,
    submitAssessment
  };
}
