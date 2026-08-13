/**
 * Navigation configuration for sidebar and layout components.
 * Extracted from hardcoded arrays inside Sidebar.tsx and StudentLayout.tsx.
 */
import {
  LayoutDashboard,
  BrainCircuit,
  BookOpen,
  Target,
  User,
  Settings,
  type LucideIcon,
} from 'lucide-react';
import { ROUTES } from './routes';

export interface NavItem {
  label: string;
  path: string;
  icon: LucideIcon;
}

export const STUDENT_NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', path: ROUTES.STUDENT_DASHBOARD, icon: LayoutDashboard },
  { label: 'Learning Hub', path: ROUTES.STUDENT_LEARNING, icon: BookOpen },
  { label: 'Study Plan', path: ROUTES.STUDENT_PLAN, icon: BookOpen },
];

export const FACULTY_NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', path: ROUTES.FACULTY_DASHBOARD, icon: LayoutDashboard },
];

export const FACULTY_SECONDARY_NAV: NavItem[] = [
  { label: 'Profile', path: ROUTES.FACULTY_PROFILE, icon: User },
];
