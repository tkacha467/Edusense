import React, { useState, useMemo } from 'react';
import { 
  BrainCircuit, 
  Users, 
  AlertTriangle, 
  Award, 
  TrendingDown, 
  Clock, 
  Search, 
  Filter, 
  Download, 
  Eye, 
  Send, 
  FileSpreadsheet, 
  RotateCcw, 
  ArrowUpDown, 
  Zap, 
  ChevronDown,
  CheckCircle2
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Cell 
} from 'recharts';
import { useStudentData, type StudentRecord } from '../context/StudentDataContext';
import StudentDetailsModal from '../components/StudentDetailsModal';

export function FacultyPredictionPage() {
  const { 
    students, 
    atRiskCount, 
    openStudentModal, 
    selectedStudentDetails, 
    isModalOpen, 
    closeStudentModal, 
    generateStudentReport 
  } = useStudentData();

  // Filters State
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [subjectFilter, setSubjectFilter] = useState<string>('all');
  const [semesterFilter, setSemesterFilter] = useState<string>('all');
  const [riskFilter, setRiskFilter] = useState<string>('all');
  const [healthFilter, setHealthFilter] = useState<string>('all');

  // Sorting State
  const [sortBy, setSortBy] = useState<'forget_probability' | 'knowledge_health' | 'mastery_score' | 'name' | 'days_until_forgetting'>('forget_probability');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Calculated Dynamic Summary Metrics (No hardcoded values!)
  const summaryMetrics = useMemo(() => {
    if (students.length === 0) {
      return { total: 0, avgForgetProb: 0, highRiskCount: 0, avgHealth: 0, avgMastery: 0 };
    }
    const total = students.length;
    const avgForgetProb = Number((students.reduce((acc, s) => acc + s.forget_probability, 0) / total).toFixed(2));
    const highRiskCount = atRiskCount;
    const avgHealth = Number((students.reduce((acc, s) => acc + s.knowledge_health, 0) / total).toFixed(1));
    const avgMastery = Number((students.reduce((acc, s) => acc + s.mastery_score, 0) / total).toFixed(1));

    return { total, avgForgetProb, highRiskCount, avgHealth, avgMastery };
  }, [students, atRiskCount]);

  // Retention Distribution Chart Data
  const retentionDistData = useMemo(() => {
    const buckets = [
      { range: '0-20%', count: 0, color: '#ef4444' },
      { range: '21-40%', count: 0, color: '#f59e0b' },
      { range: '41-60%', count: 0, color: '#eab308' },
      { range: '61-80%', count: 0, color: '#6366f1' },
      { range: '81-100%', count: 0, color: '#10b981' }
    ];

    students.forEach(s => {
      if (s.retention_pct <= 20) buckets[0].count++;
      else if (s.retention_pct <= 40) buckets[1].count++;
      else if (s.retention_pct <= 60) buckets[2].count++;
      else if (s.retention_pct <= 80) buckets[3].count++;
      else buckets[4].count++;
    });

    return buckets;
  }, [students]);

  // Risk Distribution Chart Data
  const riskDistData = useMemo(() => {
    const counts = { Critical: 0, High: 0, Medium: 0, Low: 0 };
    students.forEach(s => {
      counts[s.risk_level] = (counts[s.risk_level] || 0) + 1;
    });

    return [
      { name: 'Critical Risk', count: counts.Critical, color: '#f43f5e' },
      { name: 'High Risk', count: counts.High, color: '#ef4444' },
      { name: 'Medium Risk', count: counts.Medium, color: '#f59e0b' },
      { name: 'Low Risk', count: counts.Low, color: '#10b981' }
    ];
  }, [students]);

  // Revision Immediate Action Panel Data (Days remaining <= 3 or Critical/High Risk)
  const immediateRevisionStudents = useMemo(() => {
    return students.filter(s => s.days_until_forgetting <= 3 || s.risk_level === 'Critical' || s.risk_level === 'High');
  }, [students]);

  // Filtered & Sorted Student List
  const filteredAndSortedStudents = useMemo(() => {
    return students
      .filter(s => {
        const q = searchQuery.toLowerCase().trim();
        const matchSearch = 
          !q ||
          s.name.toLowerCase().includes(q) ||
          s.email.toLowerCase().includes(q) ||
          s.enrollment_number.toLowerCase().includes(q) ||
          s.skills.some(sk => sk.toLowerCase().includes(q));

        const matchSubject = subjectFilter === 'all' || s.subject_id === subjectFilter || s.subject.toLowerCase().includes(subjectFilter.toLowerCase());
        const matchSemester = semesterFilter === 'all' || s.semester.toString() === semesterFilter;
        const matchRisk = riskFilter === 'all' || s.risk_level.toLowerCase() === riskFilter.toLowerCase();
        
        const matchHealth = 
          healthFilter === 'all' ? true :
          healthFilter === 'optimal' ? s.knowledge_health >= 80 :
          healthFilter === 'moderate' ? (s.knowledge_health >= 50 && s.knowledge_health < 80) :
          s.knowledge_health < 50;

        return matchSearch && matchSubject && matchSemester && matchRisk && matchHealth;
      })
      .sort((a, b) => {
        let valA = a[sortBy];
        let valB = b[sortBy];

        if (typeof valA === 'string') {
          valA = (valA as string).toLowerCase();
          valB = (valB as string).toLowerCase();
        }

        if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
        if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
        return 0;
      });
  }, [students, searchQuery, subjectFilter, semesterFilter, riskFilter, healthFilter, sortBy, sortOrder]);

  // Export CSV
  const exportCSV = () => {
    const headers = ['Student Name', 'Enrollment Number', 'Email', 'Subject', 'Forget Probability', 'Knowledge Health %', 'Mastery Score %', 'Predicted Forgetting Date', 'Recommended Revision Date', 'Risk Level', 'Confidence Score %'];
    const rows = filteredAndSortedStudents.map(s => [
      `"${s.name}"`,
      `"${s.enrollment_number}"`,
      `"${s.email}"`,
      `"${s.subject}"`,
      s.forget_probability,
      s.knowledge_health,
      s.mastery_score,
      `"${s.predicted_forgetting_date}"`,
      `"${s.recommended_revision_date}"`,
      `"${s.risk_level}"`,
      s.confidence_score
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `EduSense_Decay_Predictions_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleRecommendRevision = (studentName: string) => {
    alert(`Remedial Revision Nudge dispatched to ${studentName}.\nSpaced recall practice set assigned to student portal.`);
  };

  return (
    <div className="space-y-8 p-1 sm:p-2">
      {/* 1. Header Command Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl text-white">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <span className="bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 text-xs font-semibold px-3 py-1 rounded-full uppercase tracking-wider">
                Ebbinghaus Decay Predictor Engine
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
              Faculty Decay Prediction Workspace
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Analyze individual memory retention curves, filter decay forecasts, and dispatch automated revision nudges.
            </p>
          </div>

          {/* Export Actions */}
          <div className="flex items-center space-x-3">
            <button 
              onClick={exportCSV}
              className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold px-4 py-2.5 rounded-xl transition-all shadow-md flex items-center space-x-2"
            >
              <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
              <span>Export CSV</span>
            </button>

            <button 
              onClick={() => alert('Exporting Printable Knowledge Decay PDF Report...')}
              className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition-all shadow-lg flex items-center space-x-2"
            >
              <Download className="w-4 h-4 text-slate-200" />
              <span>Export PDF Report</span>
            </button>
          </div>
        </div>
      </div>

      {/* 2. Dynamic Prediction Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Total Students</span>
            <Users className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-2xl font-bold text-white mt-2">{summaryMetrics.total}</p>
          <span className="text-[10px] text-slate-500">Active Cohort</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Avg Forget Prob.</span>
            <TrendingDown className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-bold text-amber-400 mt-2">{summaryMetrics.avgForgetProb}</p>
          <span className="text-[10px] text-slate-500">Memory Decay Rate</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">High Risk Students</span>
            <AlertTriangle className="w-4 h-4 text-rose-400" />
          </div>
          <p className="text-2xl font-bold text-rose-400 mt-2">{summaryMetrics.highRiskCount}</p>
          <span className="text-[10px] text-rose-400/80 font-medium">Requires Revision</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Avg Knowledge Health</span>
            <BrainCircuit className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold text-white mt-2">{summaryMetrics.avgHealth}%</p>
          <span className="text-[10px] text-emerald-400 font-medium">Optimal Retention</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Avg Mastery Score</span>
            <Award className="w-4 h-4 text-violet-400" />
          </div>
          <p className="text-2xl font-bold text-indigo-400 mt-2">{summaryMetrics.avgMastery}%</p>
          <span className="text-[10px] text-slate-500">Topic Proficiency</span>
        </div>
      </div>

      {/* 3. Visualizations Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Retention Probability Distribution */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
          <h2 className="text-sm font-bold text-white flex items-center space-x-2 pb-4 border-b border-slate-800">
            <BrainCircuit className="w-4 h-4 text-indigo-400" />
            <span>Retention Probability Distribution</span>
          </h2>
          <div className="h-56 mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={retentionDistData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="range" stroke="#64748b" />
                <YAxis stroke="#64748b" allowDecimals={false} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', color: '#fff' }} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]} name="Students">
                  {retentionDistData.map((entry, index) => (
                    <Cell key={`cell-ret-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Level Distribution */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
          <h2 className="text-sm font-bold text-white flex items-center space-x-2 pb-4 border-b border-slate-800">
            <AlertTriangle className="w-4 h-4 text-rose-400" />
            <span>Risk Level Distribution</span>
          </h2>
          <div className="h-56 mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={riskDistData} layout="vertical" margin={{ top: 10, right: 20, left: 20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" stroke="#64748b" allowDecimals={false} />
                <YAxis type="category" dataKey="name" stroke="#94a3b8" tick={{ fontSize: 11 }} width={100} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', color: '#fff' }} />
                <Bar dataKey="count" radius={[0, 4, 4, 0]} name="Students">
                  {riskDistData.map((entry, index) => (
                    <Cell key={`cell-risk-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 4. Revision Immediate Intervention Panel */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div>
            <h2 className="text-base font-bold text-white flex items-center space-x-2">
              <Zap className="w-4 h-4 text-amber-400" />
              <span>Immediate Revision Action Panel ({immediateRevisionStudents.length} Flagged)</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Students reaching critical decay threshold within 3 days requiring mandatory recall sets.
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-[11px] font-semibold uppercase tracking-wider">
                <th className="py-2.5 px-4">Student</th>
                <th className="py-2.5 px-4">Subject</th>
                <th className="py-2.5 px-4 text-center">Days Remaining</th>
                <th className="py-2.5 px-4">Revision Date</th>
                <th className="py-2.5 px-4 text-center">Priority</th>
                <th className="py-2.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs text-slate-300">
              {immediateRevisionStudents.map((s) => (
                <tr key={s.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4 font-bold text-white">
                    {s.name} ({s.enrollment_number})
                  </td>
                  <td className="py-3 px-4 text-slate-300">
                    {s.subject}
                  </td>
                  <td className="py-3 px-4 text-center font-bold text-rose-400">
                    {s.days_until_forgetting} Day{s.days_until_forgetting > 1 ? 's' : ''}
                  </td>
                  <td className="py-3 px-4 text-slate-400 font-mono">
                    {s.recommended_revision_date}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className="bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2.5 py-0.5 rounded-full font-bold text-[10px]">
                      {s.revision_priority} Priority
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => handleRecommendRevision(s.name)}
                      className="bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-400 border border-indigo-500/30 px-3 py-1 rounded-lg text-xs font-semibold transition-all inline-flex items-center space-x-1"
                    >
                      <Send className="w-3 h-3" />
                      <span>Recommend Revision</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. Filter & Sorting Controls */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Search Input */}
          <div className="relative">
            <input 
              type="text"
              placeholder="Search student, email, ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-xl pl-9 pr-4 py-2.5 focus:outline-none focus:border-indigo-500"
            />
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3 pointer-events-none" />
          </div>

          {/* Subject Filter */}
          <select
            value={subjectFilter}
            onChange={(e) => setSubjectFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-xl px-3 py-2.5 focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            <option value="all">All Subjects</option>
            <option value="17bd775e-8512-4311-965f-fdc9c3979792">Logit Function & AI Logic</option>
            <option value="28ce886f-9623-5422-076f-ged9d4080803">Neural Decay Networks</option>
            <option value="39df9970-0734-6533-187g-hfe0e5191914">Matrix Calculus</option>
          </select>

          {/* Semester Filter */}
          <select
            value={semesterFilter}
            onChange={(e) => setSemesterFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-xl px-3 py-2.5 focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            <option value="all">All Semesters</option>
            <option value="4">Semester 4</option>
            <option value="6">Semester 6</option>
          </select>

          {/* Risk Level Filter */}
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-xl px-3 py-2.5 focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            <option value="all">All Risk Levels</option>
            <option value="critical">Critical Risk</option>
            <option value="high">High Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="low">Low Risk</option>
          </select>

          {/* Knowledge Health Filter */}
          <select
            value={healthFilter}
            onChange={(e) => setHealthFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-xl px-3 py-2.5 focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            <option value="all">All Health Tiers</option>
            <option value="optimal">{"Optimal (>= 80%)"}</option>
            <option value="moderate">{"Moderate (50 - 79%)"}</option>
            <option value="critical">{"Critical (< 50%)"}</option>
          </select>
        </div>

        {/* Sorting Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pt-3 border-t border-slate-800 gap-3">
          <div className="flex items-center space-x-2 text-xs text-slate-400">
            <span>Sort By:</span>
            {(['forget_probability', 'knowledge_health', 'mastery_score', 'name', 'days_until_forgetting'] as const).map((col) => (
              <button
                key={col}
                onClick={() => {
                  if (sortBy === col) {
                    setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
                  } else {
                    setSortBy(col);
                    setSortOrder('desc');
                  }
                }}
                className={`px-3 py-1 rounded-lg border text-xs transition-all ${
                  sortBy === col 
                    ? 'bg-indigo-600/20 text-indigo-400 border-indigo-500/30 font-semibold' 
                    : 'bg-slate-800/60 text-slate-400 border-slate-700 hover:text-white'
                }`}
              >
                {col === 'forget_probability' ? 'Forget Prob' :
                 col === 'knowledge_health' ? 'Knowledge Health' :
                 col === 'mastery_score' ? 'Mastery Score' :
                 col === 'days_until_forgetting' ? 'Revision Due' : 'Student Name'}
                {sortBy === col && (sortOrder === 'desc' ? ' ↓' : ' ↑')}
              </button>
            ))}
          </div>

          <span className="text-xs text-slate-400">
            Showing {filteredAndSortedStudents.length} of {students.length} predictions
          </span>
        </div>
      </div>

      {/* 6. Main Decay Prediction Matrix Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse" aria-label="Faculty Student Prediction Matrix">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-[11px] font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Student</th>
                <th className="py-3 px-4">Student ID</th>
                <th className="py-3 px-4">Subject</th>
                <th className="py-3 px-4 text-center">Forget Prob (%)</th>
                <th className="py-3 px-4 text-center">Knowledge Health</th>
                <th className="py-3 px-4 text-center">Mastery Score</th>
                <th className="py-3 px-4">Predicted Forget Date</th>
                <th className="py-3 px-4">Revision Due</th>
                <th className="py-3 px-4 text-center">Risk Level</th>
                <th className="py-3 px-4 text-center">Confidence</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs text-slate-300">
              {filteredAndSortedStudents.length > 0 ? (
                filteredAndSortedStudents.map((s) => (
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
                    <td className="py-3.5 px-4 text-center font-mono font-bold text-amber-400">
                      {s.forget_probability}
                    </td>
                    <td className="py-3.5 px-4 text-center font-bold text-white">
                      {s.knowledge_health}%
                    </td>
                    <td className="py-3.5 px-4 text-center font-bold text-indigo-400">
                      {s.mastery_score}%
                    </td>
                    <td className="py-3.5 px-4 text-rose-400 font-mono">
                      {s.predicted_forgetting_date}
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 font-mono">
                      {s.recommended_revision_date}
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
                    <td className="py-3.5 px-4 text-center font-mono text-emerald-400 font-medium">
                      {s.confidence_score}%
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end space-x-1.5">
                        <button
                          onClick={() => openStudentModal(s.id)}
                          title="View Details"
                          className="p-1.5 bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-400 border border-indigo-500/30 rounded-lg transition-all"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => generateStudentReport(s.id)}
                          title="Generate Report"
                          className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded-lg transition-all"
                        >
                          <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
                        </button>
                        <button
                          onClick={() => handleRecommendRevision(s.name)}
                          title="Recommend Revision"
                          className="p-1.5 bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-400 border border-indigo-500/30 rounded-lg transition-all"
                        >
                          <Send className="w-3.5 h-3.5 text-indigo-300" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={11} className="py-12 text-center text-slate-500">
                    No prediction records match your active search and filter criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 7. Integrated Deep-Dive Student Details Modal */}
      <StudentDetailsModal
        details={selectedStudentDetails}
        isOpen={isModalOpen}
        onClose={closeStudentModal}
      />
    </div>
  );
}

export default FacultyPredictionPage;
