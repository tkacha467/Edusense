import React, { useState } from 'react';
import { 
  X, 
  BrainCircuit, 
  Clock, 
  AlertTriangle, 
  Award, 
  TrendingUp, 
  TrendingDown, 
  BookOpen, 
  CheckCircle2, 
  Calendar, 
  Sparkles,
  Zap,
  Layers,
  Activity
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from 'recharts';
import type { StudentDeepDiveDetails } from '../types/studentAnalytics';

import { InterventionDialog } from './InterventionDialog';
import type { InterventionRecord } from '../api/facultyApi';

interface StudentDetailsModalProps {
  details: StudentDeepDiveDetails | null;
  isOpen: boolean;
  onClose: () => void;
}

export function StudentDetailsModal({ details, isOpen, onClose }: StudentDetailsModalProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'timeline' | 'decay' | 'skills' | 'history' | 'recommendations'>('overview');
  
  // Intervention Dialog State
  const [isInterventionOpen, setIsInterventionOpen] = useState(false);
  const [selectedSkillId, setSelectedSkillId] = useState<string>('');
  const [selectedSkillName, setSelectedSkillName] = useState<string>('');
  const [selectedSkillRisk, setSelectedSkillRisk] = useState<'LOW' | 'MEDIUM' | 'HIGH'>('HIGH');
  const [selectedSkillProb, setSelectedSkillProb] = useState<number>(0.5);

  const handleOpenIntervention = (skillId: string, skillName: string, riskLevel: string = 'HIGH', forgetProb: number = 0.5) => {
    setSelectedSkillId(skillId);
    setSelectedSkillName(skillName);
    setSelectedSkillRisk(riskLevel.includes('High') || riskLevel === 'HIGH' ? 'HIGH' : riskLevel.includes('Medium') || riskLevel === 'MEDIUM' ? 'MEDIUM' : 'LOW');
    setSelectedSkillProb(forgetProb);
    setIsInterventionOpen(true);
  };

  if (!isOpen || !details) return null;

  const { student, weak_skills, strong_skills, recent_assessments, retention_timeline, knowledge_decay_curve, mastery_distribution, revision_frequency, skill_heatmap, recommendations } = details;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-student-name"
    >
      <div className="bg-slate-900 border border-slate-800 w-full max-w-5xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="p-6 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold text-lg">
              {student.name.charAt(0)}
            </div>
            <div>
              <div className="flex items-center space-x-3">
                <h2 id="modal-student-name" className="text-xl font-bold text-white">{student.name}</h2>
                <span className="text-xs font-mono bg-slate-800 text-slate-400 px-2.5 py-0.5 rounded-md border border-slate-700">
                  {student.enrollment_number}
                </span>
                <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${
                  student.status === 'At Risk' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' : 
                  student.status === 'Review Needed' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 
                  'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                }`}>
                  {student.status}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                {student.email} • {student.institution} • {student.department} (Sem {student.semester})
              </p>
            </div>
          </div>

          <button 
            onClick={onClose}
            aria-label="Close Modal"
            className="p-2 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-xl transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Navigation Tabs */}
        <div className="flex items-center space-x-1 px-6 bg-slate-950 border-b border-slate-800 overflow-x-auto">
          {[
            { key: 'overview', label: 'Overview' },
            { key: 'timeline', label: 'Retention Timeline' },
            { key: 'decay', label: 'Knowledge Decay' },
            { key: 'skills', label: 'Weak & Strong Skills' },
            { key: 'history', label: 'Revision History' },
            { key: 'recommendations', label: 'Recommendations' },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`px-4 py-3 text-xs font-medium border-b-2 transition-all whitespace-nowrap ${
                activeTab === tab.key 
                  ? 'border-indigo-500 text-indigo-400 font-semibold' 
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Modal Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-slate-200">
          {/* TAB 1: OVERVIEW */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Metric Cards Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="bg-slate-950/60 border border-slate-800 p-4 rounded-xl">
                  <span className="text-xs text-slate-400">Knowledge Health Score</span>
                  <p className="text-2xl font-bold text-white mt-1">{student.knowledge_health}%</p>
                  <span className="text-[10px] text-emerald-400 font-medium">Optimal Retention</span>
                </div>
                <div className="bg-slate-950/60 border border-slate-800 p-4 rounded-xl">
                  <span className="text-xs text-slate-400">Forget Probability</span>
                  <p className="text-2xl font-bold text-amber-400 mt-1">{student.forget_probability}</p>
                  <span className="text-[10px] text-slate-400">Memory Decay Rate</span>
                </div>
                <div className="bg-slate-950/60 border border-slate-800 p-4 rounded-xl">
                  <span className="text-xs text-slate-400">Est. Days Until Forgetting</span>
                  <p className="text-2xl font-bold text-rose-400 mt-1">{student.days_until_forgetting} Days</p>
                  <span className="text-[10px] text-rose-400 font-medium">Revision Priority: {student.revision_priority}</span>
                </div>
                <div className="bg-slate-950/60 border border-slate-800 p-4 rounded-xl">
                  <span className="text-xs text-slate-400">Learning Consistency</span>
                  <p className="text-2xl font-bold text-indigo-400 mt-1">{student.learning_consistency}%</p>
                  <span className="text-[10px] text-slate-400">Avg Time: {student.avg_response_time_sec}s</span>
                </div>
              </div>

              {/* Mastery Distribution & Skill Heatmap Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-slate-950/60 border border-slate-800 p-5 rounded-xl">
                  <h3 className="text-sm font-bold text-white mb-4 flex items-center space-x-2">
                    <Award className="w-4 h-4 text-amber-400" />
                    <span>Mastery Score Distribution</span>
                  </h3>
                  <div className="h-44">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={mastery_distribution} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                        <XAxis type="number" stroke="#64748b" />
                        <YAxis type="category" dataKey="category" stroke="#94a3b8" tick={{ fontSize: 10 }} width={120} />
                        <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', color: '#fff' }} />
                        <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                          {mastery_distribution.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Skill Heatmap List */}
                <div className="bg-slate-950/60 border border-slate-800 p-5 rounded-xl">
                  <h3 className="text-sm font-bold text-white mb-4 flex items-center space-x-2">
                    <Layers className="w-4 h-4 text-indigo-400" />
                    <span>Cognitive Skill Heatmap</span>
                  </h3>
                  <div className="space-y-3">
                    {skill_heatmap.map((item, idx) => (
                      <div key={idx} className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="text-slate-300 font-medium">{item.skill}</span>
                          <span className={item.risk_level === 'High Risk' ? 'text-rose-400 font-bold' : 'text-emerald-400 font-bold'}>
                            {item.mastery_pct}% ({item.risk_level})
                          </span>
                        </div>
                        <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${item.risk_level === 'High Risk' ? 'bg-rose-500' : 'bg-emerald-500'}`}
                            style={{ width: `${item.mastery_pct}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: RETENTION TIMELINE */}
          {activeTab === 'timeline' && (
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <TrendingUp className="w-4 h-4 text-indigo-400" />
                <span>Historical Memory Retention vs Unrevised Baseline</span>
              </h3>
              <div className="h-72 bg-slate-950/60 border border-slate-800 p-4 rounded-xl">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={retention_timeline}>
                    <defs>
                      <linearGradient id="stuRetGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="date" stroke="#64748b" />
                    <YAxis stroke="#64748b" domain={[0, 100]} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', color: '#fff' }} />
                    <Area type="monotone" dataKey="retention" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#stuRetGrad)" name="Student Retention" />
                    <Line type="monotone" dataKey="baseline" stroke="#64748b" strokeWidth={2} strokeDasharray="5 5" name="Baseline Decay" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* TAB 3: KNOWLEDGE DECAY */}
          {activeTab === 'decay' && (
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <TrendingDown className="w-4 h-4 text-rose-400" />
                <span>Predicted 30-Day Memory Decay Curve</span>
              </h3>
              <div className="h-72 bg-slate-950/60 border border-slate-800 p-4 rounded-xl">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={knowledge_decay_curve}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="day" stroke="#64748b" tickFormatter={(v) => `Day ${v}`} />
                    <YAxis stroke="#64748b" domain={[0, 100]} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', color: '#fff' }} />
                    <Line type="monotone" dataKey="predicted_retention" stroke="#ef4444" strokeWidth={3} name="Predicted Retention %" />
                    <Line type="monotone" dataKey="threshold" stroke="#f59e0b" strokeWidth={2} strokeDasharray="3 3" name="Remedial Threshold (50%)" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* TAB 4: WEAK & STRONG SKILLS */}
          {activeTab === 'skills' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Weak Skills */}
              <div className="bg-slate-950/60 border border-slate-800 p-5 rounded-xl space-y-4">
                <h3 className="text-sm font-bold text-rose-400 flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4" />
                  <span>Weak Cognitive Skills (High Forget Probability)</span>
                </h3>
                <div className="space-y-3">
                  {weak_skills.map((s) => (
                    <div key={s.id} className="p-3 bg-slate-900 border border-slate-800 rounded-lg flex items-center justify-between">
                      <div>
                        <p className="text-xs font-semibold text-white">{s.name}</p>
                        <p className="text-[10px] text-slate-400 mt-0.5">Forget Probability: <span className="text-rose-400 font-bold">{s.forget_prob}</span></p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleOpenIntervention(s.id, s.name, 'HIGH', typeof s.forget_prob === 'number' ? s.forget_prob : parseFloat(String(s.forget_prob).replace('%','')) / 100)}
                          className="bg-indigo-600/30 hover:bg-indigo-600/50 border border-indigo-500/30 text-indigo-300 font-semibold text-[11px] px-2.5 py-1 rounded-md transition-all flex items-center space-x-1"
                        >
                          <Zap className="w-3 h-3 text-indigo-400" />
                          <span>Recommend Intervention</span>
                        </button>
                        <span className="text-xs font-bold text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2.5 py-1 rounded-md">
                          {s.proficiency}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Strong Skills */}
              <div className="bg-slate-950/60 border border-slate-800 p-5 rounded-xl space-y-4">
                <h3 className="text-sm font-bold text-emerald-400 flex items-center space-x-2">
                  <Award className="w-4 h-4" />
                  <span>Strong Cognitive Skills (Mastered)</span>
                </h3>
                <div className="space-y-3">
                  {strong_skills.map((s) => (
                    <div key={s.id} className="p-3 bg-slate-900 border border-slate-800 rounded-lg flex items-center justify-between">
                      <div>
                        <p className="text-xs font-semibold text-white">{s.name}</p>
                        <p className="text-[10px] text-emerald-400 mt-0.5">Optimal Memory Retention</p>
                      </div>
                      <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-md">
                        {s.proficiency}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: REVISION HISTORY */}
          {activeTab === 'history' && (
            <div className="space-y-6">
              {/* Revision Frequency Chart */}
              <div className="bg-slate-950/60 border border-slate-800 p-5 rounded-xl space-y-4">
                <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                  <Activity className="w-4 h-4 text-indigo-400" />
                  <span>Weekly Revision Frequency</span>
                </h3>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={revision_frequency}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis dataKey="week" stroke="#64748b" />
                      <YAxis stroke="#64748b" />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', color: '#fff' }} />
                      <Bar dataKey="revisions_count" fill="#6366f1" radius={[4, 4, 0, 0]} name="Revisions Completed" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Recent Assessments List */}
              <div className="bg-slate-950/60 border border-slate-800 p-5 rounded-xl space-y-4">
                <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                  <BookOpen className="w-4 h-4 text-amber-400" />
                  <span>Recent Assessment Submissions</span>
                </h3>
                <div className="divide-y divide-slate-800 text-xs">
                  {recent_assessments.map((a) => (
                    <div key={a.id} className="py-3 flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-white">{a.title}</p>
                        <p className="text-[10px] text-slate-400 mt-0.5">Completed on {a.date}</p>
                      </div>
                      <span className="font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-md">
                        {a.score_pct}% Score
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 6: RECOMMENDATIONS */}
          {activeTab === 'recommendations' && (
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-amber-400" />
                <span>AI Recommended Remedial Practice & Interventions</span>
              </h3>
              <div className="space-y-3">
                {recommendations.map((rec) => (
                  <div key={rec.id} className="p-4 bg-slate-950/80 border border-indigo-500/20 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-bold text-indigo-400">{rec.title}</span>
                        <span className="text-[10px] bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded-full font-medium">
                          {rec.type}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-1">{rec.description}</p>
                    </div>
                    <button className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs px-4 py-2 rounded-xl shadow-lg transition-all shrink-0">
                      Assign To Student
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Targeted Learning Intervention Dialog */}
      <InterventionDialog
        isOpen={isInterventionOpen}
        onClose={() => setIsInterventionOpen(false)}
        studentId={student.id}
        studentName={student.name}
        skillId={selectedSkillId}
        skillName={selectedSkillName}
        currentRisk={selectedSkillRisk}
        forgetProbability={selectedSkillProb}
      />
    </div>
  );
}

export default StudentDetailsModal;
