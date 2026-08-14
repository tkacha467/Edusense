import React from 'react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '../../../api/apiClient';
import { ShieldAlert, TrendingDown } from 'lucide-react';

interface AtRiskSkill {
  student_id: string;
  skill_id: string;
  forget_probability: number;
  retention_score: number;
  past_attempts: number;
  skill?: {
    name: string;
  };
}

export function WeakSkills() {
  const { data: atRiskSkills, isLoading, error } = useQuery<AtRiskSkill[], Error>({
    queryKey: ['atRiskSkills'],
    queryFn: async () => {
      const response = await apiClient.get<AtRiskSkill[]>('/knowledge/at-risk?threshold=0.50');
      return response.data;
    }
  });

  if (isLoading) {
    return (
      <div className="bg-white border p-6 rounded-2xl shadow-sm flex items-center justify-center min-h-[140px]">
        <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !atRiskSkills) {
    return (
      <div className="bg-white border p-6 rounded-2xl shadow-sm text-center text-xs text-red-500">
        Failed to load weak skills list.
      </div>
    );
  }

  return (
    <div className="bg-white border rounded-2xl p-6 shadow-sm space-y-4">
      <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
        <TrendingDown className="w-5 h-5 text-rose-500" /> High-Risk Decay Skills
      </h3>

      {atRiskSkills.length === 0 ? (
        <p className="text-xs text-gray-400 py-4 text-center">
          No skills currently at risk! Excellent retention indices across all topics.
        </p>
      ) : (
        <div className="space-y-3">
          {atRiskSkills.map((item) => (
            <div key={item.skill_id} className="flex justify-between items-center p-3.5 border rounded-xl bg-rose-50/20 border-rose-100">
              <div className="space-y-0.5">
                <h4 className="font-extrabold text-sm text-gray-900">
                  {item.skill?.name || `Skill ${item.skill_id.substring(0, 8)}`}
                </h4>
                <p className="text-[10px] text-gray-400 font-medium">Attempts: {item.past_attempts}</p>
              </div>
              <div className="text-right flex items-center gap-2">
                <div>
                  <p className="text-xs font-black text-rose-600">
                    {Math.round(item.forget_probability * 100)}% Forget Risk
                  </p>
                  <p className="text-[10px] text-gray-400">Retention: {Math.round(item.retention_score * 100)}%</p>
                </div>
                <ShieldAlert className="w-5 h-5 text-rose-500 shrink-0" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
