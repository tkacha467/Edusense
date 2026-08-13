import React, { useEffect, useMemo } from 'react';
import type { UserRoleType } from '../../../types';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link } from 'react-router-dom';
import { Loader2, User, Building } from 'lucide-react';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '../../../components/ui/Form';
import { Input } from '../../../components/ui/Input';
import { Button } from '../../../components/ui/Button';
import { EmailInput } from './EmailInput';
import { PasswordInput } from './PasswordInput';

interface AuthFormProps {
  mode: 'login' | 'signup';
  role: UserRoleType;
  loading: boolean;
  onSubmit: (values: any) => Promise<void>;
  onChange?: (values: any) => void;
  values?: any;
  errors?: any;
}

export const AuthForm: React.FC<AuthFormProps> = React.memo(({
  mode,
  role,
  loading,
  onSubmit,
  onChange,
  values,
}) => {
  const isStudent = role === 'student';
  const isSignup = mode === 'signup';

  const buttonColorClass = isStudent 
    ? 'bg-emerald-600 hover:bg-emerald-700 focus:ring-emerald-500' 
    : 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500';
  const textColorClass = isStudent ? 'text-emerald-600' : 'text-blue-600';
  const checkboxColorClass = isStudent ? 'text-emerald-600 focus:ring-emerald-600' : 'text-blue-600 focus:ring-blue-600';

  // Build the validation schema dynamically
  const schema = useMemo(() => {
    if (!isSignup) {
      return z.object({
        email: z.string().email('Please enter a valid email address'),
        password: z.string().min(8, 'Password must be at least 8 characters'),
        rememberMe: z.boolean().optional(),
      });
    }

    const signupSchema = z.object({
      fullName: z.string().min(2, 'Name must be at least 2 characters'),
      email: z.string().email('Please enter a valid email address'),
      ...(role !== 'student' ? { 
          department: z.string().min(2, 'Department is required'),
          institution_id: z.string().min(2, 'Institution ID is required') 
      } : {}),
      password: z.string().min(8, 'Password must be at least 8 characters'),
      confirmPassword: z.string().min(8, 'Confirm password must be at least 8 characters'),
    }).refine((data) => data.password === data.confirmPassword, {
      message: "Passwords don't match",
      path: ["confirmPassword"],
    });

    return signupSchema;
  }, [isSignup, role]);

  const defaultValues = useMemo(() => {
    if (values) return values;
    if (!isSignup) {
      return { email: '', password: '', rememberMe: false };
    }
    return {
      fullName: '',
      email: '',
      department: '',
      institution_id: '',
      password: '',
      confirmPassword: '',
    };
  }, [values, isSignup]);

  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues,
  });

  const { watch } = form;
  const formValues = watch();

  useEffect(() => {
    if (onChange) {
      onChange(formValues);
    }
  }, [formValues, onChange]);

  const handleFormSubmit = async (data: any) => {
    await onSubmit(data);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleFormSubmit)} className="space-y-5">
        {isSignup && (
          <FormField
            control={form.control}
            name="fullName"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Full Name</FormLabel>
                <FormControl>
                  <div className="relative">
                    <User className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                    <Input
                      className="pl-10 h-12 bg-gray-50 border-gray-200 focus:bg-white text-base"
                      placeholder={isStudent ? "Alex Student" : "Dr. Jane Smith"}
                      disabled={loading}
                      autoComplete="name"
                      aria-label="Full Name"
                      {...field}
                    />
                  </div>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        )}

        {isSignup && role !== 'student' && (
          <>
            <FormField
              control={form.control}
              name="institution_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Institution ID</FormLabel>
                  <FormControl>
                    <div className="relative">
                      <Building className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                      <Input
                        className="pl-10 h-12 bg-gray-50 border-gray-200 focus:bg-white text-base"
                        placeholder="EDU-12345"
                        disabled={loading}
                        aria-label="Institution ID"
                        {...field}
                      />
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="department"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Department</FormLabel>
                  <FormControl>
                    <div className="relative">
                      <Building className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                      <Input
                        className="pl-10 h-12 bg-gray-50 border-gray-200 focus:bg-white text-base"
                        placeholder="Computer Science"
                        disabled={loading}
                        aria-label="Department"
                        {...field}
                      />
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </>
        )}

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

        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <PasswordInput
              field={{
                name: field.name,
                value: field.value,
                onChange: field.onChange,
                onBlur: field.onBlur,
                ref: field.ref,
              }}
              label={isSignup ? "Create Password" : "Password"}
              placeholder="••••••••"
              disabled={loading}
              autoComplete={isSignup ? "new-password" : "current-password"}
            />
          )}
        />

        {isSignup && (
          <FormField
            control={form.control}
            name="confirmPassword"
            render={({ field }) => (
              <PasswordInput
                field={{
                  name: field.name,
                  value: field.value,
                  onChange: field.onChange,
                  onBlur: field.onBlur,
                  ref: field.ref,
                }}
                label="Confirm Password"
                placeholder="••••••••"
                disabled={loading}
                autoComplete="new-password"
              />
            )}
          />
        )}

        {!isSignup && (
          <div className="flex items-center justify-between">
            <FormField
              control={form.control}
              name="rememberMe"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center space-x-2 space-y-0">
                  <FormControl>
                    <input
                      type="checkbox"
                      className={`h-4 w-4 rounded border-gray-300 ${checkboxColorClass}`}
                      checked={field.value}
                      onChange={field.onChange}
                      disabled={loading}
                    />
                  </FormControl>
                  <div className="space-y-1 leading-none">
                    <FormLabel className="text-sm font-normal text-gray-600 cursor-pointer">
                      Remember me
                    </FormLabel>
                  </div>
                </FormItem>
              )}
            />
            <Link 
              to={isStudent ? "/student/forgot-password" : "/faculty/forgot-password"} 
              className={`text-sm font-medium hover:underline ${textColorClass}`}
            >
              Forgot password?
            </Link>
          </div>
        )}

        <Button 
          type="submit" 
          className={`w-full h-12 text-base font-semibold text-white ${buttonColorClass}`} 
          disabled={loading}
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Processing...
            </>
          ) : (
            isSignup 
              ? (role === 'student' ? 'Create Account' : 'Request Access')
              : 'Sign In'
          )}
        </Button>

        <div className="text-center mt-6">
          <p className="text-sm text-gray-600">
            {isSignup ? (
              <>
                Already have an account?{' '}
                <Link 
                  to={isStudent ? "/student/login" : "/faculty/login"} 
                  className={`font-semibold hover:underline ${textColorClass}`}
                >
                  Sign in
                </Link>
              </>
            ) : (
              <>
                {isStudent ? (
                  <>
                    Don't have an account?{' '}
                    <Link 
                      to="/student/signup" 
                      className={`font-semibold hover:underline ${textColorClass}`}
                    >
                      Sign up
                    </Link>
                  </>
                ) : (
                  <>
                    Faculty registration requires admin approval.{' '}
                    <Link 
                      to="/faculty/signup" 
                      className={`font-semibold hover:underline ${textColorClass}`}
                    >
                      Request Access
                    </Link>
                  </>
                )}
              </>
            )}
          </p>
        </div>
      </form>
    </Form>
  );
});

AuthForm.displayName = 'AuthForm';
