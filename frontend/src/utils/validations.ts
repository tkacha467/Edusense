import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  rememberMe: z.boolean().optional(),
});

export const profileSchema = z.object({
  firstName: z.string().min(2, 'First name must be at least 2 characters').max(50),
  lastName: z.string().min(2, 'Last name must be at least 2 characters').max(50),
  email: z.string().email('Invalid email address'),
  role: z.enum(['Admin', 'Teacher', 'Student', 'Analyst']),
  bio: z.string().max(500, 'Bio must be less than 500 characters').optional(),
});

export const passwordSchema = z.object({
  currentPassword: z.string().min(1, 'Current password is required'),
  newPassword: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Must contain at least one number')
    .regex(/[^A-Za-z0-9]/, 'Must contain at least one special character'),
  confirmPassword: z.string()
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

export const settingsSchema = z.object({
  theme: z.enum(['light', 'dark', 'system']),
  emailNotifications: z.boolean(),
  pushNotifications: z.boolean(),
  weeklyReports: z.boolean(),
  language: z.string(),
  timezone: z.string(),
});

export const studentReportSchema = z.object({
  studentId: z.string().min(1, 'Please select a student'),
  dateRange: z.object({
    from: z.date({ required_error: 'Start date is required' }),
    to: z.date({ required_error: 'End date is required' }),
  }),
  includeDecayMetrics: z.boolean(),
  includeRecommendations: z.boolean(),
});

export const studentSignupSchema = z.object({
  fullName: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

export const otpSchema = z.object({
  pin: z.string().length(6, { message: 'Your one-time password must be exactly 6 characters' }),
});

export const studentOnboardingSchema = z.object({
  grade: z.string().optional(),
  schoolType: z.string().min(1, 'Please select your education type'),
  degreeLevel: z.string().optional(),
  stream: z.string().optional(),
  selectedSubjectId: z.string().optional(),
  selectedTopicId: z.string().optional(),
  skillsToTrack: z.array(z.string()).optional(),
});
