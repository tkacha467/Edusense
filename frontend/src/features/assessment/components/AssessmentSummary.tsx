import React from 'react';
import { BookOpen, HelpCircle } from 'lucide-react';

interface AssessmentSummaryProps {
  percentage: number;
}

export function AssessmentSummary({ percentage }: AssessmentSummaryProps) {
  const getFeedbackMessage = (pct: number) => {
    if (pct >= 90) return "Outstanding masterclass performance! Your cognitive retrieval retention is currently fully reinforced. Maintain practice schedules to preserve memory trace index properties.";
    if (pct >= 75) return "Great performance. Your key retention index metrics are stable. Focus revision intervals on the identified targeted weaknesses to achieve full master status.";
    if (pct >= 60) return "Modest performance. Your neural trace paths are undergoing mild forgetting decay. Consider running custom practice reviews to stabilize decay risks.";
    return "Attention recommended. High forgetting curve decay risks identified. We recommend initiating a structured retrieval schedule to repair knowledge gaps.";
  };

  return (
    <div className="bg-white border rounded-2xl p-6 shadow-sm space-y-4">
      <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
        <BookOpen className="w-5 h-5 text-primary" /> Evaluation Analysis
      </h3>
      <p className="text-sm text-gray-600 leading-relaxed">
        {getFeedbackMessage(percentage)}
      </p>
      <div className="bg-gray-50 border p-4 rounded-xl flex gap-3 text-xs text-gray-500">
        <HelpCircle className="w-5 h-5 text-gray-400 shrink-0" />
        <p>
          EduSense continuously updates your Knowledge Profile using these metrics. The forgetting curve model tracks retention decay trends dynamically to configure optimal review schedules.
        </p>
      </div>
    </div>
  );
}
