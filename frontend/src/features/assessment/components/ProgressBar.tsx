import React from 'react';

interface ProgressBarProps {
  current: number;
  total: number;
}

export function ProgressBar({ current, total }: ProgressBarProps) {
  const percentage = total > 0 ? Math.round((current / total) * 100) : 0;
  
  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center text-xs text-gray-500 font-semibold uppercase tracking-wider">
        <span>Progress Breakdown</span>
        <span>{current} of {total} Answered ({percentage}%)</span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden border">
        <div 
          className="bg-primary h-full rounded-full transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
