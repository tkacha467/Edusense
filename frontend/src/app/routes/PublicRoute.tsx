import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

export const PublicRoute: React.FC = () => {
  const { isAuthenticated, role, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  // If logged in, redirect away from public routes (like login/register)
  if (isAuthenticated) {
    return <Navigate to={role === 'student' ? '/student/dashboard' : '/dashboard'} replace />;
  }

  return <Outlet />;
};


