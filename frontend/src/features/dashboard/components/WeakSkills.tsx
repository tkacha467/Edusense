import React from 'react';
import { Award, RefreshCw } from 'lucide-react';
import { useWeakSkills } from '../hooks/useDashboard';

export const WeakSkills: React.FC = () => {
  const { data: skills, isLoading, isError, refetch } = useWeakSkills(5);

  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm animate-pulse space-y-4">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4" />
        {[...Array(4)].map((_, i) => (
          <div key={i} className="space-y-2">
            <div className="h-4 bg-gray-200 rounded w-3/4" />
            <div className="h-3 bg-gray-150 rounded w-full" />
          </div>
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm text-center">
        <p className="text-sm text-gray-500 mb-3">Failed to load cohort weakness data</p>
        <button
          onClick={() => refetch()}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-blue-600 border border-blue-200 rounded-lg hover:bg-blue-50 transition-colors"
        >
          <RefreshCw className="w-3 h-3" /> Retry
        </button>
      </div>
    );
  }

  const items = skills || [];

  if (items.length === 0) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex flex-col items-center justify-center text-center py-12">
        <Award className="w-10 h-10 text-emerald-300 mb-3" />
        <h3 className="text-base font-bold text-gray-900 mb-1">No weak skills identified</h3>
        <p className="text-xs text-gray-500 max-w-xs">
          All skills meet or exceed average mastery targets.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex flex-col h-full">
      <div className="mb-5">
        <h2 className="text-lg font-bold text-gray-950">Weakest Cohort Skills</h2>
        <p className="text-xs text-gray-500 mt-0.5">
          Concept areas showing lowest mastery and highest forget probabilities
        </p>
      </div>

      <div className="flex-1 space-y-5 overflow-y-auto pr-1">
        {items.map((item) => {
          const masteryPercent = Math.round(item.avg_mastery * 100);
          const forgetPercent = Math.round(item.avg_forget_probability * 100);

          return (
            <div key={item.skill_id} className="space-y-2">
              <div className="flex items-center justify-between text-xs md:text-sm">
                <span className="font-semibold text-gray-900 truncate max-w-[180px] md:max-w-xs" title={item.skill_name}>
                  {item.skill_name}
                </span>
                <span className="text-xs font-medium text-gray-500">
                  {item.students_affected} {item.students_affected === 1 ? 'student' : 'students'} affected
                </span>
              </div>

              {/* Progress bars for Mastery & Forget Probability */}
              <div className="space-y-1">
                {/* Mastery Bar */}
                <div className="flex items-center gap-3">
                  <span className="text-[10px] font-bold text-gray-400 w-14">Mastery</span>
                  <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                      style={{ width: `${masteryPercent}%` }}
                    />
                  </div>
                  <span className="text-[10px] font-bold text-emerald-600 w-8 text-right">{masteryPercent}%</span>
                </div>

                {/* Forget Probability Bar */}
                <div className="flex items-center gap-3">
                  <span className="text-[10px] font-bold text-gray-400 w-14">Decay Risk</span>
                  <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-rose-500 rounded-full transition-all duration-500"
                      style={{ width: `${forgetPercent}%` }}
                    />
                  </div>
                  <span className="text-[10px] font-bold text-rose-600 w-8 text-right">{forgetPercent}%</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
