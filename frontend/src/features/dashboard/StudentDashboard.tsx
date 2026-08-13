import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { TrendAreaChart } from '../../components/ui/Charts';
import { Flame, BrainCircuit, CheckCircle2, TrendingDown, Target, BookOpen, Rocket, PlayCircle, Loader2 } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import type { StudentProfile } from '../../types';
import { useToast } from '../../contexts/ToastContext';
import { useDashboard } from './hooks/useDashboard';
import { Skeleton } from '../../components/ui/Skeleton';

export function StudentDashboard() {
  const { currentUser } = useAuth();
  const { showToast } = useToast();
  const [isSimulating, setIsSimulating] = useState(false);
  
  const { data: dashboardData, isLoading, error } = useDashboard();

  if (!currentUser || currentUser.role !== 'student') return null;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-1/3" />
        <Skeleton className="h-[300px] w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center text-red-500">
        <p>Failed to load dashboard data. Please try again later.</p>
      </div>
    );
  }

  const profile = currentUser as Partial<StudentProfile>;
  
  // Defensive initialization with default values for new/incomplete profiles
  const learningState = profile?.learningState || 'NEW';
  const streak = profile?.streak || 0;
  const minutesToday = profile?.minutesToday || 0;
  
  // Use data from backend
  const completedTopics = dashboardData?.assessmentHistory || [];
  const studyPlan = dashboardData?.todayTasks || [];
  
  // Use real knowledge profiles
  const alerts = dashboardData?.knowledgeProfiles
    ? dashboardData.knowledgeProfiles.filter(p => (p.forget_probability || 0) > 0.5).map(p => ({
        topic: p.topic_name || p.topic_id || 'Unknown Topic',
        retention: Math.round((p.retention_score || (1 - (p.forget_probability || 0))) * 100)
      })) 
    : [];
  
  const predictions: any[] = []; // Re-enable when trend API is integrated
  
  const firstName = (profile?.fullName || 'Student').split(' ')[0];

  const handleStartSession = () => {
    setIsSimulating(true);
    setTimeout(() => {
      setIsSimulating(false);
      showToast('Learning session completed! Progress updated.', 'success');
    }, 1500);
  };

  const handleReview = () => {
    setIsSimulating(true);
    setTimeout(() => {
      setIsSimulating(false);
      showToast('Review session completed! Memory refreshed.', 'success');
    }, 1500);
  };

  return (
    <div className="space-y-6 animate-in fade-in zoom-in-95 duration-300">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Welcome, {firstName}!</h1>
          <p className="text-muted-foreground mt-1">
            {learningState === 'NEW' ? "Let's get your learning journey started." : "Here is your daily learning snapshot."}
          </p>
        </div>
        {learningState !== 'NEW' && (
          <div className="flex items-center gap-2 bg-orange-50 border border-orange-100 px-4 py-2 rounded-full">
            <Flame className={`w-5 h-5 ${streak > 0 ? 'text-orange-500' : 'text-gray-400'}`} />
            <span className={`font-bold ${streak > 0 ? 'text-orange-600' : 'text-gray-500'}`}>{streak} Day Streak</span>
          </div>
        )}
      </div>

      {learningState === 'NEW' ? (
        <Card className="border-emerald-200 bg-emerald-50/50 shadow-sm">
          <CardContent className="p-8 text-center flex flex-col items-center justify-center min-h-[300px]">
            <div className="bg-emerald-100 p-4 rounded-full mb-6">
              <Rocket className="w-12 h-12 text-emerald-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Ready to beat the forgetting curve?</h2>
            <p className="text-gray-600 max-w-md mx-auto mb-8 text-lg">
              Take your first learning module to establish your baseline memory retention. EduSense AI will then build a personalized study plan for you.
            </p>
            <Button onClick={handleStartSession} className="bg-emerald-600 hover:bg-emerald-700 text-white h-12 px-8 text-lg rounded-full" disabled={isSimulating}>
              {isSimulating ? <><Loader2 className="w-5 h-5 mr-2 animate-spin" /> Preparing Module...</> : <><PlayCircle className="w-5 h-5 mr-2" /> Start First Assessment</>}
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Urgent Action needed (Knowledge Decay Alert) */}
          <Card className={`md:col-span-2 shadow-sm relative overflow-hidden ${alerts.length > 0 ? 'border-red-200' : 'border-emerald-100'}`}>
            {alerts.length > 0 && (
              <div className="absolute top-0 right-0 p-4 opacity-10">
                <TrendingDown className="w-32 h-32 text-red-500" />
              </div>
            )}
            <CardContent className="p-6">
              {alerts.length > 0 ? (
                <div className="flex items-start gap-4">
                  <div className="bg-red-100 p-3 rounded-xl shrink-0">
                    <BrainCircuit className="w-8 h-8 text-red-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">Memory Decay Alert</h3>
                    <p className="text-gray-600 mt-1 mb-4 max-w-md">
                      Your retention for <strong className="text-gray-900">{alerts[0].topic}</strong> has dropped below {alerts[0].retention}%. We recommend a quick review session to strengthen those neural pathways!
                    </p>
                    <div className="flex gap-3">
                      <Button onClick={handleReview} className="bg-red-600 hover:bg-red-700 text-white shadow-sm" disabled={isSimulating}>
                        {isSimulating ? 'Reviewing...' : 'Review Now'}
                      </Button>
                      <Button variant="outline" className="bg-white">Remind me later</Button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-center space-y-3 py-6">
                  <div className="bg-emerald-100 p-3 rounded-xl shrink-0">
                    <CheckCircle2 className="w-8 h-8 text-emerald-600" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900">All Caught Up!</h3>
                  <p className="text-gray-600">Your memory retention is looking strong across all topics.</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Daily Goal */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center gap-2">
                <Target className="w-5 h-5 text-primary" /> Daily Goal
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center justify-center py-4">
                <div className="text-4xl font-bold text-gray-900">{minutesToday}<span className="text-xl text-gray-500 font-medium">/30</span></div>
                <p className="text-sm text-gray-500 mt-1">minutes studied today</p>
                
                <div className="w-full bg-gray-100 rounded-full h-2.5 mt-6 mb-2">
                  <div className="bg-primary h-2.5 rounded-full" style={{ width: `${Math.min((minutesToday / 30) * 100, 100)}%` }}></div>
                </div>
                <p className="text-xs font-medium text-primary w-full text-right">{Math.round(Math.min((minutesToday / 30) * 100, 100))}% Complete</p>
              </div>
            </CardContent>
          </Card>

        </div>
      )}

      {learningState !== 'NEW' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Retention Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Memory Retention Chart</CardTitle>
            </CardHeader>
            <CardContent>
              {learningState === 'AI_ENABLED' && predictions.length > 0 ? (
                <div className="h-[250px]">
                  <TrendAreaChart data={predictions} categories={['retention']} height={250} />
                </div>
              ) : (
                <div className="h-[250px] flex flex-col items-center justify-center text-center bg-gray-50 rounded-xl border border-dashed border-gray-200">
                  <BrainCircuit className="w-10 h-10 text-gray-400 mb-3" />
                  <h3 className="font-semibold text-gray-700">Gathering Intelligence...</h3>
                  <p className="text-sm text-gray-500 max-w-[200px] mt-1">Complete more topics ({10 - (completedTopics?.length || 0)} remaining) to unlock AI retention charts.</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Up Next List */}
          <Card>
            <CardHeader>
              <CardTitle>Up Next For You</CardTitle>
            </CardHeader>
            <CardContent>
              {studyPlan.length > 0 ? (
                <div className="space-y-4">
                  {studyPlan.map((item: any, i: number) => (
                    <div key={i} className="flex items-center justify-between p-4 rounded-xl border border-gray-100 hover:border-gray-200 hover:shadow-sm transition-all bg-white">
                      <div className="flex items-center gap-4">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${
                          item.status === 'completed' ? 'bg-emerald-100 text-emerald-600' :
                          item.status === 'urgent' ? 'bg-red-100 text-red-600' :
                          'bg-blue-100 text-blue-600'
                        }`}>
                          {item.status === 'completed' ? <CheckCircle2 className="w-5 h-5" /> : <BookOpen className="w-5 h-5" />}
                        </div>
                        <div>
                          <h4 className={`font-semibold ${item.status === 'completed' ? 'text-gray-500 line-through' : 'text-gray-900'}`}>{item.title}</h4>
                          <p className="text-xs text-gray-500">{item.type} • {item.time}</p>
                        </div>
                      </div>
                      {item.status !== 'completed' && (
                        <Button onClick={handleStartSession} variant={item.status === 'urgent' ? 'default' : 'outline'} size="sm" className={item.status === 'urgent' ? 'bg-red-600 hover:bg-red-700 text-white' : ''} disabled={isSimulating}>
                          Start
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="h-[250px] flex flex-col items-center justify-center text-center">
                  <p className="text-gray-500">Your study plan is empty. Start a new topic!</p>
                  <Button onClick={handleStartSession} className="mt-4" disabled={isSimulating}>Browse Topics</Button>
                </div>
              )}
            </CardContent>
          </Card>

        </div>
      )}
    </div>
  );
}


