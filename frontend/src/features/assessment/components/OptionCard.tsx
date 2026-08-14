import React from 'react';

interface OptionCardProps {
  optionId: string;
  label: string;
  text: string;
  isSelected: boolean;
  onSelect: () => void;
}

export function OptionCard({ optionId, label, text, isSelected, onSelect }: OptionCardProps) {
  return (
    <button
      onClick={onSelect}
      className={`w-full text-left p-5 rounded-xl border-2 transition-all duration-200 text-lg flex items-center group focus:ring-2 focus:ring-primary focus:outline-none
        ${isSelected 
          ? 'border-primary bg-primary/5 shadow-md transform scale-[1.01]' 
          : 'border-gray-200 bg-white hover:border-primary/50 hover:bg-gray-50'}`}
      aria-checked={isSelected}
      role="radio"
    >
      <div className={`w-6 h-6 rounded-full border-2 mr-4 flex items-center justify-center shrink-0 transition-colors
        ${isSelected ? 'border-primary' : 'border-gray-300 group-hover:border-primary/50'}`}>
        {isSelected && <div className="w-3 h-3 rounded-full bg-primary" />}
      </div>
      <span className="font-semibold mr-2">{label}.</span>
      <span className="text-gray-800">{text}</span>
    </button>
  );
}
