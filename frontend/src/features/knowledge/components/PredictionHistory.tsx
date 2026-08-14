import React, { useState, useEffect } from 'react';
import { usePredictionHistory } from '../hooks/usePredictionHistory';
import { useDashboard } from '../../dashboard/hooks/useDashboard';
import { History, Sparkles, TrendingDown, Target, Zap } from 'lucide-react';

export function PredictionHistory() {
  const { data: dashboardData } = useDashboard();
  const knowledgeProfiles = dashboardData?.knowledgeProfiles || [];

  const [selectedSkillId, setSelectedSkillId] = useState<string>('');

  useEffect(() => {
    if (knowledgeProfiles.length > 0 && !selectedSkillId) {
      setSelectedSkillId(knowledgeProfiles[0].skill_id);
    }
  }, [knowledgeProfiles]);

  const { data: historyData, isLoading, error } = usePredictionHistory(selectedSkillId);

  const activeSkill = knowledgeProfiles.find(p => p.skill_id === selectedSkillId);

  return (
    <div className="bg-white border rounded-2xl p-6 shadow-sm space-y-5">
      <div className="flex justify-between items-center pb-2 border-b flex-wrap gap-2">
        <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
          <History className="w-5 h-5 text-primary" /> Prediction Snapshots
        </h3>
        
        {knowledgeProfiles.length > 0 && (
          <select
            value={selectedSkillId}
            onChange={(e) => setSelectedSkillId(e.target.value)}
            className="text-xs bg-gray-50 border rounded-xl px-3 py-1.5 font-bold text-gray-700 outline-none focus:ring-2 focus:ring-primary/20"
          >
            {knowledgeProfiles.map(p => (
              <option key={p.skill_id} value={p.skill_id}>
                {p.skill?.name || `Skill ${p.skill_id.substring(0, 8)}`}
              </option>
            ))}
          </select>
        )}
      </div>

      {isLoading ? (
        <div className="flex justify-center py-8">
          <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      ) : error || !historyData ? (
        <p className="text-xs text-red-500 text-center py-4">Failed to load prediction history.</p>
      ) : historyData.length === 0 ? (
        <p className="text-xs text-gray-400 text-center py-4">No prediction history recorded yet.</p>
      ) : (
        <div className="relative border-l pl-4 ml-2 space-y-6">
          {historyData.map((item) => (
            <div key={item.id} className="relative group">
              {/* Timeline dot */}
              <div className="absolute -left-[21px] top-1 w-3 h-3 rounded-full bg-primary border-2 border-white ring-2 ring-primary/25" />
              
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-[10px] text-gray-400">
                  <span className="font-semibold font-mono">
                    {new Date(item.predicted_at).toLocaleDateString()} at {new Date(item.predicted_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                  <span className="bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full font-bold uppercase tracking-wider">{item.triggered_by}</span>
                </div>
                
                <div className="p-4 border rounded-xl bg-gray-50/50 hover:bg-white transition-all space-y-3">
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div>
                      <p className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider">Forget Probability</p>
                      <p className="text-sm font-black text-rose-600 mt-0.5">{Math.round(item.forget_probability * 100)}%</p>
                    </div>
                    <div>
                      <p className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider">Retention Score</p>
                      <p className="text-sm font-black text-emerald-600 mt-0.5">{Math.round(item.retention_score * 100)}%</p>
                    </div>
                    <div>
                      <p className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider">Attempts</p>
                      <p className="text-sm font-bold text-gray-700 mt-0.5">{item.past_attempts}</p>
                    </div>
                    <div>
                      <p className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider">Model Version</p>
                      <p className="text-[11px] font-bold text-gray-500 font-mono mt-0.5 truncate">{item.model_version}</p>
                    </div>
                  </div>
                  
                  {/* ML Feature Snapshots */}
                  <div className="pt-2 border-t flex flex-wrap gap-2.5">
                    <span className="text-[9px] bg-white border px-2 py-0.5 rounded-full text-gray-500 font-medium">Interaction: #{item.interaction_order}</span>
                    <span className="text-[9px] bg-white border px-2 py-0.5 rounded-full text-gray-500 font-medium">Rolling Acc: {Math.round(item.rolling_accuracy * 100)}%</span>
                    <span className="text-[9px] bg-white border px-2 py-0.5 rounded-full text-gray-500 font-medium">{item.mastered ? 'Mastered' : 'Progressing'}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
