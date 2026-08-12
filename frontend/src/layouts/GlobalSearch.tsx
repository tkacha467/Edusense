import React, { useState } from 'react';
import { Search } from 'lucide-react';

export function GlobalSearch() {
  const [focused, setFocused] = useState(false);

  return (
    <div className={`relative flex items-center w-full max-w-md transition-all duration-300 ${focused ? 'scale-105' : ''}`}>
      <Search
        className="pointer-events-none absolute inset-y-0 left-3 h-full w-4 text-gray-400"
        aria-hidden="true"
      />
      <input
        id="search-field"
        className="block h-9 w-full rounded-full border-0 py-0 pl-10 pr-4 text-gray-900 bg-gray-100 hover:bg-gray-200 focus:bg-white focus:ring-2 focus:ring-primary focus:outline-none sm:text-sm transition-colors"
        placeholder="Search students, skills, reports... (Cmd+K)"
        type="search"
        name="search"
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
      />
      
      {/* Search results dropdown mockup */}
      {focused && (
        <div className="absolute top-12 left-0 w-full bg-white rounded-xl border shadow-lg z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="p-2">
            <div className="px-3 py-1 text-xs font-semibold text-muted-foreground">Recent</div>
            <div className="px-3 py-2 text-sm hover:bg-gray-100 rounded-md cursor-pointer">Advanced Calculus - Decay Report</div>
            <div className="px-3 py-2 text-sm hover:bg-gray-100 rounded-md cursor-pointer">Diana Evans (Student)</div>
          </div>
        </div>
      )}
    </div>
  );
}
