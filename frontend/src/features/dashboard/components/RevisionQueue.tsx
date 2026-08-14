import React, { useState, useMemo } from 'react';
import { Search, ChevronDown, ChevronUp, ChevronLeft, ChevronRight, Filter, AlertTriangle } from 'lucide-react';
import { useRevisionQueue } from '../hooks/useDashboard';

export const RevisionQueue: React.FC = () => {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [sortBy, setSortBy] = useState('forget_probability');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Simple debounce logic for search input
  React.useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1); // reset to page 1 on search
    }, 400);
    return () => clearTimeout(handler);
  }, [search]);

  const queryParams = useMemo(() => ({
    page,
    size: 5,
    sort_by: sortBy,
    sort_order: sortOrder,
    search: debouncedSearch || undefined,
    priority_filter: priorityFilter || undefined,
    status_filter: statusFilter || undefined,
  }), [page, sortBy, sortOrder, debouncedSearch, priorityFilter, statusFilter]);

  const { data, isLoading, isError, refetch } = useRevisionQueue(queryParams);

  const handleSort = (field: string) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
    setPage(1);
  };

  const getPriorityBadgeClass = (priority: 'HIGH' | 'MEDIUM' | 'LOW') => {
    switch (priority) {
      case 'HIGH':
        return 'bg-rose-50 text-rose-700 border-rose-100';
      case 'MEDIUM':
        return 'bg-amber-50 text-amber-700 border-amber-100';
      case 'LOW':
        return 'bg-emerald-50 text-emerald-700 border-emerald-100';
    }
  };

  const getStatusBadgeClass = (status: string) => {
    return status === 'PENDING'
      ? 'bg-amber-50 text-amber-700 border-amber-150'
      : 'bg-emerald-50 text-emerald-700 border-emerald-150';
  };

  const items = data?.items || [];
  const total = data?.total || 0;
  const pages = data?.pages || 0;

  const renderSortIcon = (field: string) => {
    if (sortBy !== field) return null;
    return sortOrder === 'asc' ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />;
  };

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden flex flex-col h-full">
      {/* Header and Filters Section */}
      <div className="p-6 border-b border-gray-100">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-lg font-bold text-gray-950">Revision Queue</h2>
            <p className="text-xs text-gray-500 mt-0.5">
              Prioritized list of topics requiring immediate retrieval practice
            </p>
          </div>
          
          <div className="relative w-full md:w-72">
            <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search student or skill..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-4 py-2 w-full text-sm border border-gray-200 rounded-xl focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none bg-gray-50/50 focus:bg-white transition-all"
            />
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-gray-600 bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-100">
            <Filter className="w-3.5 h-3.5 text-gray-400" />
            <span>Filters</span>
          </div>

          <select
            value={priorityFilter}
            onChange={(e) => { setPriorityFilter(e.target.value); setPage(1); }}
            className="text-xs bg-white border border-gray-200 rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="">All Priorities</option>
            <option value="HIGH">High Priority</option>
            <option value="MEDIUM">Medium Priority</option>
            <option value="LOW">Low Priority</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            className="text-xs bg-white border border-gray-200 rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="">All Statuses</option>
            <option value="PENDING">Pending</option>
            <option value="COMPLETED">Completed</option>
          </select>

          {(priorityFilter || statusFilter || search) && (
            <button
              onClick={() => {
                setPriorityFilter('');
                setStatusFilter('');
                setSearch('');
                setPage(1);
              }}
              className="text-xs text-blue-600 hover:text-blue-700 font-semibold transition-colors"
            >
              Clear all filters
            </button>
          )}
        </div>
      </div>

      {/* Table Section */}
      <div className="flex-1 overflow-x-auto">
        {isLoading ? (
          <div className="p-8 space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-10 bg-gray-100 rounded w-full animate-pulse" />
            ))}
          </div>
        ) : isError ? (
          <div className="p-8 text-center">
            <p className="text-sm text-gray-500 mb-4">Could not load revision queue data</p>
            <button
              onClick={() => refetch()}
              className="px-4 py-2 text-sm font-semibold text-blue-600 border border-blue-200 rounded-xl hover:bg-blue-50 transition-colors"
            >
              Retry
            </button>
          </div>
        ) : items.length === 0 ? (
          <div className="p-12 text-center flex flex-col items-center justify-center">
            <AlertTriangle className="w-10 h-10 text-gray-300 mb-3" />
            <h3 className="text-base font-bold text-gray-900 mb-1">No students requiring revision</h3>
            <p className="text-xs text-gray-500 max-w-xs">
              No matching records found. Verify your filters or search query.
            </p>
          </div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50/50 text-xs font-semibold text-gray-600 uppercase tracking-wider">
                <th
                  onClick={() => handleSort('student_name')}
                  className="px-6 py-4 cursor-pointer hover:bg-gray-100 transition-colors rounded-tl-lg"
                >
                  <div className="flex items-center gap-1">Student {renderSortIcon('student_name')}</div>
                </th>
                <th
                  onClick={() => handleSort('skill_name')}
                  className="px-6 py-4 cursor-pointer hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-1">Skill {renderSortIcon('skill_name')}</div>
                </th>
                <th
                  onClick={() => handleSort('forget_probability')}
                  className="px-6 py-4 cursor-pointer hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-1">Forget Prob {renderSortIcon('forget_probability')}</div>
                </th>
                <th className="px-6 py-4">Priority</th>
                <th className="px-6 py-4">Recommended Date</th>
                <th className="px-6 py-4 rounded-tr-lg">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm">
              {items.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-6 py-4.5 font-semibold text-gray-900">{item.student_name}</td>
                  <td className="px-6 py-4.5 text-gray-600">{item.skill_name}</td>
                  <td className="px-6 py-4.5 font-bold text-gray-800">
                    {Math.round(item.forget_probability * 100)}%
                  </td>
                  <td className="px-6 py-4.5">
                    <span className={`px-2.5 py-1 text-xs font-bold rounded-lg border ${getPriorityBadgeClass(item.revision_priority)}`}>
                      {item.revision_priority}
                    </span>
                  </td>
                  <td className="px-6 py-4.5 text-gray-500">{item.recommended_revision_date || '-'}</td>
                  <td className="px-6 py-4.5">
                    <span className={`px-2.5 py-1 text-xs font-semibold rounded-lg border ${getStatusBadgeClass(item.status)}`}>
                      {item.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination Footer */}
      {!isLoading && !isError && pages > 1 && (
        <div className="px-6 py-4 border-t border-gray-100 flex items-center justify-between bg-gray-50/20">
          <span className="text-xs text-gray-500">
            Showing page <span className="font-semibold text-gray-800">{page}</span> of <span className="font-semibold text-gray-800">{pages}</span> ({total} items)
          </span>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(p - 1, 1))}
              disabled={page === 1}
              className="p-1.5 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="w-4 h-4 text-gray-600" />
            </button>
            
            <button
              onClick={() => setPage((p) => Math.min(p + 1, pages))}
              disabled={page === pages}
              className="p-1.5 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight className="w-4 h-4 text-gray-600" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
