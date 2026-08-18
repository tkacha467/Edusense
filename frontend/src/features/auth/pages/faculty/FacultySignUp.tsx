import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserRole } from '../../../../types';
import { AuthLayout } from '../../components/AuthLayout';
import { RoleHeader } from '../../components/RoleHeader';
import { AuthForm } from '../../components/AuthForm';
import { useAuth } from '../../../../contexts/AuthContext';
import { useToast } from '../../../../contexts/ToastContext';

interface FacultySignUpValues {
  fullName?: string;
  email?: string;
  department?: string;
  institution_id?: string;
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
        role: UserRole.FACULTY,
        department: values.department || '',
        institution_id: values.institution_id || '',
      });
      showToast('Welcome to EduSense! Account created successfully.', 'success');
      navigate('/dashboard');
    } catch (error: unknown) {
      const err = error as { message?: string };
      showToast(err.message || 'Registration failed', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout
      role={UserRole.FACULTY}
      heading="Join the Faculty Network"
      subheading="Get access to powerful tools to monitor student engagement and optimize learning."
    >
      <RoleHeader 
        title="Request Faculty Access" 
        subtitle="Your account will be reviewed by an administrator." 
        role={UserRole.FACULTY}
      />
      <AuthForm
        mode="signup"
        role={UserRole.FACULTY}
        loading={isLoading}
        onSubmit={onSubmit}
      />
    </AuthLayout>
  );
};
