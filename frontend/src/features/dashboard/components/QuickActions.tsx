import React from 'react';
import { useNavigate } from 'react-router-dom';
import { UserPlus, Upload, Database, FileSpreadsheet, Sparkles, BookOpen } from 'lucide-react';

interface ActionItem {
  title: string;
  description: string;
  icon: React.ElementType;
  colorClass: string;
  bgClass: string;
  route: string;
}

export const QuickActions: React.FC = () => {
  const navigate = useNavigate();

  const actions: ActionItem[] = [
    {
      title: 'Add Student',
      description: 'Manually register a student profile',
      icon: UserPlus,
      colorClass: 'text-blue-600',
      bgClass: 'bg-blue-50',
      route: '/student/signup',
    },
    {
      title: 'Import Roster',
      description: 'Upload spreadsheet of student rosters',
      icon: FileSpreadsheet,
      colorClass: 'text-emerald-600',
      bgClass: 'bg-emerald-50',
      route: '/prediction', // Placeholder page
    },
    {
      title: 'Upload Dataset',
      description: 'Import new course log data to train AI',
      icon: Upload,
      colorClass: 'text-amber-600',
      bgClass: 'bg-amber-50',
      route: '/prediction', // Placeholder page
    },
    {
      title: 'Trigger Predictions',
      description: 'Run half-life models for decay predictions',
      icon: Sparkles,
      colorClass: 'text-purple-600',
      bgClass: 'bg-purple-50',
      route: '/prediction', // Placeholder page
    },
    {
      title: 'Generate Reports',
      description: 'Export cohort retention analytics',
      icon: Database,
      colorClass: 'text-indigo-600',
      bgClass: 'bg-indigo-50',
      route: '/reports',
    },
    {
      title: 'Manage Courses',
      description: 'Add or configure subject curriculum',
      icon: BookOpen,
      colorClass: 'text-rose-600',
      bgClass: 'bg-rose-50',
      route: '/analytics',
    },
  ];

  return (
    <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
      <div className="mb-5">
        <h2 className="text-lg font-bold text-gray-950">Quick Admin Actions</h2>
        <p className="text-xs text-gray-500 mt-0.5">
          Execute platform management task shortcuts
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {actions.map((action) => {
          const Icon = action.icon;
          return (
            <button
              key={action.title}
              onClick={() => navigate(action.route)}
              className="flex flex-col items-center text-center p-4 rounded-xl border border-gray-100 hover:border-blue-200 hover:bg-blue-50/10 hover:shadow-sm transition-all duration-200 group focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            >
              <div className={`p-3 rounded-xl mb-3 ${action.bgClass} group-hover:scale-105 transition-transform duration-200`}>
                <Icon className={`w-5 h-5 ${action.colorClass}`} />
              </div>
              <h3 className="text-xs font-bold text-gray-900 mb-0.5 group-hover:text-blue-700 transition-colors">
                {action.title}
              </h3>
              <p className="text-[10px] text-gray-400 font-medium leading-normal">
                {action.description}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
};
