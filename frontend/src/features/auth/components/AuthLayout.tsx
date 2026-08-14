import React from 'react';
import { BrainCircuit, BookOpen, Users } from 'lucide-react';
import type { UserRoleType as Role } from '../../../types';

interface AuthLayoutProps {
  children: React.ReactNode;
  role: Role;
  heading: string;
  subheading: string;
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({ children, role, heading, subheading }) => {
  const isStudent = role === 'student';
  const color = isStudent ? 'emerald' : 'blue';
  
  return (
    <div className="min-h-screen w-full flex bg-white">
      {/* Left Pane - Branding */}
      <div className={`hidden lg:flex flex-1 flex-col justify-between p-12 relative overflow-hidden ${isStudent ? 'bg-emerald-900 text-emerald-50' : 'bg-blue-900 text-blue-50'}`}>
        <div className={`absolute top-0 right-0 w-[800px] h-[800px] rounded-full blur-3xl -z-10 translate-x-1/3 -translate-y-1/3 ${isStudent ? 'bg-emerald-800' : 'bg-blue-800'}`} />
        <div className={`absolute bottom-0 left-0 w-[600px] h-[600px] rounded-full blur-3xl -z-10 -translate-x-1/3 translate-y-1/3 ${isStudent ? 'bg-emerald-700/50' : 'bg-blue-700/50'}`} />

        <div className="flex items-center gap-2">
          <div className="bg-white/20 p-2 rounded-xl backdrop-blur-md border border-white/10">
            <BrainCircuit className="h-8 w-8 text-white" />
          </div>
          <span className="text-2xl font-bold tracking-tight">EduSense {isStudent ? 'Student' : 'Faculty'}</span>
        </div>

        <div className="max-w-lg mb-12">
          <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 border border-white/20 text-sm font-medium mb-6`}>
            {isStudent ? <BookOpen className="w-4 h-4" /> : <Users className="w-4 h-4" />} 
            {isStudent ? 'Learn, Practice, Track' : 'Monitor, Guide, Succeed'}
          </div>
          <h1 className="text-5xl font-bold tracking-tight mb-6 leading-tight">
            {heading}
          </h1>
          <p className="text-lg opacity-90 leading-relaxed">
            {subheading}
          </p>
        </div>

        <p className="text-sm opacity-50">© 2026 EduSense Inc. All rights reserved.</p>
      </div>

      {/* Right Pane - Content */}
      <div className="flex-1 flex flex-col justify-center px-6 lg:px-24">
        <div className="w-full max-w-md mx-auto space-y-8">
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <div className={`p-2 rounded-xl text-white ${isStudent ? 'bg-emerald-600' : 'bg-blue-600'}`}>
              <BrainCircuit className="h-8 w-8" />
            </div>
            <span className="text-2xl font-bold tracking-tight text-gray-900">EduSense {isStudent ? 'Student' : 'Faculty'}</span>
          </div>
          
          {children}
        </div>
      </div>
    </div>
  );
};
