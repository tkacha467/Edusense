import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthLayout } from '../../components/AuthLayout';
import { ForgotPasswordForm } from '../../components/ForgotPasswordForm';

export const StudentForgotPassword: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [emailValue, setEmailValue] = useState('');

  const handleEmailChange = useCallback((value: string) => {
    setEmailValue(value);
  }, []);

  const handleReturnToLogin = useCallback(() => {
    navigate('/student/login');
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
      role="student"
      heading="Reset Your Password"
      subheading="Don't worry, we'll help you get back to your learning journey."
    >
      <ForgotPasswordForm
        role="student"
        email={emailValue}
        loading={isLoading}
        isSubmitted={isSubmitted}
        backToLoginLink="/student/login"
        onSubmit={onSubmit}
        onChange={handleEmailChange}
        onReturnToLogin={handleReturnToLogin}
      />
    </AuthLayout>
  );
};
