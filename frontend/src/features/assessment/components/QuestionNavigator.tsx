import React from 'react';

interface QuestionNavigatorProps {
  totalQuestions: number;
  currentIndex: number;
  responses: Record<string, string>;
  questionIds: string[];
  reviewLater: Record<string, boolean>;
  onJump: (index: number) => void;
}

export function QuestionNavigator({ 
  totalQuestions, 
  currentIndex, 
  responses, 
  questionIds,
  reviewLater, 
  onJump 
}: QuestionNavigatorProps) {
  return (
    <div className="bg-white border rounded-xl p-5 space-y-5">
      <div>
        <h4 className="font-bold text-gray-800 text-sm mb-3 select-none">Question Palette</h4>
        <div className="grid grid-cols-5 gap-2">
          {Array.from({ length: totalQuestions }).map((_, i) => {
            const qId = questionIds[i];
            const isAnswered = qId && !!responses[qId];
            const isCurrent = currentIndex === i;
            const isMarked = qId && !!reviewLater[qId];
            
            return (
              <button
                key={i}
                onClick={() => onJump(i)}
                className={`w-9 h-9 rounded-lg flex items-center justify-center font-bold text-xs transition-all outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2
                  ${isCurrent ? 'ring-2 ring-primary ring-offset-2 ring-offset-white' : ''}
                  ${isMarked 
                    ? 'bg-amber-100 text-amber-800 border border-amber-300' 
                    : isAnswered 
                      ? 'bg-primary text-white border border-primary' 
                      : 'bg-gray-50 text-gray-500 border border-gray-200 hover:bg-gray-100'}`}
              >
                {i + 1}
              </button>
            );
          })}
        </div>
      </div>

      <div className="p-3 bg-gray-50 rounded-lg space-y-2 border text-xs">
        <div className="flex items-center">
          <div className="w-3.5 h-3.5 rounded bg-primary mr-2" />
          <span className="text-gray-600">Answered</span>
        </div>
        <div className="flex items-center">
          <div className="w-3.5 h-3.5 rounded bg-amber-100 border border-amber-300 mr-2" />
          <span className="text-gray-600">Review Later</span>
        </div>
        <div className="flex items-center">
          <div className="w-3.5 h-3.5 rounded bg-gray-50 border border-gray-200 mr-2" />
          <span className="text-gray-600">Unanswered</span>
        </div>
      </div>
    </div>
  );
}
