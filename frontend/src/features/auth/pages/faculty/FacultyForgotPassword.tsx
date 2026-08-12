import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthLayout } from '../../components/AuthLayout';
import { ForgotPasswordForm } from '../../components/ForgotPasswordForm';

export const FacultyForgotPassword: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [emailValue, setEmailValue] = useState('');

  const handleEmailChange = useCallback((value: string) => {
    setEmailValue(value);
  }, []);

  const handleReturnToLogin = useCallback(() => {
    navigate('/faculty/login');
  }, [navigate]);

  const onSubmit = async (email: string) => {
    setIsLoading(true);
    // Simulate API delay
    setTimeout(() => {
      setIsLoading(false);
      setIsSubmitted(true);
    }, 1500);
  };

  return (
    <AuthLayout
      role="teacher"
      heading="Reset Faculty Password"
      subheading="Regain access to your dashboard and continue guiding your students."
    >
      <ForgotPasswordForm
        role="teacher"
        email={emailValue}
        loading={isLoading}
        isSubmitted={isSubmitted}
        backToLoginLink="/faculty/login"
        onSubmit={onSubmit}
        onChange={handleEmailChange}
        onReturnToLogin={handleReturnToLogin}
      />
    </AuthLayout>
  );
};
