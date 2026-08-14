import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '../../../components/ui/Card';
import { PlayCircle, CheckCircle, Flame, Calendar, Loader2, RefreshCw, XCircle, ArrowRight, BookOpen } from 'lucide-react';
import { Button } from '../../../components/ui/Button';
import { usePlanner } from '../hooks/usePlanner';
import { useSubjects } from '../../learning/hooks/useLearning';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../../../contexts/ToastContext';

export function StudyPlan() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  
  const {
    todayTasksQuery,
    upcomingTasksQuery,
    studyPlansQuery,
    generatePlanMutation,
    completeTaskMutation,
    skipTaskMutation
  } = usePlanner();

  const { data: subjects, isLoading: isLoadingSubjects } = useSubjects();
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>('');

  const { data: todayTasks, isLoading: isLoadingToday, isError: isErrorToday, refetch: refetchToday } = todayTasksQuery;
  const { data: studyPlans, isLoading: isLoadingPlans, isError: isErrorPlans, refetch: refetchPlans } = studyPlansQuery;

  const handleGeneratePlan = async () => {
    try {
      await generatePlanMutation.mutateAsync(selectedSubjectId || undefined);
      showToast('Personalized AI study plan generated successfully!', 'success');
    } catch (err) {
      console.error(err);
      showToast('Failed to generate study plan.', 'error');
    }
  };

  const handleCompleteTask = async (taskId: string) => {
    try {
      await completeTaskMutation.mutateAsync(taskId);
      showToast('Task marked as completed! Neural pathways reinforced.', 'success');
    } catch (err) {
      console.error(err);
      showToast('Failed to complete task.', 'error');
    }
  };

  const handleSkipTask = async (taskId: string) => {
    try {
      await skipTaskMutation.mutateAsync(taskId);
      showToast('Task skipped.', 'info');
    } catch (err) {
      console.error(err);
      showToast('Failed to skip task.', 'error');
    }
  };

  const isLoading = isLoadingToday || isLoadingPlans || generatePlanMutation.isPending;

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
        <p className="text-muted-foreground animate-pulse font-medium">Loading your adaptive study plan...</p>
      </div>
    );
  }

  if (isErrorToday || isErrorPlans) {
    return (
      <div className="p-8 max-w-lg mx-auto text-center space-y-4">
        <div className="bg-red-50 p-4 rounded-full w-16 h-16 flex items-center justify-center mx-auto border border-red-100">
          <XCircle className="w-8 h-8 text-red-600" />
        </div>
        <h3 className="text-xl font-bold text-gray-900">Failed to load study plan</h3>
        <p className="text-sm text-gray-500">
          We encountered an issue connecting to the adaptive recommendation backend.
        </p>
        <Button onClick={() => { refetchToday(); refetchPlans(); }} className="flex items-center gap-2 mx-auto">
          <RefreshCw className="w-4 h-4" /> Retry Connection
        </Button>
      </div>
    );
  }

  const hasPlans = studyPlans && studyPlans.length > 0;
  const hasTasks = todayTasks && todayTasks.length > 0;

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 flex items-center gap-3">
            <Calendar className="w-8 h-8 text-primary" /> Study Planner
          </h1>
          <p className="text-muted-foreground mt-1">
            AI-generated curriculum pacing and retrieval revision targets.
          </p>
        </div>
      </div>

      {!hasPlans ? (
        <Card className="border-dashed max-w-2xl mx-auto">
          <CardContent className="p-8 text-center flex flex-col items-center justify-center space-y-6">
            <div className="bg-primary/10 p-4 rounded-full">
              <Calendar className="w-12 h-12 text-primary" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">No Study Plan Active</h2>
              <p className="text-gray-500 mt-2 text-sm max-w-md mx-auto">
                Generate a personalized learning curriculum schedule. EduSense AI will prioritize your skills based on forget probability.
              </p>
            </div>

            <div className="w-full max-w-sm space-y-3">
              <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider text-left block">
                Select Course (Optional)
              </label>
              <select
                value={selectedSubjectId}
                onChange={(e) => setSelectedSubjectId(e.target.value)}
                className="flex h-10 w-full rounded-xl border border-gray-200 bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
              >
                <option value="">All Enrolled Courses</option>
                {subjects?.map((sub) => (
                  <option key={sub.id} value={sub.id}>
                    [{sub.code}] {sub.name}
                  </option>
                ))}
              </select>

              <Button 
                onClick={handleGeneratePlan} 
                disabled={generatePlanMutation.isPending} 
                className="w-full h-11 text-base rounded-xl font-semibold shadow-lg hover:shadow-primary/25"
              >
                {generatePlanMutation.isPending ? 'Generating Plan...' : 'Generate AI Study Plan'}
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Today's Tasks */}
          <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-extrabold text-gray-900">Today's Study Checklist</h2>
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wide bg-gray-100 px-3 py-1 rounded-full">
                {todayTasks?.filter(t => t.status === 'COMPLETED').length || 0} / {todayTasks?.length || 0} Tasks Done
              </span>
            </div>

            {!hasTasks ? (
              <Card className="border-dashed py-12 text-center flex flex-col items-center justify-center">
                <CheckCircle className="w-12 h-12 text-emerald-400 mb-3" />
                <h3 className="text-lg font-bold text-gray-900 mb-1">Checklist Completed!</h3>
                <p className="text-xs text-gray-500 max-w-xs mb-4">
                  No recommended study tasks remaining for today. Maintain your streak tomorrow.
                </p>
                <Button variant="outline" onClick={() => navigate('/student/assessment')} className="rounded-xl">
                  Take Custom Assessment
                </Button>
              </Card>
            ) : (
              <div className="space-y-4">
                {todayTasks.map((task) => {
                  const isCompleted = task.status === 'COMPLETED';
                  const isSkipped = task.status === 'SKIPPED';
                  
                  return (
                    <Card key={task.id} className={`overflow-hidden border-gray-100 transition-all ${isCompleted ? 'bg-gray-50/50 opacity-70' : 'bg-white hover:shadow-md'}`}>
                      <CardContent className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                        <div className="flex items-start gap-4">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${
                            isCompleted ? 'bg-emerald-50 text-emerald-600' :
                            task.priority === 'HIGH' ? 'bg-rose-50 text-rose-600' :
                            'bg-blue-50 text-blue-600'
                          }`}>
                            {isCompleted ? <CheckCircle className="w-5 h-5" /> : <BookOpen className="w-5 h-5" />}
                          </div>
                          
                          <div>
                            <h4 className={`font-bold text-base leading-tight ${isCompleted ? 'text-gray-400 line-through' : 'text-gray-900'}`}>
                              {task.title}
                            </h4>
                            <p className="text-xs text-gray-400 mt-1">
                              Priority: <span className={`font-semibold ${task.priority === 'HIGH' ? 'text-rose-600' : 'text-gray-600'}`}>{task.priority}</span>
                              {task.estimated_minutes && ` • Est: ${task.estimated_minutes} min`}
                            </p>
                          </div>
                        </div>

                        {!isCompleted && !isSkipped && (
                          <div className="flex items-center gap-2 sm:self-center self-end">
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              onClick={() => handleSkipTask(task.id)}
                              className="text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg text-xs"
                            >
                              Skip
                            </Button>
                            <Button 
                              size="sm" 
                              onClick={() => handleCompleteTask(task.id)}
                              className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-lg px-4"
                            >
                              Complete Task
                            </Button>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </div>

          {/* Active Study Plans Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            <h2 className="text-xl font-extrabold text-gray-900">Your Study Curriculums</h2>
            
            <div className="space-y-4">
              {studyPlans?.map((plan) => (
                <Card key={plan.id} className="border-gray-100 bg-white">
                  <CardHeader className="pb-2">
                    <span className="text-[10px] font-bold text-primary bg-primary/10 px-2 py-0.5 rounded uppercase tracking-wider self-start">
                      {plan.plan_type}
                    </span>
                    <CardTitle className="text-base font-bold mt-2">{plan.title}</CardTitle>
                  </CardHeader>
                  <CardContent className="pb-4">
                    <p className="text-xs text-gray-500">{plan.description || 'No description provided.'}</p>
                    <div className="flex justify-between items-center text-[10px] text-gray-400 mt-4 border-t pt-3">
                      <span>Start: {plan.start_date || 'Immediate'}</span>
                      <span>Status: <strong className="text-emerald-600 uppercase">{plan.status}</strong></span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
