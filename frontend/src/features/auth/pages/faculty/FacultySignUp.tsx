import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthLayout } from '../../components/AuthLayout';
import { RoleHeader } from '../../components/RoleHeader';
import { AuthForm } from '../../components/AuthForm';
import { useAuth } from '../../../../contexts/AuthContext';
import { useToast } from '../../../../contexts/ToastContext';

interface FacultySignUpValues {
  fullName?: string;
  email?: string;
  department?: string;
  password?: string;
}

export const FacultySignUp: React.FC = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { register } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const onSubmit = async (values: FacultySignUpValues) => {
    setIsLoading(true);
    try {
      await register({
        fullName: values.fullName || '',
        email: values.email || '',
        password: values.password || '',
        role: 'teacher',
        department: values.department || '',
      });
      showToast('Account requested. An admin will review your access.', 'success');
      navigate('/faculty/login');
    } catch (error: unknown) {
      const err = error as { message?: string };
      showToast(err.message || 'Registration failed', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout
      role="teacher"
      heading="Join the Faculty Network"
      subheading="Get access to powerful tools to monitor student engagement and optimize learning."
    >
      <RoleHeader 
        title="Request Faculty Access" 
        subtitle="Your account will be reviewed by an administrator." 
        role="teacher"
      />
      <AuthForm
        mode="signup"
        role="teacher"
        loading={isLoading}
        onSubmit={onSubmit}
      />
    </AuthLayout>
  );
};
