import React from 'react';
import { Building2, BookOpen, Calendar } from 'lucide-react';
import { useProfileSummary } from '../hooks/useDashboard';

export const DashboardHeader: React.FC = () => {
  const { data: profile, isLoading, isError, refetch } = useProfileSummary();

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };

  const currentDateStr = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-1/4 mb-3" />
        <div className="h-8 bg-gray-200 rounded w-1/2 mb-4" />
        <div className="flex gap-4">
          <div className="h-4 bg-gray-200 rounded w-1/3" />
          <div className="h-4 bg-gray-200 rounded w-1/3" />
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-red-50 rounded-2xl p-6 border border-red-100 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-red-800">Unable to load profile header</h2>
          <p className="text-sm text-red-600">Failed to connect to backend profile service.</p>
        </div>
        <button
          onClick={() => refetch()}
          className="px-4 py-2 text-sm font-medium text-red-700 bg-white rounded-lg border border-red-200 hover:bg-red-50 shadow-sm transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 text-white rounded-2xl p-6 md:p-8 shadow-md relative overflow-hidden">
      {/* Decorative background grid blur */}
      <div className="absolute top-0 right-0 -mt-12 -mr-12 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
      
      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <p className="text-blue-200 text-sm font-semibold tracking-wide uppercase mb-1">
            {getGreeting()}
          </p>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
            {profile?.full_name || 'Faculty Member'}
          </h1>
          <p className="text-blue-100 text-sm mt-1 font-medium opacity-90">
            {profile?.designation || 'Faculty'}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 text-xs md:text-sm text-blue-100">
          <div className="flex items-center gap-2 bg-white/10 backdrop-blur-md px-3.5 py-2 rounded-xl border border-white/10">
            <Building2 className="w-4 h-4 text-blue-300" />
            <span>{profile?.institution || 'EduSense University'}</span>
          </div>

          <div className="flex items-center gap-2 bg-white/10 backdrop-blur-md px-3.5 py-2 rounded-xl border border-white/10">
            <BookOpen className="w-4 h-4 text-indigo-300" />
            <span>{profile?.department || 'Computer Science'}</span>
          </div>

          <div className="flex items-center gap-2 bg-white/10 backdrop-blur-md px-3.5 py-2 rounded-xl border border-white/10">
            <Calendar className="w-4 h-4 text-sky-300" />
            <span>{currentDateStr}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
