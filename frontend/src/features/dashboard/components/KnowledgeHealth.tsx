import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { RefreshCw, TrendingUp } from 'lucide-react';
import { useKnowledgeHealth } from '../hooks/useDashboard';

export const KnowledgeHealth: React.FC = () => {
  const { data, isLoading, isError, refetch } = useKnowledgeHealth();

  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm h-96 flex flex-col justify-between animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4" />
        <div className="flex-1 bg-gray-150 rounded w-full" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm h-96 flex flex-col items-center justify-center text-center">
        <div className="max-w-md">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Could not load analytics</h3>
          <p className="text-sm text-gray-500 mb-4">
            An error occurred while fetching the knowledge health trends.
          </p>
          <button
            onClick={() => refetch()}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-lg border border-blue-200 transition-colors"
          >
            <RefreshCw className="w-4 h-4" /> Retry
          </button>
        </div>
      </div>
    );
  }

  const points = data?.points || [];

  if (points.length === 0) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm h-96 flex flex-col items-center justify-center text-center">
        <TrendingUp className="w-12 h-12 text-gray-300 mb-3" />
        <h3 className="text-lg font-semibold text-gray-950 mb-1">No analytics available</h3>
        <p className="text-sm text-gray-500 max-w-sm">
          Once students complete practice questions and predictions are generated, your time-series knowledge health tracking will appear here.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex flex-col h-96">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-bold text-gray-950">Knowledge Health Overview</h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Cohort retention trends and forget probability tracking
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 bg-emerald-500 rounded-full" />
            <span className="font-semibold text-gray-600">Avg Retention</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 bg-rose-500 rounded-full" />
            <span className="font-semibold text-gray-600">Avg Forget Prob</span>
          </div>
        </div>
      </div>

      <div className="flex-1 w-full min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={points} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorRetention" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorForget" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis
              dataKey="date_label"
              stroke="#94a3b8"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              dy={10}
            />
            <YAxis
              stroke="#94a3b8"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              domain={[0, 1]}
              tickFormatter={(val) => `${Math.round(val * 100)}%`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#ffffff',
                border: '1px solid #f1f5f9',
                borderRadius: '12px',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.05)',
              }}
              labelStyle={{ fontSize: '11px', fontWeight: 600, color: '#1e293b' }}
              itemStyle={{ fontSize: '12px', padding: '2px 0' }}
              formatter={(value: any, name: string) => [
                `${(Number(value) * 100).toFixed(1)}%`,
                name === 'avg_retention' ? 'Avg Retention' : 'Avg Forget Prob'
              ]}
            />
            <Area
              type="monotone"
              dataKey="avg_retention"
              stroke="#10b981"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorRetention)"
            />
            <Area
              type="monotone"
              dataKey="avg_forget_prob"
              stroke="#f43f5e"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorForget)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
