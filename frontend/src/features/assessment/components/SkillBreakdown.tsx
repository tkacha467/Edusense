import React from 'react';
import { TrendingUp, TrendingDown, Target } from 'lucide-react';

interface SkillItem {
  skillId: string;
  skillName: string;
  accuracy: number;
  isMastered: boolean;
}

interface SkillBreakdownProps {
  skills: SkillItem[];
}

export function SkillBreakdown({ skills }: SkillBreakdownProps) {
  if (skills.length === 0) {
    return (
      <div className="bg-white border rounded-2xl p-6 text-center text-xs text-gray-500">
        No specific skill data mapped for this evaluation.
      </div>
    );
  }

  const strongSkills = skills.filter(s => s.accuracy >= 80);
  const weakSkills = skills.filter(s => s.accuracy < 60);

  return (
    <div className="space-y-6">
      <div className="bg-white border rounded-2xl p-6 shadow-sm">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Target className="w-5 h-5 text-primary" /> Skill Proficiency Details
        </h3>
        
        <div className="space-y-4">
          {skills.map((skill) => (
            <div key={skill.skillId} className="space-y-1">
              <div className="flex justify-between items-center text-xs">
                <span className="font-bold text-gray-800">{skill.skillName}</span>
                <span className={`font-black ${skill.accuracy >= 80 ? 'text-emerald-600' : 'text-gray-600'}`}>
                  {Math.round(skill.accuracy)}% Accuracy
                </span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2 border">
                <div 
                  className={`h-full rounded-full transition-all duration-300 ${
                    skill.accuracy >= 80 ? 'bg-emerald-500' : 
                    skill.accuracy >= 60 ? 'bg-blue-500' : 'bg-rose-500'
                  }`}
                  style={{ width: `${skill.accuracy}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Strong Skills */}
        <div className="bg-emerald-50/50 border border-emerald-100 rounded-2xl p-5 space-y-3">
          <h4 className="font-extrabold text-emerald-950 text-sm flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-emerald-600" /> Strong Cognitive Areas
          </h4>
          {strongSkills.length === 0 ? (
            <p className="text-xs text-emerald-800/80">No areas above 80% accuracy yet. Keep practice intervals steady.</p>
          ) : (
            <ul className="space-y-2">
              {strongSkills.map(s => (
                <li key={s.skillId} className="text-xs text-emerald-900 font-medium flex items-center gap-1.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> {s.skillName}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Weak Skills */}
        <div className="bg-rose-50/50 border border-rose-100 rounded-2xl p-5 space-y-3">
          <h4 className="font-extrabold text-rose-950 text-sm flex items-center gap-2">
            <TrendingDown className="w-4 h-4 text-rose-600" /> Improvement Target Areas
          </h4>
          {weakSkills.length === 0 ? (
            <p className="text-xs text-rose-800/80">No areas below 60% accuracy. Excellent overall consistency!</p>
          ) : (
            <ul className="space-y-2">
              {weakSkills.map(s => (
                <li key={s.skillId} className="text-xs text-rose-900 font-medium flex items-center gap-1.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-rose-500" /> {s.skillName}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
