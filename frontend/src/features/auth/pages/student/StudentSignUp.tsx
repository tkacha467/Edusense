import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthLayout } from '../../components/AuthLayout';
import { RoleHeader } from '../../components/RoleHeader';
import { AuthForm } from '../../components/AuthForm';
import { useAuth } from '../../../../contexts/AuthContext';
import { useToast } from '../../../../contexts/ToastContext';

interface StudentSignUpValues {
  fullName?: string;
  email?: string;
  password?: string;
}

export const StudentSignUp: React.FC = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { register } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const onSubmit = async (values: StudentSignUpValues) => {
    setIsLoading(true);
    try {
      await register({
        fullName: values.fullName || '',
        email: values.email || '',
        password: values.password || '',
        role: 'student',
      });
      showToast('Welcome to EduSense! Account created successfully.', 'success');
      navigate('/student/dashboard');
    } catch (error: unknown) {
      const err = error as { message?: string };
      showToast(err.message || 'Registration failed', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout
      role="student"
      heading="Start Your Journey"
      subheading="Join thousands of students mastering their subjects with EduSense."
    >
      <RoleHeader 
        title="Create Student Account" 
        subtitle="Track your progress and beat the forgetting curve." 
        role="student"
      />
      <AuthForm
        mode="signup"
        role="student"
        loading={isLoading}
        onSubmit={onSubmit}
      />
    </AuthLayout>
  );
};
