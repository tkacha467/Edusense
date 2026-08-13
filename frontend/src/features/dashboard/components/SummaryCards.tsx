import React from 'react';
import { Users, BrainCircuit, AlertTriangle, Clock, Sparkles, BookOpen, RefreshCw } from 'lucide-react';
import { useDashboardSummary } from '../hooks/useDashboard';

interface CardProps {
  title: string;
  value: number;
  icon: React.ElementType;
  colorClass: string;
  bgClass: string;
  badgeText?: string;
  badgeClass?: string;
}

const SummaryCardItem: React.FC<CardProps> = ({
  title,
  value,
  icon: Icon,
  colorClass,
  bgClass,
  badgeText,
  badgeClass,
}) => {
  return (
    <div className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow duration-200 flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
          {title}
        </span>
        <div className={`p-2.5 rounded-xl ${bgClass}`}>
          <Icon className={`w-5 h-5 ${colorClass}`} />
        </div>
      </div>

      <div className="flex items-baseline justify-between">
        <span className="text-3xl font-extrabold text-gray-900 tracking-tight">
          {value.toLocaleString()}
        </span>
        {badgeText && (
          <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${badgeClass}`}>
            {badgeText}
          </span>
        )}
      </div>
    </div>
  );
};

export const SummaryCards: React.FC = () => {
  const { data: summary, isLoading, isError, refetch } = useDashboardSummary();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-4" />
            <div className="h-8 bg-gray-200 rounded w-3/4" />
          </div>
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-amber-50 rounded-2xl p-4 border border-amber-200 flex items-center justify-between">
        <span className="text-sm font-medium text-amber-800">
          Failed to load live platform statistics from server.
        </span>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-amber-900 bg-white rounded-lg border border-amber-300 hover:bg-amber-100 transition-colors shadow-sm"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Retry
        </button>
      </div>
    );
  }

  const cards = [
    {
      title: 'Total Students',
      value: summary?.total_students ?? 0,
      icon: Users,
      colorClass: 'text-blue-600',
      bgClass: 'bg-blue-50',
    },
    {
      title: 'Total Skills',
      value: summary?.total_skills ?? 0,
      icon: BrainCircuit,
      colorClass: 'text-emerald-600',
      bgClass: 'bg-emerald-50',
    },
    {
      title: 'High Risk Students',
      value: summary?.high_risk_students ?? 0,
      icon: AlertTriangle,
      colorClass: 'text-rose-600',
      bgClass: 'bg-rose-50',
      badgeText: (summary?.high_risk_students ?? 0) > 0 ? 'Requires Action' : 'All Clear',
      badgeClass: (summary?.high_risk_students ?? 0) > 0 ? 'bg-rose-100 text-rose-800' : 'bg-emerald-100 text-emerald-800',
    },
    {
      title: 'Pending Revisions',
      value: summary?.pending_revisions ?? 0,
      icon: Clock,
      colorClass: 'text-amber-600',
      bgClass: 'bg-amber-50',
    },
    {
      title: 'Predictions Run',
      value: summary?.predictions_generated ?? 0,
      icon: Sparkles,
      colorClass: 'text-purple-600',
      bgClass: 'bg-purple-50',
    },
    {
      title: 'Active Courses',
      value: summary?.active_courses ?? 0,
      icon: BookOpen,
      colorClass: 'text-indigo-600',
      bgClass: 'bg-indigo-50',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      {cards.map((card) => (
        <SummaryCardItem key={card.title} {...card} />
      ))}
    </div>
  );
};
