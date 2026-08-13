/**
 * Faculty Dashboard API Layer
 * Connecting to FastAPI backend /dashboard endpoints.
 */
import apiClient from '../../../api/apiClient';

export interface ProfileSummary {
  full_name: string;
  email: string;
  institution: string;
  department: string;
  designation: string;
  role: string;
}

export interface DashboardSummary {
  total_students: number;
  total_skills: number;
  high_risk_students: number;
  pending_revisions: number;
  predictions_generated: number;
  active_courses: number;
}

export interface KnowledgeHealthPoint {
  date_label: string;
  avg_retention: number;
  avg_forget_prob: number;
  predictions_count: number;
}

export interface KnowledgeHealthData {
  points: KnowledgeHealthPoint[];
}

export interface RevisionQueueItem {
  id: string;
  student_id: string;
  student_name: string;
  skill_id: string;
  skill_name: string;
  forget_probability: number;
  revision_priority: 'HIGH' | 'MEDIUM' | 'LOW';
  recommended_revision_date?: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';
}

export interface RevisionQueueResponse {
  items: RevisionQueueItem[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface WeakSkillItem {
  skill_id: string;
  skill_name: string;
  avg_mastery: number;
  avg_forget_probability: number;
  students_affected: number;
}

export interface RecentActivityItem {
  id: string;
  student_name: string;
  activity_type: string;
  description: string;
  timestamp: string;
}

export interface RevisionQueueQueryParams {
  page?: number;
  size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  search?: string;
  priority_filter?: string;
  status_filter?: string;
}

export const fetchProfileSummary = async (): Promise<ProfileSummary> => {
  const response = await apiClient.get('/dashboard/profile-summary');
  return response.data;
};

export const fetchDashboardSummary = async (): Promise<DashboardSummary> => {
  const response = await apiClient.get('/dashboard/summary');
  return response.data;
};

export const fetchKnowledgeHealth = async (): Promise<KnowledgeHealthData> => {
  const response = await apiClient.get('/dashboard/knowledge-health');
  return response.data;
};

export const fetchRevisionQueue = async (params: RevisionQueueQueryParams = {}): Promise<RevisionQueueResponse> => {
  const response = await apiClient.get('/dashboard/revision-queue', { params });
  return response.data;
};

export const fetchWeakSkills = async (limit: number = 5): Promise<WeakSkillItem[]> => {
  const response = await apiClient.get('/dashboard/weak-skills', { params: { limit } });
  return response.data;
};

export const fetchRecentActivities = async (limit: number = 10): Promise<RecentActivityItem[]> => {
  const response = await apiClient.get('/dashboard/recent-activities', { params: { limit } });
  return response.data;
};
