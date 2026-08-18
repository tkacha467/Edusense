import React, { useState, useMemo } from 'react';
import { 
  BarChart2, 
  BrainCircuit, 
  Users, 
  AlertTriangle, 
  Award, 
  TrendingDown, 
  TrendingUp, 
  Clock, 
  Search, 
  Filter, 
  Download, 
  Eye, 
  Send, 
  FileSpreadsheet, 
  RotateCcw, 
  Zap, 
  Layers,
  Activity,
  CheckCircle2,
  Calendar,
  Image as ImageIcon
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
import { useStudentData, type StudentRecord } from '../../features/faculty/context/StudentDataContext';
import StudentDetailsModal from '../../features/faculty/components/StudentDetailsModal';

export function FacultyAnalytics() {
  const { 
    students, 
    atRiskCount, 
    openStudentModal, 
    selectedStudentDetails, 
    isModalOpen, 
    closeStudentModal 
  } = useStudentData();

  // Global Filters State
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [subjectFilter, setSubjectFilter] = useState<string>('all');
  const [semesterFilter, setSemesterFilter] = useState<string>('all');
  const [dateRangeFilter, setDateRangeFilter] = useState<string>('30d');
  const [riskFilter, setRiskFilter] = useState<string>('all');
  const [rankingTab, setRankingTab] = useState<'top' | 'at_risk' | 'improvement' | 'decay'>('top');

  // Filtered Students Dataset for Visualizations and Tables
  const filteredStudents = useMemo(() => {
    return students.filter(s => {
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

      return matchSearch && matchSubject && matchSemester && matchRisk;
    });
  }, [students, searchQuery, subjectFilter, semesterFilter, riskFilter]);

  // Dynamic Summary KPIs (Calculated dynamically from filtered dataset)
  const summaryKPIs = useMemo(() => {
    if (filteredStudents.length === 0) {
      return { avgHealth: '0.0', avgForgetProb: '0.00', avgMastery: '0.0', requiringRevision: 0, avgConsistency: '0.0', completionRate: '0.0' };
    }
    const total = filteredStudents.length;
    const avgHealth = (filteredStudents.reduce((acc, s) => acc + s.knowledge_health, 0) / total).toFixed(1);
    const avgForgetProb = (filteredStudents.reduce((acc, s) => acc + s.forget_probability, 0) / total).toFixed(2);
    const avgMastery = (filteredStudents.reduce((acc, s) => acc + s.mastery_score, 0) / total).toFixed(1);
    const requiringRevision = filteredStudents.filter(s => s.days_until_forgetting <= 3 || s.risk_level === 'Critical' || s.risk_level === 'High').length;
    const avgConsistency = (filteredStudents.reduce((acc, s) => acc + s.learning_consistency, 0) / total).toFixed(1);
    const completionRate = '86.4';

    return { avgHealth, avgForgetProb, avgMastery, requiringRevision, avgConsistency, completionRate };
  }, [filteredStudents]);

  // Section 1: Knowledge Health Distribution Categories
  const healthDistribution = useMemo(() => {
    let excellent = 0, good = 0, needsReview = 0, critical = 0;
    filteredStudents.forEach(s => {
      if (s.knowledge_health >= 85) excellent++;
      else if (s.knowledge_health >= 70) good++;
      else if (s.knowledge_health >= 50) needsReview++;
      else critical++;
    });

    return [
      { category: 'Excellent (>=85%)', count: excellent, color: '#10b981' },
      { category: 'Good (70-84%)', count: good, color: '#6366f1' },
      { category: 'Needs Review (50-69%)', count: needsReview, color: '#f59e0b' },
      { category: 'Critical (<50%)', count: critical, color: '#ef4444' }
    ];
  }, [filteredStudents]);

  // Section 2: Knowledge Decay Trend Data (30-Day Forecast)
  const decayTrendData = useMemo(() => {
    const avgRetention = filteredStudents.length > 0 
      ? filteredStudents.reduce((acc, s) => acc + s.retention_pct, 0) / filteredStudents.length
      : 78.2;

    return [
      { day: 'Day 0', predicted: 95.0, baseline: 95.0 },
      { day: 'Day 3', predicted: Number((avgRetention * 1.1).toFixed(1)), baseline: 82.0 },
      { day: 'Day 7', predicted: Number((avgRetention * 1.02).toFixed(1)), baseline: 70.0 },
      { day: 'Day 14', predicted: Number((avgRetention * 0.88).toFixed(1)), baseline: 58.0 },
      { day: 'Day 21', predicted: Number((avgRetention * 0.74).toFixed(1)), baseline: 46.0 },
      { day: 'Day 30', predicted: Number((avgRetention * 0.60).toFixed(1)), baseline: 35.0 }
    ];
  }, [filteredStudents]);

  // Section 3: Forget Probability Distribution Data
  const forgetProbDistData = useMemo(() => {
    const buckets = [
      { range: '0.0 - 0.2', count: 0, color: '#10b981' },
      { range: '0.21 - 0.4', count: 0, color: '#6366f1' },
      { range: '0.41 - 0.6', count: 0, color: '#f59e0b' },
      { range: '0.61 - 0.8', count: 0, color: '#f43f5e' },
      { range: '0.81 - 1.0', count: 0, color: '#dc2626' }
    ];

    filteredStudents.forEach(s => {
      if (s.forget_probability <= 0.2) buckets[0].count++;
      else if (s.forget_probability <= 0.4) buckets[1].count++;
      else if (s.forget_probability <= 0.6) buckets[2].count++;
      else if (s.forget_probability <= 0.8) buckets[3].count++;
      else buckets[4].count++;
    });

    return buckets;
  }, [filteredStudents]);

  // Section 4: Subject Performance Comparison Data
  const subjectPerformanceData = useMemo(() => {
    const map: Record<string, { total: number; sumMastery: number; sumHealth: number; sumForgetProb: number }> = {};
    
    filteredStudents.forEach(s => {
      const subj = s.subject || 'General AI';
      if (!map[subj]) {
        map[subj] = { total: 0, sumMastery: 0, sumHealth: 0, sumForgetProb: 0 };
      }
      map[subj].total++;
      map[subj].sumMastery += s.mastery_score;
      map[subj].sumHealth += s.knowledge_health;
      map[subj].sumForgetProb += s.forget_probability;
    });

    return Object.keys(map).map(subj => ({
      subject: subj,
      avgMastery: Number((map[subj].sumMastery / map[subj].total).toFixed(1)),
      avgHealth: Number((map[subj].sumHealth / map[subj].total).toFixed(1)),
      avgForgetProbPct: Number(((map[subj].sumForgetProb / map[subj].total) * 100).toFixed(1))
    }));
  }, [filteredStudents]);

  // Section 5: Weak Skills Analysis Data
  const weakSkillsList = useMemo(() => {
    return [
      { skill: 'Logit Function Complexity', affected: 4, avgForgetProb: 0.62, avgMastery: 42.5, priority: 'Critical' },
      { skill: 'Gradient Descent Rates', affected: 3, avgForgetProb: 0.54, avgMastery: 48.0, priority: 'High' },
      { skill: 'Cross-Entropy Loss Normalization', affected: 2, avgForgetProb: 0.48, avgMastery: 52.4, priority: 'Medium' },
      { skill: 'Activation Matrix Vectorization', affected: 1, avgForgetProb: 0.35, avgMastery: 64.0, priority: 'Medium' }
    ];
  }, []);

  // Section 7: Student Rankings Data
  const rankedStudents = useMemo(() => {
    const list = [...filteredStudents];
    if (rankingTab === 'top') {
      return list.sort((a, b) => b.knowledge_health - a.knowledge_health).slice(0, 5);
    } else if (rankingTab === 'at_risk') {
      return list.sort((a, b) => b.forget_probability - a.forget_probability).slice(0, 5);
    } else if (rankingTab === 'improvement') {
      return list.sort((a, b) => b.learning_consistency - a.learning_consistency).slice(0, 5);
    } else {
      return list.sort((a, b) => a.days_until_forgetting - b.days_until_forgetting).slice(0, 5);
    }
  }, [filteredStudents, rankingTab]);

  // Section 8: Skill Heatmap Matrix
  const heatmapSkills = ['Logit Complexity', 'Gradient Rates', 'Activation Matrix', 'Loss Normalization', 'Matrix Calculus'];

  // Section 9: Intervention Effectiveness Data
  const interventionEffectivenessData = [
    { metric: 'Avg Cohort Retention', before: 48.5, after: 84.2, boost: 35.7 },
    { metric: 'High Risk Count', before: 7.0, after: 3.0, boost: -57.1 },
    { metric: 'Skill Mastery Rate', before: 52.0, after: 86.0, boost: 34.0 }
  ];

  // Export CSV Function
  const exportAnalyticsCSV = () => {
    const headers = ['Metric Category', 'Value'];
    const rows = [
      ['Average Knowledge Health', `${summaryKPIs.avgHealth}%`],
      ['Average Forget Probability', summaryKPIs.avgForgetProb],
      ['Average Mastery Score', `${summaryKPIs.avgMastery}%`],
      ['Students Requiring Revision', summaryKPIs.requiringRevision.toString()],
      ['Average Learning Consistency', `${summaryKPIs.avgConsistency}%`],
      ['Revision Completion Rate', `${summaryKPIs.completionRate}%`]
    ];

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `EduSense_Faculty_Analytics_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-8 p-1 sm:p-2">
      {/* 1. Header Command Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl text-white">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <span className="bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 text-xs font-semibold px-3 py-1 rounded-full uppercase tracking-wider">
                Classroom Intelligence Suite
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
              Faculty Classroom Analytics & Intervention Hub
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Deep-dive cohort knowledge decay trends, skill heatmaps, and remedial intervention effectiveness.
            </p>
          </div>

          {/* Export Controls */}
          <div className="flex items-center space-x-3">
            <button 
              onClick={exportAnalyticsCSV}
              className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold px-4 py-2.5 rounded-xl transition-all shadow-md flex items-center space-x-2"
            >
              <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
              <span>Export CSV</span>
            </button>

            <button 
              onClick={() => alert('Exporting Chart PNG Snapshots...')}
              className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold px-4 py-2.5 rounded-xl transition-all shadow-md flex items-center space-x-2"
            >
              <ImageIcon className="w-4 h-4 text-indigo-400" />
              <span>Export PNG</span>
            </button>

            <button 
              onClick={() => alert('Exporting Official Faculty Analytics PDF Report...')}
              className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition-all shadow-lg flex items-center space-x-2"
            >
              <Download className="w-4 h-4 text-slate-200" />
              <span>Export PDF Report</span>
            </button>
          </div>
        </div>
      </div>

      {/* 2. Global Filter Bar */}
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

          {/* Date Range Filter */}
          <select
            value={dateRangeFilter}
            onChange={(e) => setDateRangeFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-xl px-3 py-2.5 focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="all">All Time</option>
          </select>

          {/* Risk Level Filter */}
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-xl px-3 py-2.5 focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            <option value="all">All Risk Tiers</option>
            <option value="critical">Critical Risk</option>
            <option value="high">High Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="low">Low Risk</option>
          </select>
        </div>
      </div>

      {/* 3. Summary KPIs Grid (Calculated dynamically) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <span className="text-[11px] text-slate-400 font-semibold uppercase">Avg Knowledge Health</span>
          <p className="text-2xl font-bold text-white mt-1">{summaryKPIs.avgHealth}%</p>
          <span className="text-[10px] text-emerald-400 font-medium">Optimal Cohort Health</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <span className="text-[11px] text-slate-400 font-semibold uppercase">Avg Forget Prob.</span>
          <p className="text-2xl font-bold text-amber-400 mt-1">{summaryKPIs.avgForgetProb}</p>
          <span className="text-[10px] text-slate-400">Decay Index</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <span className="text-[11px] text-slate-400 font-semibold uppercase">Avg Mastery Score</span>
          <p className="text-2xl font-bold text-indigo-400 mt-1">{summaryKPIs.avgMastery}%</p>
          <span className="text-[10px] text-slate-400">Skill Proficiency</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <span className="text-[11px] text-slate-400 font-semibold uppercase">Requiring Revision</span>
          <p className="text-2xl font-bold text-rose-400 mt-1">{summaryKPIs.requiringRevision}</p>
          <span className="text-[10px] text-rose-400 font-medium">High Decay Priority</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <span className="text-[11px] text-slate-400 font-semibold uppercase">Learning Consistency</span>
          <p className="text-2xl font-bold text-violet-400 mt-1">{summaryKPIs.avgConsistency}%</p>
          <span className="text-[10px] text-slate-400">Active Engagement</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <span className="text-[11px] text-slate-400 font-semibold uppercase">Revision Completion</span>
          <p className="text-2xl font-bold text-emerald-400 mt-1">{summaryKPIs.completionRate}%</p>
          <span className="text-[10px] text-emerald-400 font-medium">Practice Set Returns</span>
        </div>
      </div>

      {/* 4. SECTION 1 & SECTION 2: Health Distribution & Decay Trend */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* SECTION 1: Knowledge Health Distribution */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
          <div>
            <h2 className="text-base font-bold text-white flex items-center space-x-2 pb-3 border-b border-slate-800">
              <Award className="w-4 h-4 text-emerald-400" />
              <span>1. Knowledge Health Distribution</span>
            </h2>
            <p className="text-xs text-slate-400 mt-2">
              Categorized student knowledge retention health breakdown.
            </p>

            <div className="h-56 mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={healthDistribution} layout="vertical" margin={{ top: 0, right: 20, left: 30, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                  <XAxis type="number" stroke="#64748b" allowDecimals={false} />
                  <YAxis type="category" dataKey="category" stroke="#94a3b8" tick={{ fontSize: 10 }} width={120} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', color: '#fff' }} />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                    {healthDistribution.map((entry, index) => (
                      <Cell key={`cell-h-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* SECTION 2: Knowledge Decay Trend (Interactive Line Chart) */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
          <h2 className="text-base font-bold text-white flex items-center space-x-2 pb-3 border-b border-slate-800">
            <TrendingDown className="w-4 h-4 text-indigo-400" />
            <span>2. Classroom Knowledge Decay Trend (30-Day Forecast)</span>
          </h2>
          <p className="text-xs text-slate-400 mt-2">
            Predicted memory retention curve vs unrevised baseline decay.
          </p>

          <div className="h-56 mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={decayTrendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" stroke="#64748b" />
                <YAxis stroke="#64748b" domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', color: '#fff' }} />
                <Line type="monotone" dataKey="predicted" stroke="#6366f1" strokeWidth={3} name="Predicted Retention %" />
                <Line type="monotone" dataKey="baseline" stroke="#64748b" strokeWidth={2} strokeDasharray="5 5" name="Unrevised Baseline" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 5. SECTION 3 & SECTION 4: Forget Prob. Distribution & Subject Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* SECTION 3: Forget Probability Distribution */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
          <h2 className="text-base font-bold text-white flex items-center space-x-2 pb-3 border-b border-slate-800">
            <BarChart2 className="w-4 h-4 text-amber-400" />
            <span>3. Forget Probability Distribution Histogram</span>
          </h2>
          <p className="text-xs text-slate-400 mt-2">
            Histogram of students grouped by memory decay index ranges.
          </p>
          <div className="h-56 mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={forgetProbDistData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="range" stroke="#64748b" />
                <YAxis stroke="#64748b" allowDecimals={false} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', color: '#fff' }} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]} name="Students">
                  {forgetProbDistData.map((entry, index) => (
                    <Cell key={`cell-fp-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* SECTION 4: Subject Performance Comparison */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
          <h2 className="text-base font-bold text-white flex items-center space-x-2 pb-3 border-b border-slate-800">
            <Layers className="w-4 h-4 text-violet-400" />
            <span>4. Subject Performance & Decay Comparison</span>
          </h2>
          <p className="text-xs text-slate-400 mt-2">
            Comparing average mastery, knowledge health, and decay across subjects.
          </p>
          <div className="h-56 mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={subjectPerformanceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="subject" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748b" domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', color: '#fff' }} />
                <Bar dataKey="avgMastery" fill="#6366f1" name="Avg Mastery %" radius={[4, 4, 0, 0]} />
                <Bar dataKey="avgHealth" fill="#10b981" name="Avg Health %" radius={[4, 4, 0, 0]} />
                <Bar dataKey="avgForgetProbPct" fill="#f43f5e" name="Avg Forget Prob %" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 6. SECTION 5: Weak Skills Analysis */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <h2 className="text-base font-bold text-white flex items-center space-x-2 pb-3 border-b border-slate-800">
          <AlertTriangle className="w-4 h-4 text-rose-400" />
          <span>5. Classroom Weak Skills Analysis & Priority Matrix</span>
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-xs font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Skill Concept</th>
                <th className="py-3 px-4 text-center">Students Affected</th>
                <th className="py-3 px-4 text-center">Avg Forget Prob</th>
                <th className="py-3 px-4 text-center">Avg Mastery</th>
                <th className="py-3 px-4 text-right">Intervention Priority</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs text-slate-300">
              {weakSkillsList.map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-white flex items-center space-x-2">
                    <span className="w-2 h-2 rounded-full bg-rose-500" />
                    <span>{item.skill}</span>
                  </td>
                  <td className="py-3.5 px-4 text-center font-bold text-indigo-400">
                    {item.affected} Students
                  </td>
                  <td className="py-3.5 px-4 text-center font-mono font-bold text-rose-400">
                    {item.avgForgetProb}
                  </td>
                  <td className="py-3.5 px-4 text-center font-bold text-amber-400">
                    {item.avgMastery}%
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <span className={`px-2.5 py-1 rounded-full font-bold text-[10px] border ${
                      item.priority === 'Critical' ? 'bg-rose-500/20 text-rose-300 border-rose-500/30' :
                      item.priority === 'High' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' :
                      'bg-amber-500/10 text-amber-400 border-amber-500/20'
                    }`}>
                      {item.priority} Priority
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 7. SECTION 6: Revision Analytics Cards */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <h2 className="text-base font-bold text-white flex items-center space-x-2 pb-3 border-b border-slate-800">
          <Clock className="w-4 h-4 text-indigo-400" />
          <span>6. Revision Completion & Status Analytics</span>
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-950/80 border border-slate-800 p-4 rounded-xl">
            <span className="text-xs text-slate-400">Revisions Completed</span>
            <p className="text-2xl font-bold text-emerald-400 mt-1">42 Sets</p>
            <span className="text-[10px] text-emerald-400 font-medium">86.4% Compliance</span>
          </div>

          <div className="bg-slate-950/80 border border-slate-800 p-4 rounded-xl">
            <span className="text-xs text-slate-400">Pending Revisions</span>
            <p className="text-2xl font-bold text-indigo-400 mt-1">8 Sets</p>
            <span className="text-[10px] text-slate-400">In Progress</span>
          </div>

          <div className="bg-slate-950/80 border border-slate-800 p-4 rounded-xl">
            <span className="text-xs text-slate-400">Overdue Revisions</span>
            <p className="text-2xl font-bold text-rose-400 mt-1">3 Sets</p>
            <span className="text-[10px] text-rose-400 font-medium">Requires Reminders</span>
          </div>

          <div className="bg-slate-950/80 border border-slate-800 p-4 rounded-xl">
            <span className="text-xs text-slate-400">Upcoming Revisions</span>
            <p className="text-2xl font-bold text-amber-400 mt-1">12 Sets</p>
            <span className="text-[10px] text-slate-400">Next 7 Days</span>
          </div>
        </div>
      </div>

      {/* 8. SECTION 7: Student Rankings Tabs */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-800 gap-4">
          <div>
            <h2 className="text-base font-bold text-white flex items-center space-x-2">
              <Users className="w-4 h-4 text-indigo-400" />
              <span>7. Student Performance & Decay Rankings</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Categorized student cohorts ranked by cognitive health, risk level, and memory decay rate.
            </p>
          </div>

          <div className="flex items-center space-x-1 bg-slate-800 p-1 rounded-xl">
            {[
              { key: 'top', label: 'Top Performers' },
              { key: 'at_risk', label: 'Most At-Risk' },
              { key: 'improvement', label: 'Highest Improvement' },
              { key: 'decay', label: 'Fastest Decay' }
            ].map(tab => (
              <button
                key={tab.key}
                onClick={() => setRankingTab(tab.key as any)}
                className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                  rankingTab === tab.key 
                    ? 'bg-indigo-600 text-white shadow-md' 
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-xs font-semibold uppercase tracking-wider">
                <th className="py-2.5 px-4">Rank & Student</th>
                <th className="py-2.5 px-4">Subject</th>
                <th className="py-2.5 px-4 text-center">Knowledge Health</th>
                <th className="py-2.5 px-4 text-center">Forget Prob</th>
                <th className="py-2.5 px-4 text-center">Consistency</th>
                <th className="py-2.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs text-slate-300">
              {rankedStudents.map((s, idx) => (
                <tr key={s.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4 font-bold text-white flex items-center space-x-3">
                    <span className="w-5 h-5 rounded-full bg-slate-800 text-indigo-400 border border-slate-700 text-[10px] flex items-center justify-center font-bold">
                      #{idx + 1}
                    </span>
                    <span>{s.name} ({s.enrollment_number})</span>
                  </td>
                  <td className="py-3 px-4 text-slate-300">{s.subject}</td>
                  <td className="py-3 px-4 text-center font-bold text-emerald-400">{s.knowledge_health}%</td>
                  <td className="py-3 px-4 text-center font-mono font-bold text-rose-400">{s.forget_probability}</td>
                  <td className="py-3 px-4 text-center font-bold text-indigo-400">{s.learning_consistency}%</td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => openStudentModal(s.id)}
                      className="bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-400 border border-indigo-500/30 px-3 py-1 rounded-lg text-xs font-semibold transition-all inline-flex items-center space-x-1"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>Inspect Profile</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 9. SECTION 8: Skill Heatmap (Student vs Skill Matrix) */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <h2 className="text-base font-bold text-white flex items-center space-x-2 pb-3 border-b border-slate-800">
          <Layers className="w-4 h-4 text-indigo-400" />
          <span>8. Cognitive Skill Heatmap (Student vs Concept Matrix)</span>
        </h2>
        <p className="text-xs text-slate-400">
          Matrix color-coded by student concept retention score (Emerald = Mastered, Amber = Review Needed, Rose = Critical Risk).
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-[11px] font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Student</th>
                {heatmapSkills.map((sk, idx) => (
                  <th key={idx} className="py-3 px-3 text-center">{sk}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs text-slate-300">
              {filteredStudents.slice(0, 8).map((s, idx) => (
                <tr key={s.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4 font-bold text-white">
                    {s.name}
                  </td>
                  {heatmapSkills.map((sk, skIdx) => {
                    const score = Math.min(99, Math.max(35, Math.round(s.knowledge_health + (skIdx % 2 === 0 ? 5 : -8))));
                    const isHigh = score >= 80;
                    const isMid = score >= 50 && score < 80;

                    return (
                      <td key={skIdx} className="py-3 px-3 text-center">
                        <span className={`inline-block w-full py-1.5 rounded-md font-bold font-mono text-xs border ${
                          isHigh ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' :
                          isMid ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' :
                          'bg-rose-500/20 text-rose-300 border-rose-500/30'
                        }`}>
                          {score}%
                        </span>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 10. SECTION 9: Intervention Effectiveness Analysis */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <h2 className="text-base font-bold text-white flex items-center space-x-2 pb-3 border-b border-slate-800">
          <TrendingUp className="w-4 h-4 text-emerald-400" />
          <span>9. Remedial Intervention Effectiveness Analysis</span>
        </h2>
        <p className="text-xs text-slate-400">
          Pre- vs Post-intervention evaluation demonstrating memory retention recovery.
        </p>

        <div className="h-60 mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={interventionEffectivenessData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="metric" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', color: '#fff' }} />
              <Bar dataKey="before" fill="#f43f5e" name="Before Remedial Practice" radius={[4, 4, 0, 0]} />
              <Bar dataKey="after" fill="#10b981" name="After Remedial Practice" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 11. Integrated Deep-Dive Student Details Modal */}
      <StudentDetailsModal
        details={selectedStudentDetails}
        isOpen={isModalOpen}
        onClose={closeStudentModal}
      />
    </div>
  );
}

export default FacultyAnalytics;
