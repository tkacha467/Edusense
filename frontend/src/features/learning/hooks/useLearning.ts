import { useQuery } from '@tanstack/react-query';
import { learningApi } from '../../../api/learningApi';

export function useSubjects() {
  return useQuery({
    queryKey: ['subjects'],
    queryFn: () => learningApi.getSubjects(),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
}

export function useTopics(subjectId: string | null) {
  return useQuery({
    queryKey: ['topics', subjectId],
    queryFn: () => learningApi.getTopics(subjectId!),
    enabled: !!subjectId,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
}

export function useSkills(topicId: string | null) {
  return useQuery({
    queryKey: ['skills', topicId],
    queryFn: () => learningApi.getSkills(topicId!),
    enabled: !!topicId,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
}
