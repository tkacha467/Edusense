import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { plannerApi, type StudyTask, type StudyPlan } from '../../../api/plannerApi';

export function usePlanner() {
  const queryClient = useQueryClient();

  const todayTasksQuery = useQuery<StudyTask[], Error>({
    queryKey: ['planner', 'todayTasks'],
    queryFn: plannerApi.getTodayTasks,
    staleTime: 30 * 1000,
  });

  const upcomingTasksQuery = useQuery<StudyTask[], Error>({
    queryKey: ['planner', 'upcomingTasks'],
    queryFn: plannerApi.getUpcomingTasks,
    staleTime: 60 * 1000,
  });

  const studyPlansQuery = useQuery<StudyPlan[], Error>({
    queryKey: ['planner', 'studyPlans'],
    queryFn: plannerApi.getStudyPlans,
    staleTime: 2 * 60 * 1000,
  });

  const generatePlanMutation = useMutation({
    mutationFn: (subjectId?: string) => plannerApi.generatePlan(subjectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['planner'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardData'] });
    }
  });

  const completeTaskMutation = useMutation({
    mutationFn: (taskId: string) => plannerApi.completeTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['planner'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardData'] });
    }
  });

  const skipTaskMutation = useMutation({
    mutationFn: (taskId: string) => plannerApi.skipTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['planner'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardData'] });
    }
  });

  return {
    todayTasksQuery,
    upcomingTasksQuery,
    studyPlansQuery,
    generatePlanMutation,
    completeTaskMutation,
    skipTaskMutation
  };
}
