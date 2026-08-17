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
import { AssessmentResult } from './pages/AssessmentResult';
import { assessmentApi } from './api/assessmentApi';

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
  
  const [activeQuestion, setActiveQuestion] = useState<any>(null);
  const [questionNumber, setQuestionNumber] = useState<number>(1);
  const [selectedOptionId, setSelectedOptionId] = useState<string>('');
  const [isLoadingQuestion, setIsLoadingQuestion] = useState<boolean>(false);
  const [isSubmittingAnswer, setIsSubmittingAnswer] = useState<boolean>(false);
  const [timeRemaining, setTimeRemaining] = useState(900); // 15 mins default
  const [resultData, setResultData] = useState<any>(null);
  const [reviewLater, setReviewLater] = useState<Record<string, boolean>>({});

  const { data: subjects, isLoading: isLoadingSubjects, error: subjectsError } = useSubjects();
  const { data: sessionDetails, isLoading: isLoadingSessionDetails } = useAssessmentSession(sessionId);
  const { 
    questions, 
    isLoadingQuestions, 
    questionsError, 
    generateSession, 
    startSession, 
    submitAssessment, 
    getDraftResponses 
  } = useAssessment(sessionId);
  const cancelSessionMutation = useCancelSession();

  // Route & Session ownership validation
  useEffect(() => {
    if (sessionId && sessionDetails && currentUser) {
      const authenticatedStudentProfileId = currentUser.profileId || currentUser.id;

      // 1. Ownership validation against canonical student profile ID
      const isOwner = sessionDetails.student_id === authenticatedStudentProfileId;

      if (!isOwner) {
        console.error(`[Route Protection] Unauthorized: session student_id (${sessionDetails.student_id}) does not match authenticated student profile (${authenticatedStudentProfileId}).`);
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
    console.log("[AssessmentPage] handleStart CLICKED with subjectId:", selectedSubjectId);
    setViewState('loading_session');
    try {
      // 1. Create and start adaptive assessment session
      const session = await assessmentApi.startAdaptiveSession(selectedSubjectId, 5);
      console.log("[AssessmentPage] SESSION CREATED & STARTED:", session);
      setSessionId(session.id);
      setViewState('in_progress');
    } catch (err) {
      console.error("[AssessmentPage] Failed to start assessment:", err);
      setViewState('landing');
    }
  };

  const handleOptionSelect = (questionId: string, optionId: string) => {
    setSelectedOptionId(optionId);
  };

  const toggleReviewLater = (questionId: string) => {
    setReviewLater((prev) => ({ ...prev, [questionId]: !prev[questionId] }));
  };

  const handleFinalSubmit = async () => {
    if (!sessionId) return;
    setViewState('submitting');
    try {
      const result = await assessmentApi.finishAdaptiveSession(sessionId);
      setResultData(result);
      setViewState('results');
    } catch (err) {
      console.error("Failed to finish assessment:", err);
      setViewState('in_progress');
    }
  };

  const handleAdaptiveAnswerSubmit = async () => {
    if (!sessionId || !activeQuestion || !selectedOptionId) return;
    setIsSubmittingAnswer(true);
    try {
      // 1. Submit current answer to backend
      await assessmentApi.submitSingleAnswer(
        sessionId,
        activeQuestion.id,
        selectedOptionId,
        15
      );
      
      // 2. Fetch the next question
      await fetchNextQuestion();
    } catch (err) {
      console.error("Failed to submit adaptive answer:", err);
    } finally {
      setIsSubmittingAnswer(false);
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

  if (viewState === 'completed' && sessionDetails) {
    return (
      <AssessmentResult
        percentage={sessionDetails.percentage || 0}
        totalQuestions={sessionDetails.total_questions || 0}
        correctAnswers={(sessionDetails as any).score || (sessionDetails as any).scored_marks || 0}
        timeTakenSeconds={sessionDetails.time_taken_seconds || 0}
      />
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
      <AssessmentResult
        percentage={resultData.percentage}
        totalQuestions={resultData.total_questions}
        correctAnswers={resultData.correct_answers}
        timeTakenSeconds={resultData.time_taken_seconds}
      />
    );
  }

  // --- Step E: Test In Progress ---
  if (viewState === 'in_progress') {
    if (isLoadingQuestion || !activeQuestion) {
      return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
          <Loader2 className="w-12 h-12 animate-spin text-primary" />
          <h2 className="text-xl font-medium animate-pulse text-muted-foreground">
            Formulating next optimal adaptive evaluation question...
          </h2>
        </div>
      );
    }

    const totalQ = sessionDetails?.total_questions || 5;
    const isLastQuestion = questionNumber === totalQ;
    const isMarkedReview = !!reviewLater[activeQuestion.id];
    
    // Simulate palette responses for components
    const fakeQuestionIds = Array.from({ length: totalQ }).map((_, i) => 
      i < questionNumber ? (i === questionNumber - 1 ? activeQuestion.id : 'prev_q_' + i) : 'future_q_' + i
    );
    const fakeResponses: Record<string, string> = Array.from({ length: questionNumber - 1 }).reduce((acc: Record<string, string>, _, i) => {
      acc['prev_q_' + i] = 'answered';
      return acc;
    }, {});
    if (selectedOptionId) {
      fakeResponses[activeQuestion.id] = selectedOptionId;
    }

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
          current={questionNumber - 1 + (selectedOptionId ? 1 : 0)}
          total={totalQ}
        />

        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Main Question Display */}
          <div className="md:col-span-3 flex flex-col space-y-6">
            <div className="flex justify-between items-center bg-gray-50 p-4 rounded-xl border border-gray-150">
              <span className="text-sm font-bold text-gray-700">Question {questionNumber} of {totalQ}</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => toggleReviewLater(activeQuestion.id)}
                className={`rounded-xl shrink-0 ${isMarkedReview ? 'text-amber-700 bg-amber-50 border border-amber-200' : 'text-gray-400'}`}
              >
                <AlertTriangle className="w-4 h-4 mr-1.5" />
                {isMarkedReview ? 'Review Listed' : 'Mark for Review'}
              </Button>
            </div>

            <QuestionCard
              question={activeQuestion}
              selectedOptionId={selectedOptionId}
              onOptionSelect={(optId) => handleOptionSelect(activeQuestion.id, optId)}
            />

            {/* Navigation Buttons */}
            <div className="flex justify-end items-center pt-4 border-t">
              <Button 
                size="lg" 
                onClick={handleAdaptiveAnswerSubmit} 
                disabled={!selectedOptionId || isSubmittingAnswer}
                className="px-8 rounded-xl shadow-lg hover:shadow-primary/20 text-sm font-bold"
              >
                {isSubmittingAnswer ? 'Submitting...' : (isLastQuestion ? 'Submit & Finish' : 'Submit & Next')} 
                <ArrowRight className="ml-2 w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Sidebar Palette Navigation */}
          <div className="md:col-span-1">
            <QuestionNavigator
              totalQuestions={totalQ}
              currentIndex={questionNumber - 1}
              responses={fakeResponses}
              questionIds={fakeQuestionIds}
              reviewLater={reviewLater}
              onJump={() => {}} // Disabled jumping in adaptive assessments to enforce selection sequence
            />
          </div>
        </div>
      </div>
    );
  }

  return null;
}
