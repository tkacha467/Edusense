import React, { useState, useEffect } from 'react';
import { useAssessment } from './hooks/useAssessment';
import { useSubjects } from '../learning/hooks/useLearning';
import { useAssessmentSession, useCancelSession } from './hooks/useAssessmentSession';
import { useSaveAnswer } from './hooks/useSaveAnswer';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../../components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../../components/ui/Card';
import { 
  Loader2, CheckCircle2, Clock, AlertTriangle, ArrowRight, 
  ArrowLeft, BookOpen, Award, FileText, ShieldAlert, XCircle 
} from 'lucide-react';

// Import modular Phase 3 components
import { AssessmentHeader } from './components/AssessmentHeader';
import { ProgressBar } from './components/ProgressBar';
import { QuestionCard } from './components/QuestionCard';
import { QuestionNavigator } from './components/QuestionNavigator';

export function AssessmentPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { currentUser } = useAuth();
  const { sessionId: paramSessionId } = useParams<{ sessionId?: string }>();
  
  // Try to read subjectId from route state
  const stateSubjectId = location.state?.subjectId;
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>(stateSubjectId || '');
  
  const [sessionId, setSessionId] = useState<string | undefined>(paramSessionId);
  const [viewState, setViewState] = useState<'subject_select' | 'landing' | 'loading_session' | 'in_progress' | 'submitting' | 'results' | 'unauthorized' | 'forbidden' | 'expired' | 'completed' | 'cancelled'>(
    paramSessionId ? 'loading_session' : (stateSubjectId ? 'landing' : 'subject_select')
  );
  
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState<Record<string, string>>({});
  const [timeRemaining, setTimeRemaining] = useState(900); // 15 mins default
  const [resultData, setResultData] = useState<any>(null);
  const [reviewLater, setReviewLater] = useState<Record<string, boolean>>({});

  const { data: subjects, isLoading: isLoadingSubjects, error: subjectsError } = useSubjects();
  const { questions, isLoadingQuestions, submitAssessment, getDraftResponses } = useAssessment(sessionId);
  const cancelSessionMutation = useCancelSession();
  const saveAnswerMutation = useSaveAnswer(sessionId || '');

  // Load backend session details for route protection
  const { data: sessionDetails, isLoading: isLoadingSessionDetails } = useAssessmentSession(sessionId);

  // Set default subject if state has it
  useEffect(() => {
    if (stateSubjectId) {
      setSelectedSubjectId(stateSubjectId);
      setViewState('landing');
    }
  }, [stateSubjectId]);

  // Restore draft answers from local storage
  useEffect(() => {
    if (sessionId) {
      const drafts = getDraftResponses(sessionId);
      if (Object.keys(drafts).length > 0) {
        setResponses(drafts);
        console.log(`[Session Recovery] Restored ${Object.keys(drafts).length} draft answers from storage.`);
      }
    }
  }, [sessionId]);

  // Timer calculation from started_at
  useEffect(() => {
    if (sessionDetails && sessionDetails.started_at && viewState === 'in_progress') {
      const startTime = new Date(sessionDetails.started_at).getTime();
      const limit = (sessionDetails.time_limit_seconds || 900) * 1000;
      
      const updateTimer = () => {
        const elapsed = Date.now() - startTime;
        const remaining = Math.max(0, Math.floor((limit - elapsed) / 1000));
        setTimeRemaining(remaining);
        
        if (remaining === 0) {
          console.warn("[Timer Expiry] Assessment limit reached. Autosubmitting responses.");
          handleFinalSubmit();
        }
      };

      updateTimer();
      const interval = setInterval(updateTimer, 1000);
      return () => clearInterval(interval);
    }
  }, [sessionDetails, viewState]);

  // Route & Session ownership validation
  useEffect(() => {
    if (sessionId && sessionDetails && currentUser) {
      // 1. Ownership validation
      if (sessionDetails.student_id !== currentUser.id) {
        console.error("[Route Protection] Unauthorized: student does not own this session.");
        setViewState('forbidden');
        return;
      }

      // 2. Status validation
      if (sessionDetails.status === 'completed') {
        setViewState('completed');
        return;
      }
      if (sessionDetails.status === 'abandoned') {
        setViewState('cancelled');
        return;
      }

      // If active and loaded, go in_progress
      setViewState('in_progress');
    }
  }, [sessionId, sessionDetails, currentUser]);

  const handleStart = async () => {
    if (!selectedSubjectId) return;
    setViewState('loading_session');
    try {
      // Create session
      const session = await submitAssessment.mutateAsync({ sessionId: '', responses: [] }); // Stub, handled in dashboard now
    } catch (err) {
      console.error("Failed to start assessment:", err);
      setViewState('landing');
    }
  };

  const handleOptionSelect = (questionId: string, optionId: string) => {
    // 1. Update state
    setResponses((prev) => ({ ...prev, [questionId]: optionId }));
    
    // 2. Sync / Autosave to storage & query cache
    saveAnswerMutation.mutate({
      question_id: questionId,
      selected_option_id: optionId,
      time_taken_seconds: 15
    });
  };

  const toggleReviewLater = (questionId: string) => {
    setReviewLater((prev) => ({ ...prev, [questionId]: !prev[questionId] }));
  };

  const handleFinalSubmit = async () => {
    if (!sessionId) return;
    setViewState('submitting');
    try {
      const payload = Object.entries(responses).map(([qId, optId]) => ({
        question_id: qId,
        selected_option_id: optId,
        time_taken_seconds: 15
      }));
      const result = await submitAssessment.mutateAsync({ sessionId, responses: payload });
      setResultData(result);
      setViewState('results');
    } catch (err) {
      console.error("Failed to submit assessment:", err);
      setViewState('in_progress'); // Fallback
    }
  };

  const handleAbandon = async () => {
    if (!sessionId) return;
    if (confirm("Are you sure you want to abandon this assessment? Your progress will be lost permanently.")) {
      try {
        await cancelSessionMutation.mutateAsync(sessionId);
        navigate('/student/dashboard');
      } catch (err) {
        console.error("Failed to abandon session:", err);
      }
    }
  };

  // --- Step A: Subject Selection Screen ---
  if (viewState === 'subject_select') {
    return (
      <div className="p-6 md:p-8 max-w-4xl mx-auto space-y-6 animate-in fade-in duration-300">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 flex items-center gap-3">
            <FileText className="w-8 h-8 text-primary" /> Start Adaptive Assessment
          </h1>
          <p className="text-muted-foreground mt-2">
            Select a subject code below to initialize a customized AI-generated retrieval evaluation.
          </p>
        </div>

        {isLoadingSubjects ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-10 h-10 animate-spin text-primary" />
          </div>
        ) : subjectsError ? (
          <div className="bg-red-50 p-6 rounded-xl text-center text-red-600 border border-red-100">
            <p>Failed to load subjects. Please check backend connections.</p>
          </div>
        ) : !subjects || subjects.length === 0 ? (
          <div className="bg-white border rounded-xl p-12 text-center shadow-sm">
            <p className="text-gray-500 mb-4">No active subjects available for testing.</p>
            <Button onClick={() => navigate('/student/learning')}>Browse Learning Hub</Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {subjects.map((sub) => (
              <Card 
                key={sub.id} 
                className={`cursor-pointer hover:border-primary transition-all duration-200 ${selectedSubjectId === sub.id ? 'border-primary ring-2 ring-primary/20 bg-primary/5' : 'border-gray-200 bg-white'}`}
                onClick={() => {
                  setSelectedSubjectId(sub.id);
                  setViewState('landing');
                }}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-bold text-primary bg-primary/10 px-2 py-0.5 rounded">{sub.code}</span>
                    <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">{sub.category}</span>
                  </div>
                  <CardTitle className="text-lg">{sub.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-gray-500 line-clamp-2">{sub.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    );
  }

  // --- Step B: Assessment Landing Screen ---
  if (viewState === 'landing') {
    const currentSubject = subjects?.find(s => s.id === selectedSubjectId);

    return (
      <div className="p-8 max-w-4xl mx-auto flex flex-col items-center mt-12 animate-in fade-in zoom-in duration-300">
        <Card className="w-full text-center p-8 shadow-xl border-t-4 border-t-primary bg-card/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-3xl font-extrabold tracking-tight">
              Adaptive Assessment: {currentSubject?.name || 'Loading...'}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6 text-muted-foreground mt-4">
            <p className="text-lg">This test will dynamically update your Knowledge Profile and adjust your future recommendations.</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
              <div className="bg-background p-4 rounded-xl shadow-sm border border-border/50 flex flex-col items-center">
                <Clock className="w-8 h-8 mb-2 text-primary" />
                <span className="font-semibold text-foreground">15 Minutes Limit</span>
              </div>
              <div className="bg-background p-4 rounded-xl shadow-sm border border-border/50 flex flex-col items-center">
                <CheckCircle2 className="w-8 h-8 mb-2 text-primary" />
                <span className="font-semibold text-foreground">5 Adaptive Questions</span>
              </div>
              <div className="bg-background p-4 rounded-xl shadow-sm border border-border/50 flex flex-col items-center">
                <AlertTriangle className="w-8 h-8 mb-2 text-primary" />
                <span className="font-semibold text-foreground">Immediate Prediction</span>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-center gap-4 mt-8">
            <Button variant="outline" onClick={() => setViewState('subject_select')} className="rounded-full px-6">
              Change Subject
            </Button>
            <Button size="lg" onClick={handleStart} className="px-12 py-6 text-lg rounded-full shadow-lg hover:shadow-primary/25 transition-all">
              Begin Assessment
            </Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  // --- Step C: Loading / Submitting State ---
  if (viewState === 'loading_session' || viewState === 'submitting' || isLoadingQuestions || isLoadingSessionDetails) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Loader2 className="w-12 h-12 animate-spin text-primary" />
        <h2 className="text-xl font-medium animate-pulse text-muted-foreground">
          {viewState === 'submitting' 
            ? 'Evaluating responses & compiling predictive memory curve...' 
            : 'Verifying session context and retrieving question blocks...'}
        </h2>
      </div>
    );
  }

  // --- Route Protection States: Forbidden, Completed, Cancelled ---
  if (viewState === 'forbidden') {
    return (
      <div className="p-8 max-w-md mx-auto mt-12 animate-in zoom-in duration-300">
        <Card className="border-red-200 bg-red-50 text-center shadow-lg">
          <CardHeader className="flex flex-col items-center">
            <ShieldAlert className="w-12 h-12 text-red-600 mb-2" />
            <CardTitle className="text-lg font-bold text-red-950">Access Denied</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-red-800">
              This assessment session does not belong to your account.
            </p>
          </CardContent>
          <CardFooter className="justify-center">
            <Button onClick={() => navigate('/student/dashboard')} className="rounded-xl">
              Return to Dashboard
            </Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  if (viewState === 'completed') {
    return (
      <div className="p-8 max-w-md mx-auto mt-12 animate-in zoom-in duration-300">
        <Card className="border-emerald-200 bg-emerald-50 text-center shadow-lg">
          <CardHeader className="flex flex-col items-center">
            <CheckCircle2 className="w-12 h-12 text-emerald-600 mb-2" />
            <CardTitle className="text-lg font-bold text-emerald-950">Assessment Completed</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-emerald-800">
              This assessment session has already been evaluated and submitted.
            </p>
          </CardContent>
          <CardFooter className="justify-center">
            <Button onClick={() => navigate('/student/dashboard')} className="rounded-xl">
              Return to Dashboard
            </Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  if (viewState === 'cancelled') {
    return (
      <div className="p-8 max-w-md mx-auto mt-12 animate-in zoom-in duration-300">
        <Card className="border-gray-200 bg-gray-50 text-center shadow-lg">
          <CardHeader className="flex flex-col items-center">
            <XCircle className="w-12 h-12 text-gray-500 mb-2" />
            <CardTitle className="text-lg font-bold text-gray-950">Session Cancelled</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-gray-500">
              This assessment session was abandoned or cancelled.
            </p>
          </CardContent>
          <CardFooter className="justify-center">
            <Button onClick={() => navigate('/student/dashboard')} className="rounded-xl">
              Start New Assessment
            </Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  // --- Step D: Results Screen ---
  if (viewState === 'results' && resultData) {
    return (
      <div className="p-8 max-w-4xl mx-auto mt-8 animate-in slide-in-from-bottom-8 duration-500">
        <Card className="overflow-hidden shadow-2xl border-0">
          <div className="bg-gradient-to-r from-primary/10 via-primary/5 to-transparent p-10 text-center border-b flex flex-col items-center">
            <Award className="w-16 h-16 text-primary mb-4" />
            <h2 className="text-4xl font-black mb-2 text-primary">Score: {Math.round(resultData.percentage)}%</h2>
            <p className="text-lg text-muted-foreground">{resultData.correct_answers} out of {resultData.total_questions} correct</p>
          </div>
          <CardContent className="p-8">
            <h3 className="text-xl font-bold mb-4">AI Predictive Sync Completed</h3>
            <ul className="space-y-4 text-muted-foreground">
              <li className="flex items-start">
                <CheckCircle2 className="w-6 h-6 mr-3 text-green-500 shrink-0" />
                <span>Your student Knowledge Profile is updated instantly inside the database.</span>
              </li>
              <li className="flex items-start">
                <CheckCircle2 className="w-6 h-6 mr-3 text-green-500 shrink-0" />
                <span>The forgetting curve half-life model has run inference on your submission accuracy.</span>
              </li>
              <li className="flex items-start">
                <CheckCircle2 className="w-6 h-6 mr-3 text-green-500 shrink-0" />
                <span>New adaptive revision blocks are added to your study planner schedule.</span>
              </li>
            </ul>
          </CardContent>
          <CardFooter className="p-8 bg-muted/20 flex justify-end">
            <Button size="lg" onClick={() => navigate('/student/dashboard')} className="rounded-full px-8">
              Return to Dashboard <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  // --- Step E: Test In Progress ---
  if (viewState === 'in_progress' && questions && questions.length > 0) {
    const currentQ = questions[currentQuestionIndex];
    const isLastQuestion = currentQuestionIndex === questions.length - 1;
    const allAnswered = questions.every((q: any) => responses[q.id]);
    const isMarkedReview = !!reviewLater[currentQ.id];
    const questionIds = questions.map((q: any) => q.id);

    return (
      <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-6">
        {/* Header Widget */}
        <AssessmentHeader
          title={sessionDetails?.title || 'Adaptive Evaluation'}
          timeRemaining={timeRemaining}
          onAbandon={handleAbandon}
          isAbandonPending={cancelSessionMutation.isPending}
        />

        {/* Progress Tracker */}
        <ProgressBar
          current={Object.keys(responses).length}
          total={questions.length}
        />

        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Main Question Display */}
          <div className="md:col-span-3 flex flex-col space-y-6">
            <div className="flex justify-between items-center bg-gray-50 p-4 rounded-xl border border-gray-150">
              <span className="text-sm font-bold text-gray-700">Question {currentQuestionIndex + 1} of {questions.length}</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => toggleReviewLater(currentQ.id)}
                className={`rounded-xl shrink-0 ${isMarkedReview ? 'text-amber-700 bg-amber-50 border border-amber-200' : 'text-gray-400'}`}
              >
                <AlertTriangle className="w-4 h-4 mr-1.5" />
                {isMarkedReview ? 'Review Listed' : 'Mark for Review'}
              </Button>
            </div>

            <QuestionCard
              question={currentQ as any}
              selectedOptionId={responses[currentQ.id]}
              onOptionSelect={(optId) => handleOptionSelect(currentQ.id, optId)}
            />

            {/* Navigation Buttons */}
            <div className="flex justify-between items-center pt-4 border-t">
              <Button 
                variant="outline" 
                size="lg"
                disabled={currentQuestionIndex === 0} 
                onClick={() => setCurrentQuestionIndex(prev => prev - 1)}
                className="px-6 rounded-xl text-sm"
              >
                <ArrowLeft className="mr-2 w-4 h-4" /> Previous
              </Button>
              
              {isLastQuestion ? (
                <Button 
                  size="lg" 
                  onClick={handleFinalSubmit} 
                  disabled={!allAnswered || submitAssessment.isPending}
                  className="px-8 rounded-xl shadow-lg hover:shadow-primary/20 text-sm font-bold"
                >
                  {submitAssessment.isPending ? 'Submitting...' : 'Submit Assessment'} 
                  <CheckCircle2 className="ml-2 w-4 h-4" />
                </Button>
              ) : (
                <Button 
                  size="lg" 
                  onClick={() => setCurrentQuestionIndex(prev => prev + 1)}
                  className="px-6 rounded-xl text-sm"
                >
                  Next <ArrowRight className="ml-2 w-4 h-4" />
                </Button>
              )}
            </div>
          </div>

          {/* Sidebar Palette Navigation */}
          <div className="md:col-span-1">
            <QuestionNavigator
              totalQuestions={questions.length}
              currentIndex={currentQuestionIndex}
              responses={responses}
              questionIds={questionIds}
              reviewLater={reviewLater}
              onJump={(idx) => setCurrentQuestionIndex(idx)}
            />
          </div>
        </div>
      </div>
    );
  }

  return null;
}
