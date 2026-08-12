import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthLayout } from '../../components/AuthLayout';
import { RoleHeader } from '../../components/RoleHeader';
import { AuthForm } from '../../components/AuthForm';
import { useAuth } from '../../../../contexts/AuthContext';
import { useToast } from '../../../../contexts/ToastContext';

interface FacultyLoginValues {
  email?: string;
  password?: string;
  rememberMe?: boolean;
}

export const FacultyLogin: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { showToast } = useToast();
  const [isLoading, setIsLoading] = useState(false);

  const onSubmit = async (values: FacultyLoginValues) => {
    setIsLoading(true);
    try {
      await login(
        values.email || '', 
        values.password || '', 
        values.rememberMe ?? false, 
        'teacher'
      );
      showToast('Welcome back to the Faculty Portal!', 'success');
      navigate('/dashboard');
    } catch (error: unknown) {
      const err = error as { message?: string };
      showToast(err.message || 'Failed to login', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout
      role="teacher"
      heading="Monitor Learning. Guide Success."
      subheading="Access advanced analytics, predict knowledge decay, and empower your students to achieve their best."
    >
      <RoleHeader 
        title="Welcome back, Faculty" 
        subtitle="Sign in to access your dashboard and analytics." 
        role="teacher"
      />
      <AuthForm
        mode="login"
        role="teacher"
        loading={isLoading}
        onSubmit={onSubmit}
      />
    </AuthLayout>
  );
};
