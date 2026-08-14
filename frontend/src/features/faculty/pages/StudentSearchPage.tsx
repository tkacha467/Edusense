import React, { useState } from 'react';
import { 
  Search, 
  Filter, 
  Users, 
  BrainCircuit, 
  AlertTriangle, 
  Award, 
  Clock, 
  Eye, 
  RotateCcw, 
  AlertCircle,
  ChevronDown
} from 'lucide-react';
import { useStudentData } from '../context/StudentDataContext';
import StudentDetailsModal from '../components/StudentDetailsModal';

export function StudentSearchPage() {
  const { 
    students, 
    openStudentModal, 
    selectedStudentDetails, 
    isModalOpen, 
    closeStudentModal 
  } = useStudentData();

  // Filters State
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [subjectFilter, setSubjectFilter] = useState<string>('all');
  const [riskFilter, setRiskFilter] = useState<string>('all');
  const [masteryFilter, setMasteryFilter] = useState<string>('all');

  // Filter Logic
  const filteredStudents = students.filter(s => {
    const queryMatch = 
      s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.enrollment_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.skills.some(sk => sk.toLowerCase().includes(searchQuery.toLowerCase()));

    const subjectMatch = 
      subjectFilter === 'all' ? true :
      s.subject_id === subjectFilter || s.subject.toLowerCase().includes(subjectFilter.toLowerCase());

    const riskMatch = 
      riskFilter === 'all' ? true :
      riskFilter === 'high' ? (s.risk_level === 'Critical' || s.risk_level === 'High' || s.forget_probability >= 0.5) :
      riskFilter === 'moderate' ? (s.risk_level === 'Medium' || (s.forget_probability >= 0.3 && s.forget_probability < 0.5)) :
      (s.risk_level === 'Low' || s.forget_probability < 0.3);

    const masteryMatch = 
      masteryFilter === 'all' ? true :
      masteryFilter === 'mastered' ? s.status === 'Mastered' :
      masteryFilter === 'review' ? s.status === 'Review Needed' :
      s.status === 'At Risk';

    return queryMatch && subjectMatch && riskMatch && masteryMatch;
  });

  return (
    <div className="space-y-8 p-1 sm:p-2">
      {/* 1. Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl text-white">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <span className="bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 text-xs font-semibold px-3 py-1 rounded-full uppercase tracking-wider">
                Student Intelligence Platform
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
              Student Search & Cognitive Analytics
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Search assigned students, filter retention metrics, and inspect deep-dive forgetting curves.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <span className="text-xs text-slate-400 bg-slate-800 px-3 py-2 rounded-xl border border-slate-700 font-mono">
              Total Cohort: {students.length}
            </span>
          </div>
        </div>
      </div>

      {/* 2. Filters & Search Command Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Search Input */}
          <div className="relative">
            <label htmlFor="search-input" className="sr-only">Search by name, email, or enrollment</label>
            <input 
              id="search-input"
              type="text"
              placeholder="Name, email, skill, or ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-xl pl-9 pr-4 py-3 focus:outline-none focus:border-indigo-500"
            />
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3.5 pointer-events-none" />
          </div>

          {/* Subject Filter */}
          <div className="relative">
            <label htmlFor="subject-select" className="sr-only">Subject Filter</label>
            <select
              id="subject-select"
              value={subjectFilter}
              onChange={(e) => setSubjectFilter(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-xl px-4 py-3 appearance-none cursor-pointer focus:outline-none focus:border-indigo-500"
            >
              <option value="all">All Assigned Subjects</option>
              <option value="17bd775e-8512-4311-965f-fdc9c3979792">Logit Function & AI Logic</option>
              <option value="28ce886f-9623-5422-076f-ged9d4080803">Neural Decay Networks</option>
            </select>
            <ChevronDown className="w-4 h-4 text-slate-400 absolute right-3 top-3.5 pointer-events-none" />
          </div>

          {/* At-Risk Filter */}
          <div className="relative">
            <label htmlFor="risk-select" className="sr-only">Risk Level Filter</label>
            <select
              id="risk-select"
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-xl px-4 py-3 appearance-none cursor-pointer focus:outline-none focus:border-indigo-500"
            >
              <option value="all">All Risk Levels</option>
              <option value="high">{"High Risk (Prob >= 0.50)"}</option>
              <option value="moderate">{"Moderate Decay (0.30 - 0.49)"}</option>
              <option value="low">{"Low Risk (< 0.30)"}</option>
            </select>
            <ChevronDown className="w-4 h-4 text-slate-400 absolute right-3 top-3.5 pointer-events-none" />
          </div>

          {/* Mastery Filter */}
          <div className="relative">
            <label htmlFor="mastery-select" className="sr-only">Mastery Filter</label>
            <select
              id="mastery-select"
              value={masteryFilter}
              onChange={(e) => setMasteryFilter(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-xl px-4 py-3 appearance-none cursor-pointer focus:outline-none focus:border-indigo-500"
            >
              <option value="all">All Mastery Tiers</option>
              <option value="mastered">{"Mastered (>= 80%)"}</option>
              <option value="review">{"Review Needed (50 - 79%)"}</option>
              <option value="at_risk">{"At Risk (< 50%)"}</option>
            </select>
            <ChevronDown className="w-4 h-4 text-slate-400 absolute right-3 top-3.5 pointer-events-none" />
          </div>
        </div>

        {/* Reset Filters Shortcut */}
        {(searchQuery || subjectFilter !== 'all' || riskFilter !== 'all' || masteryFilter !== 'all') && (
          <div className="flex items-center justify-between pt-2">
            <span className="text-xs text-slate-400">
              Showing {filteredStudents.length} of {students.length} students
            </span>
            <button 
              onClick={() => {
                setSearchQuery('');
                setSubjectFilter('all');
                setRiskFilter('all');
                setMasteryFilter('all');
              }}
              className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center space-x-1 font-medium"
            >
              <RotateCcw className="w-3.5 h-3.5 mr-1" />
              <span>Reset All Filters</span>
            </button>
          </div>
        )}
      </div>

      {/* 3. Student Table Grid */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse" aria-label="Student Cognitive Analytics Table">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-xs font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Student Name & Enrollment</th>
                <th className="py-3 px-4">Subject</th>
                <th className="py-3 px-4 text-center">Knowledge Health</th>
                <th className="py-3 px-4 text-center">Retention %</th>
                <th className="py-3 px-4 text-center">Forget Prob.</th>
                <th className="py-3 px-4 text-center">Mastery Score</th>
                <th className="py-3 px-4">Last Revision</th>
                <th className="py-3 px-4 text-center">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs text-slate-300">
              {filteredStudents.length > 0 ? (
                filteredStudents.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4">
                      <div>
                        <p className="font-bold text-white text-sm">{s.name}</p>
                        <p className="text-[10px] text-slate-400 font-mono mt-0.5">{s.enrollment_number} • {s.email}</p>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 font-medium text-indigo-300">
                      {s.subject}
                    </td>
                    <td className="py-3.5 px-4 text-center font-bold text-white">
                      {s.knowledge_health}%
                    </td>
                    <td className="py-3.5 px-4 text-center font-bold text-emerald-400">
                      {s.retention_pct}%
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span className={`font-mono font-bold ${s.forget_probability >= 0.5 ? 'text-rose-400' : 'text-slate-300'}`}>
                        {s.forget_probability}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-center font-bold text-indigo-400">
                      {s.mastery_score}%
                    </td>
                    <td className="py-3.5 px-4 text-slate-400">
                      {s.last_revision}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span className={`px-2.5 py-1 rounded-full font-semibold border ${
                        s.status === 'At Risk' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' :
                        s.status === 'Review Needed' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                        'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      }`}>
                        {s.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => openStudentModal(s.id)}
                        className="inline-flex items-center space-x-1.5 bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-400 border border-indigo-500/30 px-3 py-1.5 rounded-lg font-medium transition-all"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>View Details</span>
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                // Empty State
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-500">
                    <div className="flex flex-col items-center space-y-2">
                      <Search className="w-8 h-8 text-slate-600" />
                      <p className="text-sm font-semibold text-slate-400">No student found matching your filter criteria</p>
                      <button 
                        onClick={() => {
                          setSearchQuery('');
                          setSubjectFilter('all');
                          setRiskFilter('all');
                          setMasteryFilter('all');
                        }}
                        className="text-xs text-indigo-400 hover:underline mt-2 font-medium"
                      >
                        Reset Search Filters
                      </button>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. Deep-Dive Details Modal */}
      <StudentDetailsModal
        details={selectedStudentDetails}
        isOpen={isModalOpen}
        onClose={closeStudentModal}
      />
    </div>
  );
}

export default StudentSearchPage;
