import React, { useState, useEffect } from 'react';
import { useAssessment } from './hooks/useAssessment';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../../components/ui/Card';
import { Loader2, CheckCircle2, Clock, AlertTriangle, ArrowRight, ArrowLeft } from 'lucide-react';

export function AssessmentPage({ subjectId = 'default_subject_id' }: { subjectId?: string }) {
  const navigate = useNavigate();
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [viewState, setViewState] = useState<'landing' | 'loading_session' | 'in_progress' | 'submitting' | 'results'>('landing');
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState<Record<string, string>>({});
  const [timeRemaining, setTimeRemaining] = useState(900); // 15 mins default
  const [resultData, setResultData] = useState<any>(null);

  const { generateSession, startSession, questions, isLoadingQuestions, submitAssessment } = useAssessment(sessionId);

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
    setViewState('loading_session');
    try {
      // Create session
      const session = await generateSession.mutateAsync({ subjectId, totalQuestions: 5 });
      setSessionId(session.id);
      
      // Start session
      await startSession.mutateAsync(session.id);
      setViewState('in_progress');
    } catch (err) {
      console.error("Failed to start assessment:", err);
      setViewState('landing');
      // handle error notification
    }
  };

  const handleOptionSelect = (questionId: string, optionId: string) => {
    setResponses((prev) => ({ ...prev, [questionId]: optionId }));
  };

  const handleFinalSubmit = async () => {
    if (!sessionId) return;
    setViewState('submitting');
    try {
      const payload = Object.entries(responses).map(([qId, optId]) => ({
        question_id: qId,
        selected_option_id: optId,
        time_taken_seconds: 10 // Mocked per question time, ideally tracked
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

  if (viewState === 'landing') {
    return (
      <div className="p-8 max-w-4xl mx-auto flex flex-col items-center mt-12 animate-in fade-in zoom-in duration-300">
        <Card className="w-full text-center p-8 shadow-xl border-t-4 border-t-primary bg-card/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-3xl font-extrabold tracking-tight">Adaptive Assessment</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6 text-muted-foreground mt-4">
            <p className="text-lg">This test will dynamically update your Knowledge Profile and adjust your future recommendations.</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
              <div className="bg-background p-4 rounded-xl shadow-sm border border-border/50 flex flex-col items-center">
                <Clock className="w-8 h-8 mb-2 text-primary" />
                <span className="font-semibold text-foreground">15 Minutes</span>
              </div>
              <div className="bg-background p-4 rounded-xl shadow-sm border border-border/50 flex flex-col items-center">
                <CheckCircle2 className="w-8 h-8 mb-2 text-primary" />
                <span className="font-semibold text-foreground">Adaptive Scoring</span>
              </div>
              <div className="bg-background p-4 rounded-xl shadow-sm border border-border/50 flex flex-col items-center">
                <AlertTriangle className="w-8 h-8 mb-2 text-primary" />
                <span className="font-semibold text-foreground">No going back</span>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-center mt-8">
            <Button size="lg" onClick={handleStart} className="px-12 py-6 text-lg rounded-full shadow-lg hover:shadow-primary/25 transition-all">
              Begin Assessment
            </Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  if (viewState === 'loading_session' || viewState === 'submitting' || isLoadingQuestions) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Loader2 className="w-12 h-12 animate-spin text-primary" />
        <h2 className="text-xl font-medium animate-pulse text-muted-foreground">
          {viewState === 'submitting' ? 'Evaluating your answers & updating Knowledge Profile...' : 'Generating your personalized test...'}
        </h2>
      </div>
    );
  }

  if (viewState === 'results' && resultData) {
    return (
      <div className="p-8 max-w-4xl mx-auto mt-8 animate-in slide-in-from-bottom-8 duration-500">
        <Card className="overflow-hidden shadow-2xl border-0">
          <div className="bg-gradient-to-r from-primary/10 via-primary/5 to-transparent p-10 text-center border-b">
            <h2 className="text-4xl font-black mb-2 text-primary">Score: {Math.round(resultData.percentage)}%</h2>
            <p className="text-lg text-muted-foreground">{resultData.correct_answers} out of {resultData.total_questions} correct</p>
          </div>
          <CardContent className="p-8">
            <h3 className="text-xl font-bold mb-4">What happens next?</h3>
            <ul className="space-y-4 text-muted-foreground">
              <li className="flex items-start">
                <CheckCircle2 className="w-6 h-6 mr-3 text-green-500 shrink-0" />
                <span>Your Knowledge Profile has been updated.</span>
              </li>
              <li className="flex items-start">
                <CheckCircle2 className="w-6 h-6 mr-3 text-green-500 shrink-0" />
                <span>The Forgetting Predictor engine is analyzing your retention rates.</span>
              </li>
              <li className="flex items-start">
                <CheckCircle2 className="w-6 h-6 mr-3 text-green-500 shrink-0" />
                <span>New items have been queued in your Revision Planner if needed.</span>
              </li>
            </ul>
          </CardContent>
          <CardFooter className="p-8 bg-muted/20 flex justify-end">
            <Button size="lg" onClick={() => navigate('/dashboard')} className="rounded-full px-8">
              Return to Dashboard <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  if (viewState === 'in_progress' && questions && questions.length > 0) {
    const currentQ = questions[currentQuestionIndex];
    const isLastQuestion = currentQuestionIndex === questions.length - 1;
    const allAnswered = questions.every((q: any) => responses[q.id]);

    return (
      <div className="p-4 md:p-8 max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 h-[calc(100vh-100px)]">
        
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
            <CardHeader className="bg-muted/30 border-b">
              <CardTitle className="text-2xl font-medium leading-relaxed">
                {currentQ.question_text}
              </CardTitle>
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

        {/* Sidebar Palette */}
        <div className="hidden md:block md:col-span-1 border-l pl-8 space-y-6">
          <div>
            <h3 className="font-semibold text-lg mb-4 text-foreground">Question Palette</h3>
            <div className="grid grid-cols-4 gap-2">
              {questions.map((q: any, i: number) => {
                const isAnswered = !!responses[q.id];
                const isCurrent = currentQuestionIndex === i;
                return (
                  <button
                    key={q.id}
                    onClick={() => setCurrentQuestionIndex(i)}
                    className={`w-10 h-10 rounded-lg flex items-center justify-center font-medium text-sm transition-all
                      ${isCurrent ? 'ring-2 ring-primary ring-offset-2 ring-offset-background' : ''}
                      ${isAnswered ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground hover:bg-muted/80'}`}
                  >
                    {i + 1}
                  </button>
                )
              })}
            </div>
          </div>
          
          <div className="p-4 bg-muted/30 rounded-xl space-y-3">
            <div className="flex items-center text-sm">
              <div className="w-4 h-4 rounded bg-primary mr-3"></div> Answered
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
