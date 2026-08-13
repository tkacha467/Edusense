import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link } from 'react-router-dom';
import { Loader2, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { UserRole } from '../../../types';
import type { UserRoleType } from '../../../types';
import { Form, FormField } from '../../../components/ui/Form';
import { Button } from '../../../components/ui/Button';
import { RoleHeader } from './RoleHeader';
import { EmailInput } from './EmailInput';

const forgotPasswordSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
});

interface ForgotPasswordFormProps {
  role: UserRoleType;
  email: string;
  loading: boolean;
  isSubmitted: boolean;
  backToLoginLink: string;
  onSubmit: (email: string) => Promise<void>;
  onChange?: (email: string) => void;
  onReturnToLogin: () => void;
}

export const ForgotPasswordForm: React.FC<ForgotPasswordFormProps> = React.memo(({
  role,
  email,
  loading,
  isSubmitted,
  backToLoginLink,
  onSubmit,
  onChange,
  onReturnToLogin,
}) => {
  const isStudent = role === 'student';
  const buttonColorClass = isStudent 
    ? 'bg-emerald-600 hover:bg-emerald-700 focus:ring-emerald-500' 
    : 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500';
  const checkCircleBgClass = isStudent ? 'bg-emerald-100 text-emerald-600' : 'bg-blue-100 text-blue-600';

  const form = useForm<z.infer<typeof forgotPasswordSchema>>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { email: email || '' },
  });

  const { watch } = form;
  const currentEmail = watch('email');

  useEffect(() => {
    if (onChange) {
      onChange(currentEmail);
    }
  }, [currentEmail, onChange]);

  const handleFormSubmit = async (values: z.infer<typeof forgotPasswordSchema>) => {
    await onSubmit(values.email);
  };

  return (
    <div className="space-y-6">
      <Link to={backToLoginLink} className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-900 mb-2">
        <ArrowLeft className="w-4 h-4 mr-2" /> Back to login
      </Link>

      {!isSubmitted ? (
        <>
          <RoleHeader 
            title="Forgot Password?" 
            subtitle={isStudent ? "Enter your email address and we'll send you a link to reset your password." : "Enter your faculty email and we'll send you a password reset link."} 
            role={isStudent ? UserRole.STUDENT : UserRole.FACULTY}
          />

          <Form {...form}>
            <form onSubmit={form.handleSubmit(handleFormSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <EmailInput
                    field={{
                      name: field.name,
                      value: field.value,
                      onChange: field.onChange,
                      onBlur: field.onBlur,
                      ref: field.ref,
                    }}
                    label={isStudent ? "Email Address" : "Faculty Email"}
                    placeholder={isStudent ? "student@school.edu" : "faculty@school.edu"}
                    disabled={loading}
                  />
                )}
              />

              <Button 
                type="submit" 
                className={`w-full h-12 text-base font-semibold text-white ${buttonColorClass}`} 
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Sending Link...
                  </>
                ) : (
                  'Send Reset Link'
                )}
              </Button>
            </form>
          </Form>
        </>
      ) : (
        <div className="text-center py-8">
          <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 ${checkCircleBgClass}`}>
            <CheckCircle2 className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-gray-900 mb-2">Check your inbox</h2>
          <p className="text-gray-500 mb-8">
            We've sent a password reset link to <br/>
            <span className="font-medium text-gray-900">{form.getValues('email')}</span>
          </p>
          <Button onClick={onReturnToLogin} variant="outline" className="w-full h-12 text-base">
            Return to Login
          </Button>
        </div>
      )}
    </div>
  );
});

ForgotPasswordForm.displayName = 'ForgotPasswordForm';
