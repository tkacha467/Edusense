import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { TrendAreaChart } from '../../components/ui/Charts';
import { 
  Flame, BrainCircuit, CheckCircle2, TrendingDown, Target, 
  BookOpen, Rocket, PlayCircle, Loader2, Award, Calendar, 
  Activity, AlertTriangle, ArrowRight, UserCheck 
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import type { StudentProfile } from '../../types';
import { useToast } from '../../contexts/ToastContext';
import { useDashboard } from './hooks/useDashboard';
import { Skeleton } from '../../components/ui/Skeleton';
import { useNavigate } from 'react-router-dom';
import { useSubjects } from '../learning/hooks/useLearning';
import { useAssessment } from '../assessment/hooks/useAssessment';
import { useResumeSession, useCancelSession } from '../assessment/hooks/useAssessmentSession';

export function StudentDashboard() {
  const { currentUser } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  
  const { data: dashboardData, isLoading, error } = useDashboard();
  const [isInitializingSession, setIsInitializingSession] = React.useState(false);
  const { data: subjects } = useSubjects();
  const { generateSession, startSession } = useAssessment();
  const { data: activeSession, refetch: refetchActiveSession } = useResumeSession();
  const cancelSessionMutation = useCancelSession();

  const handleStartAssessment = async () => {
    if (isInitializingSession) return;
    setIsInitializingSession(true);
    console.log("[Assessment Entry] Clicked Begin/Start Assessment");
    
    try {
      const subjectId = subjects && subjects.length > 0 ? subjects[0].id : null;
      if (!subjectId) {
        console.error("[Assessment Entry] No subjects found in database.");
        showToast('No subjects available. Please enroll in a course first.', 'error');
        setIsInitializingSession(false);
        return;
      }
      
      console.log(`[Assessment Entry] Creating assessment session for subject: ${subjectId}`);
      showToast('Generating personalized assessment session...', 'info');
      
      // 1. POST /assessments/generate
      const session = await generateSession.mutateAsync({ 
        subjectId, 
        totalQuestions: 5 
      });
      console.log("[Assessment Entry] Session generated successfully:", session.id);
      
      // 2. POST /assessments/{session_id}/start
      await startSession.mutateAsync(session.id);
      console.log("[Assessment Entry] Session started successfully");
      
      showToast('Assessment session initialized!', 'success');
      
      // 3. Navigate to /student/assessment/:sessionId
      console.log(`[Assessment Entry] Navigating to /student/assessment/${session.id}`);
      navigate(`/student/assessment/${session.id}`);
    } catch (err: any) {
      console.error("[Assessment Entry] Error initializing assessment session:", err);
      const detailMsg = err?.response?.data?.detail || err?.message || 'Failed to start assessment.';
      showToast(detailMsg, 'error');
    } finally {
      setIsInitializingSession(false);
    }
  };

  const handleCancelActiveSession = async (sid: string) => {
    try {
      showToast('Abandoning active assessment...', 'info');
      await cancelSessionMutation.mutateAsync(sid);
      showToast('Active assessment abandoned successfully.', 'success');
      refetchActiveSession();
    } catch (err) {
      console.error(err);
      showToast('Failed to abandon session.', 'error');
    }
  };

  if (!currentUser || currentUser.role !== 'student') return null;

  if (isLoading) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-12 w-1/3 rounded-xl animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Skeleton className="h-28 rounded-xl animate-pulse" />
          <Skeleton className="h-28 rounded-xl animate-pulse" />
          <Skeleton className="h-28 rounded-xl animate-pulse" />
          <Skeleton className="h-28 rounded-xl animate-pulse" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Skeleton className="h-80 lg:col-span-2 rounded-xl animate-pulse" />
          <Skeleton className="h-80 rounded-xl animate-pulse" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 max-w-md mx-auto text-center space-y-4">
        <div className="bg-red-50 p-4 rounded-full w-16 h-16 flex items-center justify-center mx-auto border border-red-100">
          <AlertTriangle className="w-8 h-8 text-red-600" />
        </div>
        <h3 className="text-xl font-bold text-gray-900">Connection Interrupted</h3>
        <p className="text-sm text-gray-500">Failed to load student dashboard metrics from the cloud.</p>
      </div>
    );
  }

  const profile = currentUser as Partial<StudentProfile>;
  const streak = profile?.streak || 0;
  
  // Extract real backend aggregates
  const knowledgeProfiles = dashboardData?.knowledgeProfiles || [];
  const todayTasks = dashboardData?.todayTasks || [];
  const assessmentHistory = dashboardData?.assessmentHistory || [];
  const recommendations = dashboardData?.recommendationDecisions || [];

  // Calculate Metrics from real data
  const hasHistory = assessmentHistory.length > 0;
  const hasProfiles = knowledgeProfiles.length > 0;

  // 1. Knowledge Health (Average Retention)
  const knowledgeHealth = hasProfiles
    ? Math.round((knowledgeProfiles.reduce((acc, p) => acc + (p.retention_score || 0), 0) / knowledgeProfiles.length) * 100)
    : 0;

  // 2. Mastery Score (Percentage of mastered skills)
  const masteredCount = knowledgeProfiles.filter(p => p.mastered).length;
  const masteryScore = hasProfiles
    ? Math.round((masteredCount / knowledgeProfiles.length) * 100)
    : 0;

  // 3. Consistency (Calculated based on streak & weekly minutes)
  const consistency = streak > 5 ? 'High' : (streak > 2 ? 'Medium' : 'Starting');

  // 4. Today's Revision Count
  const revisionCount = todayTasks.filter(t => t.task_type === 'REVISION' && !t.is_completed).length;

  // 5. Overall Progress
  const overallProgress = hasProfiles ? Math.round((masteredCount / knowledgeProfiles.length) * 100) : 0;

  const firstName = (profile?.fullName || 'Student').split(' ')[0];

  // Weak skills: sorted by forget_probability desc
  const weakSkills = [...knowledgeProfiles]
    .sort((a, b) => (b.forget_probability || 0) - (a.forget_probability || 0))
    .slice(0, 3);

  const mostAtRiskSkill = weakSkills.length > 0
    ? (weakSkills[0].skill?.name || `Skill ${weakSkills[0].skill_id.substring(0, 8)}`)
    : 'None';
  
  const lastPredictionSync = hasProfiles && weakSkills[0].last_predicted_at
    ? new Date(weakSkills[0].last_predicted_at).toLocaleString()
    : 'N/A';

  // Predictions format for recharts
  const predictionTrend = assessmentHistory.length > 0
    ? [...assessmentHistory]
        .reverse()
        .map((h, i) => ({
          name: h.title.substring(0, 10) || `Test ${i + 1}`,
          retention: Math.round(h.percentage)
        }))
    : [];

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Welcome Banner */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-900">Welcome back, {firstName}!</h1>
          <p className="text-muted-foreground mt-1">
            {!hasHistory ? "Let's kickstart your adaptive learning journey today." : "Here is your live cognitive knowledge matrix."}
          </p>
        </div>
        {streak > 0 && (
          <div className="flex items-center gap-2 bg-orange-50 border border-orange-100 px-4 py-2 rounded-full shadow-sm">
            <Flame className="w-5 h-5 text-orange-500 animate-pulse" />
            <span className="font-bold text-orange-600">{streak} Day Streak</span>
          </div>
        )}
      </div>

      {/* Active Session Recovery Banner */}
      {activeSession && (
        <Card className="border-amber-200 bg-amber-50 shadow-md animate-in slide-in-from-top duration-300">
          <CardContent className="p-4 flex flex-col sm:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="bg-amber-100 p-2 rounded-lg text-amber-700 shrink-0">
                <AlertTriangle className="w-5 h-5 text-amber-600 animate-pulse" />
              </div>
              <div>
                <h4 className="font-bold text-amber-950 text-sm">Active Assessment in Progress</h4>
                <p className="text-xs text-amber-900/80">You have an ongoing evaluation session. Please resume or abandon it to continue.</p>
              </div>
            </div>
            <div className="flex gap-2 shrink-0">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => handleCancelActiveSession(activeSession.id)}
                className="text-amber-800 hover:text-amber-900 border-amber-300 hover:bg-amber-100 rounded-lg text-xs"
                disabled={cancelSessionMutation.isPending}
              >
                Abandon
              </Button>
              <Button 
                size="sm" 
                onClick={() => navigate(`/student/assessment/${activeSession.id}`)}
                className="bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-semibold text-xs px-4"
              >
                Resume Session
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Hero Section Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-100/50 shadow-sm">
          <CardContent className="p-4 flex flex-col justify-between h-full">
            <span className="text-[10px] font-bold text-blue-600 uppercase tracking-wider">Knowledge Health</span>
            <span className="text-2xl font-extrabold text-blue-900 mt-2">{hasProfiles ? `${knowledgeHealth}%` : 'No data'}</span>
          </CardContent>
        </Card>
        
        <Card className="bg-gradient-to-br from-emerald-50 to-teal-50 border-emerald-100/50 shadow-sm">
          <CardContent className="p-4 flex flex-col justify-between h-full">
            <span className="text-[10px] font-bold text-emerald-600 uppercase tracking-wider">Mastery Score</span>
            <span className="text-2xl font-extrabold text-emerald-900 mt-2">{hasProfiles ? `${masteryScore}%` : 'No data'}</span>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-orange-50 to-amber-50 border-orange-100/50 shadow-sm">
          <CardContent className="p-4 flex flex-col justify-between h-full">
            <span className="text-[10px] font-bold text-orange-600 uppercase tracking-wider">Consistency</span>
            <span className="text-2xl font-extrabold text-orange-950 mt-2">{consistency}</span>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-indigo-50 border-purple-100/50 shadow-sm">
          <CardContent className="p-4 flex flex-col justify-between h-full">
            <span className="text-[10px] font-bold text-purple-600 uppercase tracking-wider">Active Streak</span>
            <span className="text-2xl font-extrabold text-purple-950 mt-2">{streak} Days</span>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-pink-50 to-rose-50 border-pink-100/50 shadow-sm">
          <CardContent className="p-4 flex flex-col justify-between h-full">
            <span className="text-[10px] font-bold text-rose-600 uppercase tracking-wider">Daily Revisions</span>
            <span className="text-2xl font-extrabold text-rose-950 mt-2">{revisionCount} Due</span>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-50 to-blue-50 border-slate-200/50 shadow-sm">
          <CardContent className="p-4 flex flex-col justify-between h-full">
            <span className="text-[10px] font-bold text-slate-600 uppercase tracking-wider">Overall Progress</span>
            <span className="text-2xl font-extrabold text-slate-900 mt-2">{hasProfiles ? `${overallProgress}%` : 'No data'}</span>
          </CardContent>
        </Card>
      </div>

      {/* If No Baseline, Show Call to Action */}
      {!hasHistory ? (
        <Card className="border-primary/20 bg-primary/5 shadow-md">
          <CardContent className="p-8 text-center flex flex-col items-center justify-center space-y-6">
            <div className="bg-primary/10 p-4 rounded-full">
              <Rocket className="w-12 h-12 text-primary" />
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-gray-900">Ready to beat the Forgetting Curve?</h2>
              <p className="text-gray-600 max-w-md mx-auto text-sm">
                Take your first adaptive learning assessment to establish your neural baseline. EduSense AI will construct a personalized study schedule immediately.
              </p>
            </div>
            <Button 
              onClick={handleStartAssessment} 
              disabled={isInitializingSession} 
              className="rounded-full px-8 py-5 h-auto text-base font-bold shadow-lg hover:shadow-primary/20"
            >
              {isInitializingSession ? (
                <><Loader2 className="w-5 h-5 mr-2 animate-spin" /> Initializing Session...</>
              ) : (
                <><PlayCircle className="w-5 h-5 mr-2" /> Start First Assessment</>
              )}
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Dashboard Panel */}
          <div className="lg:col-span-2 space-y-8">
            {/* AI Recommendation Card */}
            <Card className="border-violet-100 bg-gradient-to-br from-violet-50 to-fuchsia-50 shadow-sm">
              <CardContent className="p-6 flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="flex items-start gap-4">
                  <div className="bg-violet-100 p-3 rounded-xl text-violet-700">
                    <BrainCircuit className="w-8 h-8" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-violet-950">AI Cognitive Insight</h3>
                    <p className="text-xs text-violet-800/80 mt-1 max-w-md">
                      {recommendations.length > 0
                        ? `${recommendations[0].recommendation} Reason: ${recommendations[0].reason || 'Neural pathways decaying.'}`
                        : "Your memory retention curves are stable. Keep practicing to extend half-life retention intervals."}
                    </p>
                  </div>
                </div>
                <Button 
                  onClick={() => navigate('/student/plan')} 
                  className="bg-violet-700 hover:bg-violet-800 text-white rounded-xl shadow-md"
                >
                  Configure Study Plan <ArrowRight className="w-4 h-4 ml-1.5" />
                </Button>
              </CardContent>
            </Card>

            {/* Retention Chart */}
            <Card className="border-gray-150 bg-white">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Activity className="w-5 h-5 text-primary" /> Memory Retention Curve Trend
                </CardTitle>
              </CardHeader>
              <CardContent>
                {predictionTrend.length > 0 ? (
                  <div className="h-[250px]">
                    <TrendAreaChart data={predictionTrend} categories={['retention']} height={250} />
                  </div>
                ) : (
                  <div className="h-[250px] flex flex-col items-center justify-center text-center bg-gray-50 rounded-xl border border-dashed">
                    <p className="text-xs text-gray-500">Need more assessments to render retention history graphs.</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Revision Queue Preview */}
            <Card className="border-gray-150 bg-white">
              <CardHeader className="pb-2 flex flex-row items-center justify-between">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-primary" /> Today's Revision Targets
                </CardTitle>
                <Button variant="ghost" size="sm" onClick={() => navigate('/student/plan')} className="text-xs text-primary font-bold">
                  View Study Planner <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              </CardHeader>
              <CardContent>
                {todayTasks.length === 0 ? (
                  <div className="p-6 text-center text-xs text-gray-500">
                    No learning task revisions queued for today.
                  </div>
                ) : (
                  <div className="divide-y divide-gray-100">
                    {todayTasks.slice(0, 3).map((task) => (
                      <div key={task.id} className="py-3.5 flex justify-between items-center gap-4">
                        <div className="flex items-center gap-3">
                          <div className={`w-2.5 h-2.5 rounded-full ${task.priority === 'HIGH' ? 'bg-rose-500' : 'bg-blue-500'}`} />
                          <div>
                            <p className="text-sm font-bold text-gray-900">{task.task_title || task.title}</p>
                            <p className="text-[10px] text-gray-400 font-semibold">{task.task_type} • Est: {task.estimated_minutes || 15} mins</p>
                          </div>
                        </div>
                        <Button 
                          size="sm" 
                          variant="outline" 
                          onClick={() => navigate('/student/plan')}
                          className="h-8 rounded-lg text-xs"
                        >
                          Practice
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar Widgets */}
          <div className="space-y-8">
            {/* Learning Status Card */}
            <Card className="border-gray-150 bg-white">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center gap-2">
                  <UserCheck className="w-5 h-5 text-primary" /> Learning Status
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 pt-2">
                <div className="flex justify-between items-center text-xs border-b pb-2">
                  <span className="text-gray-400 font-medium">Cognitive Status</span>
                  <span className="font-bold text-gray-900 uppercase">{profile?.learningState || 'ACTIVE'}</span>
                </div>
                <div className="flex justify-between items-center text-xs border-b pb-2">
                  <span className="text-gray-400 font-medium">Enrolled Skills</span>
                  <span className="font-bold text-gray-900">{knowledgeProfiles.length} total</span>
                </div>
                <div className="flex justify-between items-center text-xs border-b pb-2">
                  <span className="text-gray-400 font-medium">Avg Decay Risk</span>
                  <span className="font-bold text-gray-900">
                    {hasProfiles
                      ? `${Math.round((knowledgeProfiles.reduce((acc, p) => acc + (p.forget_probability || 0), 0) / knowledgeProfiles.length) * 100)}%`
                      : 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between items-center text-xs border-b pb-2">
                  <span className="text-gray-400 font-medium">Most At Risk Skill</span>
                  <span className="font-bold text-gray-900 text-right truncate max-w-[120px]" title={mostAtRiskSkill}>{mostAtRiskSkill}</span>
                </div>
                <div className="flex justify-between items-center text-xs border-b pb-2">
                  <span className="text-gray-400 font-medium">Last Prediction Sync</span>
                  <span className="font-bold text-gray-900 text-right">{lastPredictionSync}</span>
                </div>
                <Button 
                  onClick={handleStartAssessment} 
                  disabled={isInitializingSession}
                  className="w-full text-xs font-semibold flex items-center justify-center gap-2"
                  variant="outline"
                >
                  {isInitializingSession && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  Generate Evaluation Session
                </Button>
              </CardContent>
            </Card>

            {/* Weak Skills Preview */}
            <Card className="border-gray-150 bg-white">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center gap-2 text-rose-700">
                  <TrendingDown className="w-5 h-5 text-rose-500" /> Decaying Memory Risks
                </CardTitle>
              </CardHeader>
              <CardContent>
                {!hasProfiles ? (
                  <p className="text-xs text-gray-500 py-4 text-center">No skills evaluated yet.</p>
                ) : (
                  <div className="space-y-4">
                    {weakSkills.map((sub, idx) => {
                      const prob = Math.round((sub.forget_probability || 0) * 100);
                      const ret = Math.round((sub.retention_score || 0) * 100);
                      return (
                        <div key={idx} className="space-y-1">
                          <div className="flex justify-between items-center text-xs">
                            <span className="font-semibold text-gray-800 truncate max-w-[150px]">
                              {sub.skill?.name || `Skill ${sub.skill_id.substring(0, 8)}`}
                            </span>
                            <span className="font-bold text-rose-600">{prob}% Risk</span>
                          </div>
                          <div className="w-full bg-gray-100 rounded-full h-1.5">
                            <div className="bg-rose-500 h-1.5 rounded-full" style={{ width: `${prob}%` }}></div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Recent Activity Timeline */}
            <Card className="border-gray-150 bg-white">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Award className="w-5 h-5 text-primary" /> Past Evaluations
                </CardTitle>
              </CardHeader>
              <CardContent>
                {assessmentHistory.length === 0 ? (
                  <p className="text-xs text-gray-500 py-4 text-center">No past assessments found.</p>
                ) : (
                  <div className="space-y-4">
                    {assessmentHistory.slice(0, 4).map((hist) => (
                      <div key={hist.id} className="flex items-start gap-3">
                        <div className="bg-emerald-50 text-emerald-600 p-1.5 rounded-lg shrink-0 mt-0.5">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                        </div>
                        <div>
                          <p className="text-xs font-bold text-gray-900">{hist.title}</p>
                          <p className="text-[10px] text-gray-400 font-semibold mt-0.5">
                            Score: <strong className="text-emerald-600">{Math.round(hist.percentage)}%</strong> • {new Date(hist.started_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
