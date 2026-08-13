/**
 * Centralized route path constants.
 * All route definitions in App.tsx and navigation configs reference these constants.
 * When FastAPI routes change, update only this file.
 */

// Public routes
export const ROUTES = {
  LANDING: '/',
  
  // Student auth
  STUDENT_LOGIN: '/student/login',
  STUDENT_SIGNUP: '/student/signup',
  STUDENT_FORGOT_PASSWORD: '/student/forgot-password',
  
  // Faculty auth
  FACULTY_LOGIN: '/faculty/login',
  FACULTY_SIGNUP: '/faculty/signup',
  FACULTY_FORGOT_PASSWORD: '/faculty/forgot-password',

  // Shared auth
  VERIFY_EMAIL: '/verify',
  
  // Student protected
  ONBOARDING: '/onboarding',
  STUDENT_DASHBOARD: '/student/dashboard',
  STUDENT_LEARNING: '/student/learning',
  STUDENT_PLAN: '/student/plan',
  STUDENT_PROFILE: '/student/profile',
  
  // Faculty protected
  FACULTY_DASHBOARD: '/dashboard',
  FACULTY_PROFILE: '/profile',
  
  // Error
  NOT_FOUND: '/404',
} as const;

export type RoutePath = (typeof ROUTES)[keyof typeof ROUTES];
