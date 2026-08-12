import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthLayout } from '../../components/AuthLayout';
import { RoleHeader } from '../../components/RoleHeader';
import { AuthForm } from '../../components/AuthForm';
import { useAuth } from '../../../../contexts/AuthContext';
import { useToast } from '../../../../contexts/ToastContext';

interface StudentLoginValues {
  email?: string;
  password?: string;
  rememberMe?: boolean;
}

export const StudentLogin: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { showToast } = useToast();
  const [isLoading, setIsLoading] = useState(false);

  const onSubmit = async (values: StudentLoginValues) => {
    setIsLoading(true);
    try {
      await login(
        values.email || '', 
        values.password || '', 
        values.rememberMe ?? false, 
        'student'
      );
      showToast('Welcome back!', 'success');
      navigate('/student/dashboard');
    } catch (error: unknown) {
      const err = error as { message?: string };
      showToast(err.message || 'Failed to login', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout
      role="student"
      heading="Continue Your Learning Journey"
      subheading="Master your subjects, practice consistently, and track your progress all in one place."
    >
      <RoleHeader 
        title="Welcome back, Student" 
        subtitle="Sign in to access your study materials." 
        role="student"
      />
      <AuthForm
        mode="login"
        role="student"
        loading={isLoading}
        onSubmit={onSubmit}
      />
    </AuthLayout>
  );
};
