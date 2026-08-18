import React, { useState, useMemo } from 'react';
import { 
  FileText, 
  Download, 
  Printer, 
  Eye, 
  Trash2, 
  FileSpreadsheet, 
  Users, 
  BrainCircuit, 
  AlertTriangle, 
  Award, 
  TrendingDown, 
  Clock, 
  Search, 
  Filter, 
  Building2, 
  BookOpen, 
  Layers, 
  Sparkles, 
  CheckCircle2, 
  X, 
  Share2,
  Calendar
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
import { useAuth } from '../../contexts/AuthContext';

export interface GeneratedReportItem {
  id: string;
  name: string;
  type: 'Student' | 'Class' | 'Subject' | 'Semester' | 'Department' | 'Institution';
  generatedBy: string;
  generatedOn: string;
  fileFormat: string;
}

export function FacultyReports() {
  const { currentUser: user } = useAuth();
  const { students, atRiskCount } = useStudentData();

  // Filters State
  const [subjectFilter, setSubjectFilter] = useState<string>('all');
  const [semesterFilter, setSemesterFilter] = useState<string>('all');
  const [departmentFilter, setDepartmentFilter] = useState<string>('all');
  const [studentFilter, setStudentFilter] = useState<string>('all');
  const [riskFilter, setRiskFilter] = useState<string>('all');
  const [dateRangeFilter, setDateRangeFilter] = useState<string>('30d');

  // Preview & History State
  const [selectedReportType, setSelectedReportType] = useState<'Student' | 'Class' | 'Subject' | 'Semester' | 'Department' | 'Institution' | null>(null);
  const [isPreviewOpen, setIsPreviewOpen] = useState<boolean>(false);
  
  const [reportHistory, setReportHistory] = useState<GeneratedReportItem[]>([
    {
      id: 'rep_01',
      name: 'Neural Decay Cohort Baseline Report',
      type: 'Class',
      generatedBy: user?.email || 'faculty@edusense.ai',
      generatedOn: '2026-08-14 21:30',
      fileFormat: 'PDF'
    },
    {
      id: 'rep_02',
      name: 'Logit Function Individual Diagnostic (Alex Vance)',
      type: 'Student',
      generatedBy: user?.email || 'faculty@edusense.ai',
      generatedOn: '2026-08-12 14:15',
      fileFormat: 'CSV'
    }
  ]);

  // Filtered dataset for calculations
  const filteredStudents = useMemo(() => {
    return students.filter(s => {
      const matchSubject = subjectFilter === 'all' || s.subject_id === subjectFilter || s.subject.toLowerCase().includes(subjectFilter.toLowerCase());
      const matchSemester = semesterFilter === 'all' || s.semester.toString() === semesterFilter;
      const matchDept = departmentFilter === 'all' || s.department.toLowerCase().includes(departmentFilter.toLowerCase());
      const matchStudent = studentFilter === 'all' || s.id === studentFilter;
      const matchRisk = riskFilter === 'all' || s.risk_level.toLowerCase() === riskFilter.toLowerCase();

      return matchSubject && matchSemester && matchDept && matchStudent && matchRisk;
    });
  }, [students, subjectFilter, semesterFilter, departmentFilter, studentFilter, riskFilter]);

  // Dynamic Report Summary Metrics (No hardcoded values!)
  const reportKPIs = useMemo(() => {
    const totalReports = reportHistory.length;
    const covered = filteredStudents.length;
    const highRisk = filteredStudents.filter(s => s.risk_level === 'Critical' || s.risk_level === 'High' || s.forget_probability >= 0.5).length;
    const avgHealth = covered > 0 ? (filteredStudents.reduce((acc, s) => acc + s.knowledge_health, 0) / covered).toFixed(1) : '0.0';
    const avgMastery = covered > 0 ? (filteredStudents.reduce((acc, s) => acc + s.mastery_score, 0) / covered).toFixed(1) : '0.0';
    const avgForgetProb = covered > 0 ? (filteredStudents.reduce((acc, s) => acc + s.forget_probability, 0) / covered).toFixed(2) : '0.00';

    return { totalReports, covered, highRisk, avgHealth, avgMastery, avgForgetProb };
  }, [reportHistory, filteredStudents]);

  // Handle Report Generation & History Push
  const handleGenerateReport = (type: 'Student' | 'Class' | 'Subject' | 'Semester' | 'Department' | 'Institution') => {
    setSelectedReportType(type);
    setIsPreviewOpen(true);

    const newReport: GeneratedReportItem = {
      id: `rep_${Date.now().toString().slice(-4)}`,
      name: `${type} Knowledge Retention Academic Report`,
      type,
      generatedBy: user?.email || 'faculty@edusense.ai',
      generatedOn: new Date().toISOString().replace('T', ' ').slice(0, 16),
      fileFormat: 'PDF'
    };

    setReportHistory(prev => [newReport, ...prev]);
  };

  const handlePreviewReport = (type: 'Student' | 'Class' | 'Subject' | 'Semester' | 'Department' | 'Institution') => {
    setSelectedReportType(type);
    setIsPreviewOpen(true);
  };

  const handleDeleteHistoryItem = (id: string) => {
    setReportHistory(prev => prev.filter(item => item.id !== id));
  };

  // Export Utilities
  const exportPDF = () => {
    window.print();
  };

  const exportCSV = () => {
    const headers = ['Student Name', 'Enrollment Number', 'Subject', 'Knowledge Health %', 'Forget Probability', 'Mastery Score %', 'Risk Level'];
    const rows = filteredStudents.map(s => [
      `"${s.name}"`,
      `"${s.enrollment_number}"`,
      `"${s.subject}"`,
      s.knowledge_health,
      s.forget_probability,
      s.mastery_score,
      `"${s.risk_level}"`
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `EduSense_${selectedReportType || 'Academic'}_Report_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const exportExcel = () => {
    exportCSV();
  };

  // Chart Data for Report Preview
  const previewDecayData = [
    { day: 'Day 0', retention: 95.0 },
    { day: 'Day 7', retention: 82.5 },
    { day: 'Day 14', retention: 71.0 },
    { day: 'Day 21', retention: 58.4 },
    { day: 'Day 30', retention: 46.2 }
  ];

  const previewRiskData = [
    { name: 'Critical Risk', count: filteredStudents.filter(s => s.risk_level === 'Critical').length, color: '#f43f5e' },
    { name: 'High Risk', count: filteredStudents.filter(s => s.risk_level === 'High').length, color: '#ef4444' },
    { name: 'Medium Risk', count: filteredStudents.filter(s => s.risk_level === 'Medium').length, color: '#f59e0b' },
    { name: 'Low Risk', count: filteredStudents.filter(s => s.risk_level === 'Low').length, color: '#10b981' }
  ];

  return (
    <div className="space-y-8 p-1 sm:p-2">
      {/* 1. Header Command Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl text-white">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <span className="bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 text-xs font-semibold px-3 py-1 rounded-full uppercase tracking-wider">
                Academic Reporting Studio
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
              Faculty Academic Reports & Exports
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Generate, preview, and export professional knowledge decay & retention reports for accreditation and remediation.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <span className="text-xs text-slate-400 bg-slate-800 px-3.5 py-2 rounded-xl border border-slate-700 font-mono">
              Generated Reports: {reportKPIs.totalReports}
            </span>
          </div>
        </div>
      </div>

      {/* 2. Report Summary KPIs Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <span className="text-[11px] text-slate-400 font-semibold uppercase">Total Reports Generated</span>
          <p className="text-2xl font-bold text-white mt-1">{reportKPIs.totalReports}</p>
          <span className="text-[10px] text-slate-500">History Log Counter</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <span className="text-[11px] text-slate-400 font-semibold uppercase">Students Covered</span>
          <p className="text-2xl font-bold text-indigo-400 mt-1">{reportKPIs.covered}</p>
          <span className="text-[10px] text-slate-500">Cohort Reach</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <span className="text-[11px] text-slate-400 font-semibold uppercase">High Risk Students</span>
          <p className="text-2xl font-bold text-rose-400 mt-1">{reportKPIs.highRisk}</p>
          <span className="text-[10px] text-rose-400 font-medium">Requires Attention</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <span className="text-[11px] text-slate-400 font-semibold uppercase">Avg Knowledge Health</span>
          <p className="text-2xl font-bold text-emerald-400 mt-1">{reportKPIs.avgHealth}%</p>
          <span className="text-[10px] text-emerald-400 font-medium">Optimal Retention</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <span className="text-[11px] text-slate-400 font-semibold uppercase">Average Mastery</span>
          <p className="text-2xl font-bold text-violet-400 mt-1">{reportKPIs.avgMastery}%</p>
          <span className="text-[10px] text-slate-500">Topic Proficiency</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <span className="text-[11px] text-slate-400 font-semibold uppercase">Avg Forget Prob.</span>
          <p className="text-2xl font-bold text-amber-400 mt-1">{reportKPIs.avgForgetProb}</p>
          <span className="text-[10px] text-slate-400">Decay Index</span>
        </div>
      </div>

      {/* 3. Global Filters Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
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

          {/* Department Filter */}
          <select
            value={departmentFilter}
            onChange={(e) => setDepartmentFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-xl px-3 py-2.5 focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            <option value="all">All Departments</option>
            <option value="computer science">Computer Science</option>
            <option value="data science">Data Science</option>
          </select>

          {/* Student Filter */}
          <select
            value={studentFilter}
            onChange={(e) => setStudentFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-xl px-3 py-2.5 focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            <option value="all">All Enrolled Students</option>
            {students.map(s => (
              <option key={s.id} value={s.id}>{s.name} ({s.enrollment_number})</option>
            ))}
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

          {/* Date Range Filter */}
          <select
            value={dateRangeFilter}
            onChange={(e) => setDateRangeFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-xl px-3 py-2.5 focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="ay">Academic Year 2025-26</option>
          </select>
        </div>
      </div>

      {/* 4. Report Types Cards Grid (6 Report Types) */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center space-x-2">
          <FileText className="w-5 h-5 text-indigo-400" />
          <span>Select Academic Report Type</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Card 1: Student Report */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between hover:border-indigo-500/40 transition-all">
            <div>
              <div className="w-10 h-10 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center mb-4">
                <Users className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white">Student Report</h3>
              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                Individual student cognitive profile, retention timeline, weak concept skills, and AI remedial recommendations.
              </p>
            </div>
            <div className="flex items-center space-x-2 mt-6 pt-4 border-t border-slate-800">
              <button 
                onClick={() => handleGenerateReport('Student')}
                className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-3 py-2 rounded-xl transition-all shadow-md flex items-center justify-center space-x-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Generate</span>
              </button>
              <button 
                onClick={() => handlePreviewReport('Student')}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold px-3 py-2 rounded-xl transition-all border border-slate-700 flex items-center justify-center space-x-1"
              >
                <Eye className="w-3.5 h-3.5" />
                <span>Preview</span>
              </button>
            </div>
          </div>

          {/* Card 2: Class Report */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between hover:border-indigo-500/40 transition-all">
            <div>
              <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center mb-4">
                <Layers className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white">Class Report</h3>
              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                Comprehensive cohort summary, average retention rates, risk distribution, top performers, and revision completion logs.
              </p>
            </div>
            <div className="flex items-center space-x-2 mt-6 pt-4 border-t border-slate-800">
              <button 
                onClick={() => handleGenerateReport('Class')}
                className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-3 py-2 rounded-xl transition-all shadow-md flex items-center justify-center space-x-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Generate</span>
              </button>
              <button 
                onClick={() => handlePreviewReport('Class')}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold px-3 py-2 rounded-xl transition-all border border-slate-700 flex items-center justify-center space-x-1"
              >
                <Eye className="w-3.5 h-3.5" />
                <span>Preview</span>
              </button>
            </div>
          </div>

          {/* Card 3: Subject Report */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between hover:border-indigo-500/40 transition-all">
            <div>
              <div className="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center mb-4">
                <BookOpen className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white">Subject Report</h3>
              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                Subject-wide average retention, concept skill breakdown, most forgotten topics, and mastery distribution charts.
              </p>
            </div>
            <div className="flex items-center space-x-2 mt-6 pt-4 border-t border-slate-800">
              <button 
                onClick={() => handleGenerateReport('Subject')}
                className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-3 py-2 rounded-xl transition-all shadow-md flex items-center justify-center space-x-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Generate</span>
              </button>
              <button 
                onClick={() => handlePreviewReport('Subject')}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold px-3 py-2 rounded-xl transition-all border border-slate-700 flex items-center justify-center space-x-1"
              >
                <Eye className="w-3.5 h-3.5" />
                <span>Preview</span>
              </button>
            </div>
          </div>

          {/* Card 4: Semester Report */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between hover:border-indigo-500/40 transition-all">
            <div>
              <div className="w-10 h-10 rounded-xl bg-violet-500/20 text-violet-400 flex items-center justify-center mb-4">
                <Calendar className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white">Semester Report</h3>
              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                Semester-wide knowledge retention analysis, exam readiness targets, and multi-cohort retention comparisons.
              </p>
            </div>
            <div className="flex items-center space-x-2 mt-6 pt-4 border-t border-slate-800">
              <button 
                onClick={() => handleGenerateReport('Semester')}
                className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-3 py-2 rounded-xl transition-all shadow-md flex items-center justify-center space-x-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Generate</span>
              </button>
              <button 
                onClick={() => handlePreviewReport('Semester')}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold px-3 py-2 rounded-xl transition-all border border-slate-700 flex items-center justify-center space-x-1"
              >
                <Eye className="w-3.5 h-3.5" />
                <span>Preview</span>
              </button>
            </div>
          </div>

          {/* Card 5: Department Report */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between hover:border-indigo-500/40 transition-all">
            <div>
              <div className="w-10 h-10 rounded-xl bg-rose-500/20 text-rose-400 flex items-center justify-center mb-4">
                <Building2 className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white">Department Report</h3>
              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                Departmental KPIs, top performing and weak subjects, faculty intervention summary, and academic health metrics.
              </p>
            </div>
            <div className="flex items-center space-x-2 mt-6 pt-4 border-t border-slate-800">
              <button 
                onClick={() => handleGenerateReport('Department')}
                className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-3 py-2 rounded-xl transition-all shadow-md flex items-center justify-center space-x-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Generate</span>
              </button>
              <button 
                onClick={() => handlePreviewReport('Department')}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold px-3 py-2 rounded-xl transition-all border border-slate-700 flex items-center justify-center space-x-1"
              >
                <Eye className="w-3.5 h-3.5" />
                <span>Preview</span>
              </button>
            </div>
          </div>

          {/* Card 6: Institution Report */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between hover:border-indigo-500/40 transition-all">
            <div>
              <div className="w-10 h-10 rounded-xl bg-sky-500/20 text-sky-400 flex items-center justify-center mb-4">
                <Award className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white">Institution Report</h3>
              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                Executive institutional retention metrics, accreditation compliance summary, and campus-wide longitudinal memory decay logs.
              </p>
            </div>
            <div className="flex items-center space-x-2 mt-6 pt-4 border-t border-slate-800">
              <button 
                onClick={() => handleGenerateReport('Institution')}
                className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-3 py-2 rounded-xl transition-all shadow-md flex items-center justify-center space-x-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Generate</span>
              </button>
              <button 
                onClick={() => handlePreviewReport('Institution')}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold px-3 py-2 rounded-xl transition-all border border-slate-700 flex items-center justify-center space-x-1"
              >
                <Eye className="w-3.5 h-3.5" />
                <span>Preview</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 5. Report History Log Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h2 className="text-base font-bold text-white flex items-center space-x-2">
              <Clock className="w-4 h-4 text-indigo-400" />
              <span>Report Generation History ({reportHistory.length})</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              History log of all academic reports generated during active session.
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse" aria-label="Report Generation History Table">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-xs font-semibold uppercase tracking-wider">
                <th className="py-2.5 px-4">Report Name</th>
                <th className="py-2.5 px-4">Report Type</th>
                <th className="py-2.5 px-4">Generated By</th>
                <th className="py-2.5 px-4">Generated On</th>
                <th className="py-2.5 px-4 text-center">Format</th>
                <th className="py-2.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs text-slate-300">
              {reportHistory.map((item) => (
                <tr key={item.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4 font-bold text-white">
                    {item.name}
                  </td>
                  <td className="py-3 px-4">
                    <span className="bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2.5 py-0.5 rounded-full font-semibold text-[10px]">
                      {item.type} Report
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-400">{item.generatedBy}</td>
                  <td className="py-3 px-4 text-slate-400 font-mono">{item.generatedOn}</td>
                  <td className="py-3 px-4 text-center font-bold text-emerald-400">{item.fileFormat}</td>
                  <td className="py-3 px-4 text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={exportPDF}
                        className="p-1.5 bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-400 border border-indigo-500/30 rounded-lg transition-all"
                        title="Download Report"
                      >
                        <Download className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDeleteHistoryItem(item.id)}
                        className="p-1.5 bg-rose-500/20 hover:bg-rose-500/40 text-rose-400 border border-rose-500/30 rounded-lg transition-all"
                        title="Delete Entry"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 6. Report Preview Modal */}
      {isPreviewOpen && selectedReportType && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200"
          role="dialog"
          aria-modal="true"
        >
          <div className="bg-slate-900 border border-slate-800 w-full max-w-4xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
            {/* Modal Bar */}
            <div className="p-6 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
              <div>
                <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">Academic Report Preview</span>
                <h2 className="text-xl font-bold text-white mt-0.5">{selectedReportType} Academic Report</h2>
              </div>
              
              <div className="flex items-center space-x-3">
                <button
                  onClick={exportPDF}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-3 py-2 rounded-xl transition-all shadow-md flex items-center space-x-1.5"
                >
                  <Printer className="w-3.5 h-3.5" />
                  <span>Print / PDF</span>
                </button>
                <button
                  onClick={exportCSV}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold px-3 py-2 rounded-xl transition-all flex items-center space-x-1.5"
                >
                  <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
                  <span>CSV</span>
                </button>
                <button
                  onClick={exportExcel}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold px-3 py-2 rounded-xl transition-all flex items-center space-x-1.5"
                >
                  <FileText className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Excel</span>
                </button>
                <button 
                  onClick={() => setIsPreviewOpen(false)}
                  className="p-2 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-xl transition-all"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Document Content Body */}
            <div className="p-8 overflow-y-auto space-y-6 flex-1 text-slate-200 bg-slate-900">
              {/* Document Header Metadata */}
              <div className="p-6 bg-slate-950 border border-slate-800 rounded-xl flex flex-col sm:flex-row justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold text-white">EduSense AI Academic Intelligence Platform</h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Institution: Engineering Institute • Department: Computer Science
                  </p>
                  <p className="text-xs text-slate-400">
                    Faculty Evaluator: {user?.email || 'faculty@edusense.ai'}
                  </p>
                </div>
                <div className="text-right text-xs text-slate-400">
                  <p className="font-mono">Date: 2026-08-14</p>
                  <p className="font-mono mt-1">Status: Verified Academic Export</p>
                </div>
              </div>

              {/* Summary KPIs Row */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="bg-slate-950/60 border border-slate-800 p-4 rounded-xl">
                  <span className="text-xs text-slate-400">Knowledge Health</span>
                  <p className="text-xl font-bold text-white mt-1">{reportKPIs.avgHealth}%</p>
                </div>
                <div className="bg-slate-950/60 border border-slate-800 p-4 rounded-xl">
                  <span className="text-xs text-slate-400">Forget Probability</span>
                  <p className="text-xl font-bold text-amber-400 mt-1">{reportKPIs.avgForgetProb}</p>
                </div>
                <div className="bg-slate-950/60 border border-slate-800 p-4 rounded-xl">
                  <span className="text-xs text-slate-400">Average Mastery</span>
                  <p className="text-xl font-bold text-indigo-400 mt-1">{reportKPIs.avgMastery}%</p>
                </div>
                <div className="bg-slate-950/60 border border-slate-800 p-4 rounded-xl">
                  <span className="text-xs text-slate-400">High Risk Count</span>
                  <p className="text-xl font-bold text-rose-400 mt-1">{reportKPIs.highRisk} Students</p>
                </div>
              </div>

              {/* Charts Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-slate-950/60 border border-slate-800 p-5 rounded-xl">
                  <h4 className="text-xs font-bold text-white mb-3">Predicted Retention Curve</h4>
                  <div className="h-44">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={previewDecayData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                        <XAxis dataKey="day" stroke="#64748b" tick={{ fontSize: 10 }} />
                        <YAxis stroke="#64748b" domain={[0, 100]} tick={{ fontSize: 10 }} />
                        <Line type="monotone" dataKey="retention" stroke="#6366f1" strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="bg-slate-950/60 border border-slate-800 p-5 rounded-xl">
                  <h4 className="text-xs font-bold text-white mb-3">Risk Distribution Summary</h4>
                  <div className="h-44">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={previewRiskData} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                        <XAxis type="number" stroke="#64748b" allowDecimals={false} />
                        <YAxis type="category" dataKey="name" stroke="#94a3b8" tick={{ fontSize: 10 }} width={90} />
                        <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                          {previewRiskData.map((entry, index) => (
                            <Cell key={`cell-pr-${index}`} fill={entry.color} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              {/* Detailed Student List Table */}
              <div className="bg-slate-950/60 border border-slate-800 p-5 rounded-xl space-y-3">
                <h4 className="text-xs font-bold text-white">Evaluated Cohort Members</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase">
                        <th className="py-2 px-3">Student Name</th>
                        <th className="py-2 px-3">ID</th>
                        <th className="py-2 px-3 text-center">Health %</th>
                        <th className="py-2 px-3 text-center">Forget Prob</th>
                        <th className="py-2 px-3 text-center">Risk</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 text-slate-300">
                      {filteredStudents.slice(0, 5).map(s => (
                        <tr key={s.id}>
                          <td className="py-2 px-3 font-bold text-white">{s.name}</td>
                          <td className="py-2 px-3 font-mono text-indigo-300">{s.enrollment_number}</td>
                          <td className="py-2 px-3 text-center font-bold">{s.knowledge_health}%</td>
                          <td className="py-2 px-3 text-center font-mono text-rose-400">{s.forget_probability}</td>
                          <td className="py-2 px-3 text-center">
                            <span className="bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2 py-0.5 rounded-full text-[10px]">
                              {s.risk_level}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* AI Remedial Recommendations */}
              <div className="bg-slate-950/60 border border-slate-800 p-5 rounded-xl space-y-2">
                <h4 className="text-xs font-bold text-white flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  <span>AI Academic Remediation Recommendations</span>
                </h4>
                <p className="text-xs text-slate-400">
                  Based on Ebbinghaus memory decay predictions, dispatch remedial practice sets on <span className="text-indigo-400 font-semibold">Logit Function Complexity</span> and <span className="text-indigo-400 font-semibold">Gradient Descent Rates</span> to prevent further memory degradation.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default FacultyReports;
