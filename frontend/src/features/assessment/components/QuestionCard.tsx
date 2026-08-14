import React from 'react';
import { Question } from '../types/question';
import { OptionCard } from './OptionCard';

interface QuestionCardProps {
  question: Question;
  selectedOptionId?: string;
  onOptionSelect: (optionId: string) => void;
}

export function QuestionCard({ question, selectedOptionId, onOptionSelect }: QuestionCardProps) {
  return (
    <div className="space-y-6">
      <div className="bg-white border rounded-xl p-6 shadow-sm">
        <div className="flex justify-between items-center mb-4">
          <span className="text-xs font-bold bg-primary/10 text-primary px-3 py-1 rounded-full uppercase tracking-wider">
            Difficulty: {question.difficulty_level}
          </span>
          {question.marks && (
            <span className="text-xs font-bold text-gray-500">
              {question.marks} {question.marks === 1 ? 'Mark' : 'Marks'}
            </span>
          )}
        </div>
        
        <h3 className="text-xl font-medium leading-relaxed text-gray-900 select-none">
          {question.question_text}
        </h3>

        {question.hint && (
          <details className="mt-4 text-sm text-gray-500 bg-gray-50 p-3 rounded-lg border border-dashed cursor-pointer">
            <summary className="font-semibold select-none">Show Hint</summary>
            <p className="mt-2 pl-4 border-l-2 border-primary/35">{question.hint}</p>
          </details>
        )}
      </div>

      <div className="space-y-3" role="radiogroup" aria-label="Question Options">
        {question.options.map((opt) => (
          <OptionCard
            key={opt.id}
            optionId={opt.id}
            label={opt.option_label}
            text={opt.option_text}
            isSelected={selectedOptionId === opt.id}
            onSelect={() => onOptionSelect(opt.id)}
          />
        ))}
      </div>
    </div>
  );
}
