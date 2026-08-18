/**
 * Faculty Intervention Intelligence API Client
 * Using production apiClient with dynamic edu_session session headers.
 */
import apiClient from '../../../api/apiClient';

export interface CreateInterventionPayload {
  student_id: string;
  skill_id: string;
  intervention_type?: 'REVISION' | 'PRACTICE' | 'TARGETED_ASSESSMENT';
  priority?: 'URGENT' | 'HIGH' | 'MEDIUM' | 'LOW';
  notes?: string;
}

export interface InterventionRecord {
  intervention_id: string;
  faculty_user_id: string;
  student_id: string;
  skill_id: string;
  intervention_type: string;
  priority: string;
  notes: string;
  status: 'PENDING' | 'VIEWED' | 'STARTED' | 'COMPLETED';
  forget_probability_at_intervention: number;
  forget_probability_percentage: number;
  risk_level_at_intervention: string;
  model_version_at_intervention: string;
  recommended_revision_date: string;
  top_risk_factors: string[];
  created_at: string;
  viewed_at?: string;
  started_at?: string;
  completed_at?: string;
  post_intervention_forget_probability?: number;
  observed_risk_reduction?: number;
  outcome_status: string;
}

export interface RiskProfileResponse {
  student_id: string;
  forget_probability: number;
  forget_probability_percentage: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  top_risk_factors: string[];
  protective_factors: string[];
  recommended_revision_date: string;
  model_version: string;
}

/** Fetch student risk profile with ML factor attributions */
export async function fetchStudentRiskProfile(studentId: string): Promise<RiskProfileResponse> {
  const response = await apiClient.get<RiskProfileResponse>(`/faculty/students/${studentId}/risk-profile`);
  return response.data;
}

/** Fetch student intervention history and post-intervention outcomes */
export async function fetchStudentInterventionHistory(studentId: string): Promise<InterventionRecord[]> {
  const response = await apiClient.get<InterventionRecord[]>(`/faculty/students/${studentId}/interventions`);
  return response.data;
}

/** Create a targeted faculty intervention for an at-risk skill */
export async function createIntervention(payload: CreateInterventionPayload): Promise<InterventionRecord> {
  const response = await apiClient.post<InterventionRecord>('/faculty/interventions', payload);
  return response.data;
}

/** List all interventions initiated by the faculty member */
export async function fetchFacultyInterventions(): Promise<InterventionRecord[]> {
  const response = await apiClient.get<InterventionRecord[]>('/faculty/interventions');
  return response.data;
}
