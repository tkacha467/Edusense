import React from 'react';
import { Award, CheckCircle, XCircle, BarChart3 } from 'lucide-react';

interface ScoreCardProps {
  score: number;
  totalQuestions: number;
  correctAnswers: number;
  percentage: number;
  timeTakenSeconds: number;
}

export function ScoreCard({ score, totalQuestions, correctAnswers, percentage, timeTakenSeconds }: ScoreCardProps) {
  const formatTime = (totalSeconds: number) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <div className="bg-white border rounded-2xl p-6 shadow-sm grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <div className="flex items-center gap-4">
        <div className="bg-primary/10 p-3 rounded-xl text-primary">
          <Award className="w-8 h-8" />
        </div>
        <div>
          <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Overall Accuracy</p>
          <h3 className="text-2xl font-black text-gray-900 mt-1">{Math.round(percentage)}%</h3>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="bg-emerald-50 p-3 rounded-xl text-emerald-600">
          <CheckCircle className="w-8 h-8" />
        </div>
        <div>
          <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Correct Answers</p>
          <h3 className="text-2xl font-black text-gray-900 mt-1">{correctAnswers} / {totalQuestions}</h3>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="bg-rose-50 p-3 rounded-xl text-rose-600">
          <XCircle className="w-8 h-8" />
        </div>
        <div>
          <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Incorrect Answers</p>
          <h3 className="text-2xl font-black text-gray-900 mt-1">{totalQuestions - correctAnswers} / {totalQuestions}</h3>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="bg-blue-50 p-3 rounded-xl text-blue-600">
          <BarChart3 className="w-8 h-8" />
        </div>
        <div>
          <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Time Taken</p>
          <h3 className="text-2xl font-black text-gray-900 mt-1">{formatTime(timeTakenSeconds)}</h3>
        </div>
      </div>
    </div>
  );
}
