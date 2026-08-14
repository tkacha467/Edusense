import React, { useState, useMemo, useRef, useEffect } from 'react';
import { Search, User, AlertTriangle, BookOpen, Layers } from 'lucide-react';
import { useStudentData } from '../features/faculty/context/StudentDataContext';

export function GlobalSearch() {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const { students, openStudentModal } = useStudentData();

  // Close dropdown on click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Filter students in real time by Name, Student ID, Email, Skill Name, Subject
  const searchResults = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return [];

    return students.filter(student => {
      const matchName = student.name.toLowerCase().includes(q);
      const matchEmail = student.email.toLowerCase().includes(q);
      const matchId = student.enrollment_number.toLowerCase().includes(q) || student.id.toLowerCase().includes(q);
      const matchSubject = student.subject.toLowerCase().includes(q);
      const matchSkill = student.skills && student.skills.some(sk => sk.toLowerCase().includes(q));

      return matchName || matchEmail || matchId || matchSubject || matchSkill;
    }).slice(0, 6);
  }, [query, students]);

  const handleSelectStudent = (studentId: string) => {
    openStudentModal(studentId);
    setIsOpen(false);
    setQuery('');
  };

  return (
    <div className="relative flex items-center w-full max-w-md" ref={dropdownRef}>
      <Search
        className="pointer-events-none absolute inset-y-0 left-3 h-full w-4 text-slate-400"
        aria-hidden="true"
      />
      <input
        id="global-search-field"
        className="block h-9 w-full rounded-full border border-slate-200 py-0 pl-10 pr-4 text-slate-900 bg-white hover:bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none text-xs transition-colors shadow-sm"
        placeholder="Search students, IDs, skills, subjects... (Cmd+K)"
        type="text"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setIsOpen(true);
        }}
        onFocus={() => setIsOpen(true)}
      />
      
      {/* Search results dropdown */}
      {isOpen && query.trim().length > 0 && (
        <div className="absolute top-11 left-0 w-full bg-slate-900 border border-slate-800 rounded-xl shadow-2xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-150">
          <div className="p-2 space-y-1">
            <div className="px-3 py-1 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
              Student Search Results ({searchResults.length})
            </div>

            {searchResults.length > 0 ? (
              searchResults.map((student) => (
                <div 
                  key={student.id}
                  onClick={() => handleSelectStudent(student.id)}
                  className="px-3 py-2 text-xs hover:bg-slate-800 rounded-lg cursor-pointer flex items-center justify-between transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-7 h-7 rounded-full bg-indigo-500/20 text-indigo-400 font-bold text-xs flex items-center justify-center shrink-0">
                      {student.name.charAt(0)}
                    </div>
                    <div>
                      <p className="font-bold text-white leading-tight">{student.name}</p>
                      <p className="text-[10px] text-slate-400 font-mono">
                        {student.enrollment_number} • {student.subject}
                      </p>
                    </div>
                  </div>

                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                    student.risk_level === 'Critical' || student.risk_level === 'High' 
                      ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' 
                      : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                  }`}>
                    {student.risk_level} Risk
                  </span>
                </div>
              ))
            ) : (
              <div className="px-3 py-4 text-center text-xs text-slate-400">
                No matching students found.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
