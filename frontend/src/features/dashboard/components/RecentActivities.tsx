import React from 'react';
import { Activity, Clock, RefreshCw } from 'lucide-react';
import { useRecentActivities } from '../hooks/useDashboard';

export const RecentActivities: React.FC = () => {
  const { data: activities, isLoading, isError, refetch } = useRecentActivities(8);

  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm animate-pulse space-y-4">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4" />
        {[...Array(4)].map((_, i) => (
          <div key={i} className="flex gap-3">
            <div className="w-8 h-8 bg-gray-200 rounded-full" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-3/4" />
              <div className="h-3 bg-gray-250 rounded w-1/2" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm text-center">
        <p className="text-sm text-gray-500 mb-3">Failed to load activity stream</p>
        <button
          onClick={() => refetch()}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-blue-600 border border-blue-200 rounded-lg hover:bg-blue-50 transition-colors"
        >
          <RefreshCw className="w-3 h-3" /> Retry
        </button>
      </div>
    );
  }

  const items = activities || [];

  if (items.length === 0) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex flex-col items-center justify-center text-center py-12 h-full min-h-[300px]">
        <Activity className="w-10 h-10 text-gray-300 mb-3 animate-pulse" />
        <h3 className="text-base font-bold text-gray-900 mb-1">No recent activities</h3>
        <p className="text-xs text-gray-500 max-w-xs">
          Activities will display here once students log learning events.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex flex-col h-full">
      <div className="mb-5">
        <h2 className="text-lg font-bold text-gray-950">Recent System Activity</h2>
        <p className="text-xs text-gray-500 mt-0.5">
          Live stream of updates across enrolled students
        </p>
      </div>

      <div className="flex-1 overflow-y-auto pr-1">
        <div className="relative border-l border-gray-100 pl-4 ml-3 space-y-5">
          {items.map((act) => (
            <div key={act.id} className="relative group">
              {/* Timeline marker */}
              <div className="absolute -left-[25px] top-1.5 w-2 h-2 rounded-full bg-blue-500 ring-4 ring-white group-hover:bg-blue-600 transition-colors" />
              
              <div className="space-y-1">
                <div className="flex items-center justify-between text-xs md:text-sm">
                  <span className="font-semibold text-gray-900">
                    {act.student_name}
                  </span>
                  <span className="text-[10px] text-gray-400 flex items-center gap-1">
                    <Clock className="w-3 h-3" /> {act.timestamp}
                  </span>
                </div>
                <p className="text-xs text-gray-500 font-medium">
                  {act.description}
                </p>
                <span className="inline-block text-[9px] font-bold text-blue-600 bg-blue-50 border border-blue-100 px-2 py-0.5 rounded-md">
                  {act.activity_type}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
