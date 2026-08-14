import React, { useState, useEffect } from 'react';
import { useAssessment } from './hooks/useAssessment';
import { useSubjects } from '../learning/hooks/useLearning';
import { useAssessmentSession, useCancelSession } from './hooks/useAssessmentSession';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../../components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../../components/ui/Card';
import { 
  Loader2, CheckCircle2, Clock, AlertTriangle, ArrowRight, 
  ArrowLeft, BookOpen, Award, FileText, ShieldAlert, XCircle 
} from 'lucide-react';

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
  const { generateSession, startSession, questions, isLoadingQuestions, submitAssessment } = useAssessment(sessionId);
  const cancelSessionMutation = useCancelSession();

  // Load backend session details for route protection
  const { data: sessionDetails, isLoading: isLoadingSessionDetails, error: sessionDetailsError } = useAssessmentSession(sessionId);

  // Set default subject if state has it
  useEffect(() => {
    if (stateSubjectId) {
      setSelectedSubjectId(stateSubjectId);
      setViewState('landing');
    }
  }, [stateSubjectId]);

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

  // Timer effect
  useEffect(() => {
    let timer: any;
    if (viewState === 'in_progress' && timeRemaining > 0) {
      timer = setInterval(() => {
        setTimeRemaining((prev) => prev - 1);
      }, 1000);
    } else if (timeRemaining === 0 && viewState === 'in_progress') {
      handleFinalSubmit();
    }
    return () => clearInterval(timer);
  }, [viewState, timeRemaining]);

  const handleStart = async () => {
    if (!selectedSubjectId) return;
    setViewState('loading_session');
    try {
      // Create session
      const session = await generateSession.mutateAsync({ subjectId: selectedSubjectId, totalQuestions: 5 });
      setSessionId(session.id);
      
      // Start session
      await startSession.mutateAsync(session.id);
      setViewState('in_progress');
    } catch (err) {
      console.error("Failed to start assessment:", err);
      setViewState('landing');
    }
  };

  const handleOptionSelect = (questionId: string, optionId: string) => {
    setResponses((prev) => ({ ...prev, [questionId]: optionId }));
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
        time_taken_seconds: 15 // tracked time estimation
      }));
      const result = await submitAssessment.mutateAsync({ sessionId, responses: payload });
      setResultData(result);
      setViewState('results');
    } catch (err) {
      console.error("Failed to submit assessment:", err);
      setViewState('in_progress'); // Fallback
    }
  };

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
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

    return (
      <div className="p-4 md:p-8 max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8">
        
        {/* Main Question Area */}
        <div className="md:col-span-3 flex flex-col">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-muted-foreground">Question {currentQuestionIndex + 1} of {questions.length}</h2>
            <div className={`flex items-center space-x-2 font-mono text-xl font-bold px-4 py-2 rounded-lg ${timeRemaining < 60 ? 'bg-destructive/10 text-destructive animate-pulse' : 'bg-secondary text-secondary-foreground'}`}>
              <Clock className="w-5 h-5" />
              <span>{formatTime(timeRemaining)}</span>
            </div>
          </div>

          <Card className="flex-1 shadow-lg border-primary/10">
            <CardHeader className="bg-muted/30 border-b flex flex-row items-center justify-between">
              <CardTitle className="text-xl font-medium leading-relaxed">
                {currentQ.question_text}
              </CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => toggleReviewLater(currentQ.id)}
                className={`rounded-full shrink-0 ${isMarkedReview ? 'text-amber-600 bg-amber-50' : 'text-gray-400'}`}
              >
                <AlertTriangle className="w-4 h-4 mr-1" />
                {isMarkedReview ? 'Review Listed' : 'Review Later'}
              </Button>
            </CardHeader>
            <CardContent className="p-6 space-y-4">
              {currentQ.options.map((opt: any) => {
                const isSelected = responses[currentQ.id] === opt.id;
                return (
                  <button
                    key={opt.id}
                    onClick={() => handleOptionSelect(currentQ.id, opt.id)}
                    className={`w-full text-left p-5 rounded-xl border-2 transition-all duration-200 text-lg flex items-center group
                      ${isSelected 
                        ? 'border-primary bg-primary/5 shadow-md transform scale-[1.01]' 
                        : 'border-border hover:border-primary/50 hover:bg-muted'}`}
                  >
                    <div className={`w-6 h-6 rounded-full border-2 mr-4 flex items-center justify-center shrink-0 transition-colors
                      ${isSelected ? 'border-primary' : 'border-muted-foreground group-hover:border-primary/50'}`}>
                      {isSelected && <div className="w-3 h-3 rounded-full bg-primary" />}
                    </div>
                    {opt.option_text}
                  </button>
                )
              })}
            </CardContent>
          </Card>

          <div className="flex justify-between mt-6">
            <Button 
              variant="outline" 
              size="lg"
              disabled={currentQuestionIndex === 0} 
              onClick={() => setCurrentQuestionIndex(prev => prev - 1)}
              className="px-8 rounded-full"
            >
              <ArrowLeft className="mr-2 w-5 h-5" /> Previous
            </Button>
            
            {isLastQuestion ? (
              <Button 
                size="lg" 
                onClick={handleFinalSubmit} 
                disabled={!allAnswered}
                className="px-8 rounded-full shadow-lg hover:shadow-primary/25"
              >
                Submit Assessment <CheckCircle2 className="ml-2 w-5 h-5" />
              </Button>
            ) : (
              <Button 
                size="lg" 
                onClick={() => setCurrentQuestionIndex(prev => prev + 1)}
                className="px-8 rounded-full"
              >
                Next <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            )}
          </div>
        </div>

        {/* Sidebar Question Palette */}
        <div className="hidden md:block md:col-span-1 border-l pl-8 space-y-6">
          <div>
            <h3 className="font-semibold text-lg mb-4 text-foreground">Question Palette</h3>
            <div className="grid grid-cols-4 gap-2">
              {questions.map((q: any, i: number) => {
                const isAnswered = !!responses[q.id];
                const isCurrent = currentQuestionIndex === i;
                const isMarked = !!reviewLater[q.id];
                return (
                  <button
                    key={q.id}
                    onClick={() => setCurrentQuestionIndex(i)}
                    className={`w-10 h-10 rounded-lg flex items-center justify-center font-medium text-sm transition-all
                      ${isCurrent ? 'ring-2 ring-primary ring-offset-2 ring-offset-background' : ''}
                      ${isMarked ? 'bg-amber-100 text-amber-800 border-amber-300 border' : 
                        isAnswered ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground hover:bg-muted/80'}`}
                  >
                    {i + 1}
                  </button>
                )
              })}
            </div>
          </div>
          
          <div className="p-4 bg-muted/30 rounded-xl space-y-3">
            <div className="flex items-center text-sm">
              <div className="w-4 h-4 rounded bg-primary mr-3 text-white"></div> Answered
            </div>
            <div className="flex items-center text-sm">
              <div className="w-4 h-4 rounded bg-amber-100 border border-amber-300 mr-3"></div> Review Later
            </div>
            <div className="flex items-center text-sm">
              <div className="w-4 h-4 rounded bg-muted mr-3"></div> Unanswered
            </div>
          </div>
        </div>
        
      </div>
    );
  }

  return null;
}
