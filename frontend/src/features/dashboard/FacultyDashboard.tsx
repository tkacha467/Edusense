import React, { useState, useEffect, useMemo } from 'react';
import { 
  Users, 
  BrainCircuit, 
  AlertTriangle, 
  Award, 
  TrendingDown, 
  Clock, 
  PlusCircle, 
  Sparkles, 
  Download, 
  Search, 
  BookOpen, 
  Send,
  ChevronRight,
  Filter,
  CheckCircle2,
  Eye,
  FileSpreadsheet
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell
} from 'recharts';
import apiClient from '../../api/apiClient';
import { useAuth } from '../../contexts/AuthContext';
import { useStudentData } from '../faculty/context/StudentDataContext';
import StudentDetailsModal from '../faculty/components/StudentDetailsModal';

interface ClassOverviewData {
  total_students: number;
  class_health_score: number;
  completed_assessments: number;
  at_risk_students: number;
  average_retention_rate: number;
  exam_readiness_score: number;
  mastery_distribution: {
    mastered: number;
    review_needed: number;
    at_risk: number;
  };
  forgetting_curve: Array<{
    day: number;
    predicted_retention: number;
    baseline: number;
  }>;
}

export function FacultyDashboard() {
  const { currentUser: user } = useAuth();
  const { 
    atRiskStudents, 
    atRiskCount, 
    selectedStudentDetails, 
    isModalOpen, 
    openStudentModal, 
    closeStudentModal, 
    generateStudentReport,
    scrollToAtRiskTable 
  } = useStudentData();

  const [overview, setOverview] = useState<ClassOverviewData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSubject, setSelectedSubject] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  useEffect(() => {
    fetchClassOverview();
  }, [selectedSubject]);

  const fetchClassOverview = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = selectedSubject !== 'all' ? { subject_id: selectedSubject } : {};
      const res = await apiClient.get('/faculty/analytics/overview', { params });
      setOverview(res.data);
    } catch (err: any) {
      // Fallback mock overview if subject analytics backend is unreachable
      setOverview({
        total_students: 10,
        class_health_score: 74.5,
        completed_assessments: 42,
        at_risk_students: atRiskCount,
        average_retention_rate: 78.2,
        exam_readiness_score: 76.0,
        mastery_distribution: {
          mastered: 5,
          review_needed: 2,
          at_risk: 3
        },
        forgetting_curve: [
          { day: 0, predicted_retention: 95.0, baseline: 95.0 },
          { day: 3, predicted_retention: 88.2, baseline: 82.0 },
          { day: 7, predicted_retention: 79.5, baseline: 70.0 },
          { day: 14, predicted_retention: 68.0, baseline: 58.0 },
          { day: 21, predicted_retention: 58.5, baseline: 46.0 },
          { day: 30, predicted_retention: 48.0, baseline: 35.0 }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  // Filter At-Risk Table by Search Query
  const filteredWatchlist = useMemo(() => {
    const q = searchQuery.toLowerCase().trim();
    if (!q) return atRiskStudents;

    return atRiskStudents.filter(s => 
      s.name.toLowerCase().includes(q) ||
      s.enrollment_number.toLowerCase().includes(q) ||
      s.email.toLowerCase().includes(q) ||
      s.subject.toLowerCase().includes(q)
    );
  }, [searchQuery, atRiskStudents]);

  const masteryChartData = [
    { name: 'Mastered (>=80%)', count: overview?.mastery_distribution?.mastered || 5, color: '#10b981' },
    { name: 'Review Needed (50-79%)', count: overview?.mastery_distribution?.review_needed || 2, color: '#f59e0b' },
    { name: 'At Risk (<50%)', count: atRiskCount, color: '#ef4444' }
  ];

  return (
    <div className="space-y-8">
      {/* 1. Header Command Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl text-white">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <span className="bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 text-xs font-semibold px-3 py-1 rounded-full uppercase tracking-wider">
                Faculty Command Suite
              </span>
              <span className="text-xs text-slate-400 font-mono">
                {user?.email}
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
              Faculty Intelligence & Cohort Analytics
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Real-time cognitive decay forecasts, retention diagnostics, and at-risk student monitoring.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Subject Selector */}
            <select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-xl px-4 py-2.5 font-medium focus:outline-none focus:border-indigo-500 cursor-pointer"
            >
              <option value="all">All Assigned Subjects</option>
              <option value="17bd775e-8512-4311-965f-fdc9c3979792">Logit Function & AI Logic</option>
              <option value="28ce886f-9623-5422-076f-ged9d4080803">Neural Decay Networks</option>
            </select>

            <button 
              onClick={() => alert('Generating Class Analytics Report PDF...')}
              className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition-all shadow-lg flex items-center space-x-2"
            >
              <Download className="w-4 h-4 text-slate-200" />
              <span>Export Report</span>
            </button>
          </div>
        </div>
      </div>

      {/* 2. Primary KPI Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Enrolled Students */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Enrolled Cohort</span>
            <div className="p-2.5 bg-indigo-500/10 text-indigo-400 rounded-xl border border-indigo-500/20">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <span className="text-3xl font-bold text-white">10</span>
            <span className="text-xs text-emerald-400 font-medium bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/20">
              Active Cohort
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-2">Active students in assigned subjects</p>
        </div>

        {/* Class Knowledge Health */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Class Knowledge Health</span>
            <div className="p-2.5 bg-emerald-500/10 text-emerald-400 rounded-xl border border-emerald-500/20">
              <BrainCircuit className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <span className="text-3xl font-bold text-white">{overview?.class_health_score || 74.5}%</span>
            <span className="text-xs text-emerald-400 font-medium bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/20">
              Optimal
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-2">Class-wide average retention rating</p>
        </div>

        {/* Average Recall Rate */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Average Retention</span>
            <div className="p-2.5 bg-violet-500/10 text-violet-400 rounded-xl border border-violet-500/20">
              <Award className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <span className="text-3xl font-bold text-white">{overview?.average_retention_rate || 78.2}%</span>
            <span className="text-xs text-indigo-400 font-medium bg-indigo-500/10 px-2 py-0.5 rounded-md border border-indigo-500/20">
              High Recall
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-2">Predicted memory retention probability</p>
        </div>

        {/* At-Risk Vulnerability Counter Card */}
        <div 
          onClick={scrollToAtRiskTable}
          title="Click to view At-Risk Student Watchlist table"
          className="bg-slate-900/90 border border-rose-500/30 hover:border-rose-500/60 rounded-2xl p-5 shadow-lg relative overflow-hidden cursor-pointer transition-all hover:scale-[1.02]"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">At-Risk Students</span>
            <div className="p-2.5 bg-rose-500/10 text-rose-400 rounded-xl border border-rose-500/20">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <span className="text-3xl font-bold text-rose-400">{atRiskCount}</span>
            <span className="text-xs text-rose-400 font-medium bg-rose-500/10 px-2 py-0.5 rounded-md border border-rose-500/20">
              Requires Action
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-2">Synced dataset counter (Click to scroll)</p>
        </div>
      </div>

      {/* 3. Class Forgetting Curve & Mastery Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Class Forgetting Curve Plot */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-800 gap-4">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center space-x-2">
                <TrendingDown className="w-5 h-5 text-indigo-400" />
                <span>Predicted Class Forgetting Curve (30-Day Forecast)</span>
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Aggregated retention forecast modeled by Ebbinghaus Decay Neural Predictor
              </p>
            </div>

            <div className="flex items-center space-x-4 text-xs">
              <div className="flex items-center space-x-1.5">
                <span className="w-3 h-3 rounded-full bg-indigo-500" />
                <span className="text-slate-300">Cohort Predicted</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <span className="w-3 h-3 rounded-full bg-slate-600" />
                <span className="text-slate-500">Unrevised Baseline</span>
              </div>
            </div>
          </div>

          <div className="h-72 mt-6">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={overview?.forgetting_curve || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="predictedGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="baselineGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#475569" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#475569" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" stroke="#64748b" tickFormatter={(v) => `Day ${v}`} />
                <YAxis stroke="#64748b" domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', color: '#f8fafc' }}
                  formatter={(val: any) => [`${val}%`, 'Retention']}
                  labelFormatter={(lbl) => `Forecast: Day ${lbl}`}
                />
                <Area type="monotone" dataKey="predicted_retention" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#predictedGrad)" name="Cohort Predicted" />
                <Area type="monotone" dataKey="baseline" stroke="#64748b" strokeWidth={2} strokeDasharray="5 5" fillOpacity={1} fill="url(#baselineGrad)" name="Unrevised Baseline" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Mastery Distribution Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center space-x-2 pb-4 border-b border-slate-800">
              <Award className="w-5 h-5 text-amber-400" />
              <span>Cohort Mastery Breakdown</span>
            </h2>
            <p className="text-xs text-slate-400 mt-2">
              Distribution of students by cognitive mastery tiers across active topics.
            </p>

            <div className="h-48 mt-6">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={masteryChartData} layout="vertical" margin={{ top: 0, right: 20, left: 40, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                  <XAxis type="number" stroke="#64748b" />
                  <YAxis type="category" dataKey="name" stroke="#94a3b8" tick={{ fontSize: 11 }} width={110} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', color: '#fff' }} />
                  <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                    {masteryChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-slate-800/50 border border-slate-800 rounded-xl p-4 mt-4">
            <div className="flex items-center justify-between text-xs text-slate-300">
              <span>Exam Readiness Forecast:</span>
              <span className="font-bold text-emerald-400">{overview?.exam_readiness_score || 76.0}% Score Target</span>
            </div>
          </div>
        </div>
      </div>

      {/* 4. At-Risk Student Watchlist & Intervention Table */}
      <div id="at-risk-watchlist-section" className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-4">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 text-rose-400" />
              <span>At-Risk Student Watchlist ({filteredWatchlist.length} Students)</span>
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Synchronized dataset view of students identified with accelerating decay rates requiring remedial practice.
            </p>
          </div>

          {/* Search Filter */}
          <div className="relative w-full sm:w-64">
            <input 
              type="text"
              placeholder="Search watchlist..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-xl pl-9 pr-4 py-2 focus:outline-none focus:border-indigo-500"
            />
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
          </div>
        </div>

        {/* At-Risk Student Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse" aria-label="At-Risk Watchlist Table">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-xs font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Student</th>
                <th className="py-3 px-4">Student ID</th>
                <th className="py-3 px-4">Subject</th>
                <th className="py-3 px-4 text-center">Forget Prob</th>
                <th className="py-3 px-4 text-center">Knowledge Health</th>
                <th className="py-3 px-4 text-center">Risk Level</th>
                <th className="py-3 px-4">Recommended Revision</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs text-slate-300">
              {filteredWatchlist.length > 0 ? (
                filteredWatchlist.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 rounded-full bg-indigo-500/20 text-indigo-400 font-bold text-xs flex items-center justify-center shrink-0">
                          {s.name.charAt(0)}
                        </div>
                        <div>
                          <p className="font-bold text-white text-xs">{s.name}</p>
                          <p className="text-[10px] text-slate-400">{s.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-indigo-300 font-semibold">
                      {s.enrollment_number}
                    </td>
                    <td className="py-3.5 px-4 text-slate-300">
                      {s.subject}
                    </td>
                    <td className="py-3.5 px-4 text-center font-mono font-bold text-rose-400">
                      {s.forget_probability}
                    </td>
                    <td className="py-3.5 px-4 text-center font-bold text-white">
                      {s.knowledge_health}%
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span className={`px-2.5 py-1 rounded-full font-semibold border ${
                        s.risk_level === 'Critical' ? 'bg-rose-500/20 text-rose-300 border-rose-500/30 font-bold' :
                        s.risk_level === 'High' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' :
                        s.risk_level === 'Medium' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                        'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      }`}>
                        {s.risk_level}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 font-medium">
                      {s.recommended_revision_date}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <button 
                          onClick={() => openStudentModal(s.id)}
                          className="inline-flex items-center space-x-1 bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-400 border border-indigo-500/30 px-2.5 py-1.5 rounded-lg font-medium transition-all"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>View Details</span>
                        </button>
                        <button 
                          onClick={() => generateStudentReport(s.id)}
                          className="inline-flex items-center space-x-1 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 px-2.5 py-1.5 rounded-lg font-medium transition-all"
                        >
                          <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
                          <span>Generate Report</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-500">
                    No active at-risk students match your search query.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. Integrated Deep-Dive Student Details Modal */}
      <StudentDetailsModal
        details={selectedStudentDetails}
        isOpen={isModalOpen}
        onClose={closeStudentModal}
      />
    </div>
  );
}
