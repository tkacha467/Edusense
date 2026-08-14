import React from 'react';
import { ShieldCheck, Heart, AlertTriangle, AlertCircle } from 'lucide-react';
import { useKnowledgeHealth } from '../hooks/useKnowledgeHealth';

export function KnowledgeHealthCard() {
  const { data, isLoading, error } = useKnowledgeHealth();

  if (isLoading) {
    return (
      <div className="bg-white border border-gray-100 p-6 rounded-2xl shadow-sm flex items-center justify-center min-h-[140px]">
        <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-white border border-red-100 p-6 rounded-2xl shadow-sm text-center text-xs text-red-500">
        Failed to load knowledge health metrics.
      </div>
    );
  }

  const score = data.health_score;
  const rating = data.rating;

  const getStyle = (s: number) => {
    if (s >= 80) return { bg: 'bg-emerald-50 border-emerald-100', text: 'text-emerald-700', icon: ShieldCheck, bar: 'bg-emerald-500' };
    if (s >= 60) return { bg: 'bg-blue-50 border-blue-100', text: 'text-blue-700', icon: Heart, bar: 'bg-blue-500' };
    if (s >= 40) return { bg: 'bg-amber-50 border-amber-100', text: 'text-amber-700', icon: AlertTriangle, bar: 'bg-amber-500' };
    return { bg: 'bg-rose-50 border-rose-100', text: 'text-rose-700', icon: AlertCircle, bar: 'bg-rose-500' };
  };

  const current = getStyle(score);
  const Icon = current.icon;

  return (
    <div className={`border rounded-2xl p-6 shadow-sm transition-all duration-300 ${current.bg}`}>
      <div className="flex justify-between items-start gap-4">
        <div className="space-y-1">
          <p className="text-xs uppercase font-bold tracking-wider opacity-85">Knowledge Health</p>
          <h3 className={`text-3xl font-black ${current.text}`}>{score}%</h3>
          <p className="text-xs font-semibold mt-1">Status: <span className="underline">{rating}</span></p>
        </div>
        <div className={`p-3 rounded-xl bg-white/80 border ${current.text} shadow-sm`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>

      <div className="w-full bg-white/50 rounded-full h-2 mt-4 border overflow-hidden">
        <div 
          className={`h-full rounded-full transition-all duration-500 ${current.bar}`}
          style={{ width: `${score}%` }}
        />
      </div>

      <p className="text-[11px] mt-3 opacity-75 leading-relaxed">
        Calculated from your calibrated forgetting curve memory values. Higher values indicate fully consolidated retention.
      </p>
    </div>
  );
}
