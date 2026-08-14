import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Layout
import { AppLayout } from './layouts/AppLayout';
import { StudentLayout } from './layouts/StudentLayout';

// Shared
import { NotFound } from './pages/security/NotFound';

// Features - Auth
import { LandingPage } from './features/auth/pages/LandingPage';
import { StudentLogin } from './features/auth/pages/student/StudentLogin';
import { StudentSignUp } from './features/auth/pages/student/StudentSignUp';
import { StudentForgotPassword } from './features/auth/pages/student/StudentForgotPassword';
import { FacultyLogin } from './features/auth/pages/faculty/FacultyLogin';
import { FacultySignUp } from './features/auth/pages/faculty/FacultySignUp';
import { FacultyForgotPassword } from './features/auth/pages/faculty/FacultyForgotPassword';

// Active Pages
import { Profile } from './features/profile/Profile';

// Student Pages
import { Onboarding } from './features/auth/pages/Onboarding';
import { StudentDashboard } from './features/dashboard/StudentDashboard';
import { LearningHub } from './features/learning/pages/LearningHub';
import { StudyPlan } from './features/study-planner/pages/StudyPlan';
import { AssessmentPage } from './features/assessment/AssessmentPage';
import { KnowledgeDecayPage } from './features/knowledge-decay/KnowledgeDecayPage';
import { AIAssistantPage } from './features/ai-assistant/AIAssistantPage';

// Faculty Pages
import { FacultyDashboard } from './features/dashboard/FacultyDashboard';
import { FacultyAnalytics } from './pages/faculty/FacultyAnalytics';
import { FacultyReports } from './pages/faculty/FacultyReports';
import { StudentSearchPage } from './features/faculty/pages/StudentSearchPage';
import { FacultyPredictionPage } from './features/faculty/pages/FacultyPredictionPage';
import { FacultyAIAssistant } from './features/ai-assistant/FacultyAIAssistant';

// Admin Pages
import { AdminDashboard } from './pages/admin/AdminDashboard';
import { UserRole } from './types';

// Routes
import { ProtectedRoute } from './app/routes/ProtectedRoute';
import { PublicRoute } from './app/routes/PublicRoute';

import { GlobalToast } from './components/ui/GlobalToast';
import { GlobalModal } from './components/ui/GlobalModal';

function App() {
  return (
    <>
      <GlobalToast />
      <GlobalModal />
      <Routes>
        {/* Public Routes (Only accessible if NOT logged in) */}
        <Route element={<PublicRoute />}>
          <Route path="/" element={<LandingPage />} />
          
          {/* Student Auth Routes */}
          <Route path="/student/login" element={<StudentLogin />} />
          <Route path="/student/signup" element={<StudentSignUp />} />
          <Route path="/student/forgot-password" element={<StudentForgotPassword />} />
          
          {/* Faculty Auth Routes */}
          <Route path="/faculty/login" element={<FacultyLogin />} />
          <Route path="/faculty/signup" element={<FacultySignUp />} />
          <Route path="/faculty/forgot-password" element={<FacultyForgotPassword />} />
        </Route>
        
        {/* Student Onboarding */}
        <Route element={<ProtectedRoute allowedRoles={['student']} />}>
          <Route path="/onboarding" element={<Onboarding />} />
        </Route>

        {/* Faculty Protected Routes */}
        <Route element={<ProtectedRoute allowedRoles={[UserRole.FACULTY, UserRole.SUPER_ADMIN]} />}>
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<FacultyDashboard />} />
            <Route path="/faculty/students" element={<StudentSearchPage />} />
            <Route path="/prediction" element={<FacultyPredictionPage />} />
            <Route path="/analytics" element={<FacultyAnalytics />} />
            <Route path="/reports" element={<FacultyReports />} />
            <Route path="/assistant" element={<FacultyAIAssistant />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/settings" element={<div className="p-8 text-center text-gray-500">Settings — Coming in Phase 7</div>} />
          </Route>
        </Route>

        {/* Admin Protected Routes */}
        <Route element={<ProtectedRoute allowedRoles={[UserRole.ADMIN, UserRole.SUPER_ADMIN]} />}>
          <Route element={<AppLayout />}>
            <Route path="/admin/dashboard" element={<AdminDashboard />} />
          </Route>
        </Route>

        {/* Student Protected Routes */}
        <Route element={<ProtectedRoute allowedRoles={['student']} />}>
          <Route element={<StudentLayout />}>
            <Route path="/student/dashboard" element={<StudentDashboard />} />
            <Route path="/student/learning" element={<LearningHub />} />
            <Route path="/student/plan" element={<StudyPlan />} />
            <Route path="/student/profile" element={<Profile />} />
            <Route path="/student/assessment" element={<AssessmentPage />} />
            <Route path="/student/assessment/:sessionId" element={<AssessmentPage />} />
            <Route path="/student/knowledge" element={<KnowledgeDecayPage />} />
            <Route path="/student/assistant" element={<AIAssistantPage />} />
            <Route path="/student/settings" element={<div className="p-8 text-center text-gray-500">Settings — Coming in Phase 7</div>} />
          </Route>
        </Route>
        
        {/* Error Routes */}
        <Route path="/404" element={<NotFound />} />
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Routes>
    </>
  );
}

export default App;
