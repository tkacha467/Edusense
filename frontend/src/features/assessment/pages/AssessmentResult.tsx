import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { ArrowRight, CheckCircle2 } from 'lucide-react';
import { ScoreCard } from '../components/ScoreCard';
import { SkillBreakdown } from '../components/SkillBreakdown';
import { AssessmentSummary } from '../components/AssessmentSummary';
import { useDashboard } from '../../dashboard/hooks/useDashboard';

interface AssessmentResultProps {
  percentage: number;
  totalQuestions: number;
  correctAnswers: number;
  timeTakenSeconds: number;
  subjectName?: string;
}

export function AssessmentResult({ 
  percentage, 
  totalQuestions, 
  correctAnswers, 
  timeTakenSeconds,
  subjectName 
}: AssessmentResultProps) {
  const navigate = useNavigate();
  
  // Fetch live skill profile states from dashboard cache
  const { data: dashboardData } = useDashboard();
  const knowledgeProfiles = dashboardData?.knowledgeProfiles || [];

  // Map knowledge profiles to skill breakdown format
  const skillsList = knowledgeProfiles.map(p => ({
    skillId: p.skill_id,
    skillName: p.skill?.name || `Skill ${p.skill_id.substring(0, 8)}`,
    accuracy: (p.retention_score || 0) * 100, // retention/mastery mapping
    isMastered: p.mastered
  }));

  return (
    <div className="p-6 md:p-8 max-w-5xl mx-auto space-y-8 animate-in fade-in duration-500">
      {/* Title */}
      <div className="text-center space-y-2">
        <div className="bg-emerald-50 text-emerald-600 p-3 rounded-full w-16 h-16 flex items-center justify-center mx-auto border border-emerald-100 shadow-sm">
          <CheckCircle2 className="w-9 h-9" />
        </div>
        <h1 className="text-3xl font-extrabold tracking-tight text-gray-900">Evaluation Sync Successful</h1>
        <p className="text-sm text-gray-500">
          Your responses have been processed through the cognitive prediction engine.
        </p>
      </div>

      {/* Metrics Grid */}
      <ScoreCard
        score={correctAnswers}
        totalQuestions={totalQuestions}
        correctAnswers={correctAnswers}
        percentage={percentage}
        timeTakenSeconds={timeTakenSeconds}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left pane: Summary and feedback */}
        <div className="lg:col-span-1">
          <AssessmentSummary percentage={percentage} />
        </div>

        {/* Right pane: Skill breakdown */}
        <div className="lg:col-span-2">
          <SkillBreakdown skills={skillsList} />
        </div>
      </div>

      {/* Footer */}
      <div className="flex justify-end pt-4 border-t">
        <Button size="lg" onClick={() => navigate('/student/dashboard')} className="rounded-xl px-8 shadow-lg hover:shadow-primary/20">
          Return to Dashboard <ArrowRight className="ml-2 w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}
