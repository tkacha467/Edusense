import React from 'react';
import { DashboardHeader } from './components/DashboardHeader';
import { SummaryCards } from './components/SummaryCards';
import { KnowledgeHealth } from './components/KnowledgeHealth';
import { RevisionQueue } from './components/RevisionQueue';
import { WeakSkills } from './components/WeakSkills';
import { RecentActivities } from './components/RecentActivities';
import { QuickActions } from './components/QuickActions';

export function FacultyDashboard() {
  return (
    <div className="space-y-6">
      {/* 1. Header Greeting & Details */}
      <DashboardHeader />

      {/* 2. Key Summary KPIs */}
      <SummaryCards />

      {/* 3. Graphical Overviews & Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <KnowledgeHealth />
        </div>
        <div>
          <WeakSkills />
        </div>
      </div>

      {/* 4. Actionable Revision Tasks & Activities */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RevisionQueue />
        </div>
        <div>
          <RecentActivities />
        </div>
      </div>

      {/* 5. Shortcuts & Quick Management Tools */}
      <QuickActions />
    </div>
  );
}
