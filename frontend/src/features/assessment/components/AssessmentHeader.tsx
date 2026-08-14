import React from 'react';
import { Clock, AlertTriangle } from 'lucide-react';
import { Button } from '../../../components/ui/Button';

interface AssessmentHeaderProps {
  title: string;
  timeRemaining: number;
  onAbandon: () => void;
  isAbandonPending: boolean;
}

export function AssessmentHeader({ title, timeRemaining, onAbandon, isAbandonPending }: AssessmentHeaderProps) {
  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  const isLowTime = timeRemaining < 60;

  return (
    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b">
      <div>
        <h1 className="text-2xl font-extrabold tracking-tight text-gray-900">{title}</h1>
        <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider mt-1">Adaptive AI Session</p>
      </div>

      <div className="flex items-center gap-4 w-full sm:w-auto justify-between sm:justify-end">
        <div className={`flex items-center gap-2 font-mono text-lg font-bold px-4 py-2 rounded-xl shadow-sm border transition-all duration-300
          ${isLowTime 
            ? 'bg-rose-50 text-rose-600 border-rose-100 animate-pulse' 
            : 'bg-white text-gray-700 border-gray-200'}`}
        >
          <Clock className={`w-5 h-5 ${isLowTime ? 'text-rose-500' : 'text-gray-400'}`} />
          <span>{formatTime(timeRemaining)}</span>
        </div>

        <Button
          variant="ghost"
          size="sm"
          onClick={onAbandon}
          disabled={isAbandonPending}
          className="text-gray-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg text-xs"
        >
          <AlertTriangle className="w-4 h-4 mr-1.5" />
          Abandon Session
        </Button>
      </div>
    </div>
  );
}
