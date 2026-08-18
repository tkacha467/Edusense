/**
 * Production Model Monitoring API Client Layer for EduSense AI
 * Using production apiClient with dynamic edu_session authentication.
 */
import apiClient from '../../../api/apiClient';

export interface FeatureDriftItem {
  feature_name: string;
  psi_score: number;
  status: 'LOW' | 'WARNING' | 'CRITICAL';
  sample_count: number;
}

export interface FeatureDriftData {
  status: 'HEALTHY' | 'WARNING' | 'CRITICAL' | 'INSUFFICIENT_DATA';
  sample_size: number;
  required_samples?: number;
  feature_drift_results: FeatureDriftItem[];
}

export interface PredictionDistributionData {
  status: string;
  prediction_count: number;
  mean_forget_probability?: number;
  median_forget_probability?: number;
  distribution?: {
    HIGH_percentage: number;
    MEDIUM_percentage: number;
    LOW_percentage: number;
  };
}

export interface ModelPerformanceData {
  status: 'HEALTHY' | 'WARNING' | 'CRITICAL' | 'INSUFFICIENT_DATA';
  available_labeled_samples: number;
  required_labeled_samples?: number;
  message?: string;
  PR_AUC?: number;
  ROC_AUC?: number;
  Brier_Score?: number;
  Recall?: number;
  F1?: number;
}

export interface ModelCalibrationData {
  model_version: string;
  calibration_method: string;
  status: string;
  brier_score?: number;
  expected_calibration_error?: number;
}

export interface DataSufficiencyData {
  prediction_count: number;
  drift_required: number;
  drift_sufficient: boolean;
  performance_required: number;
  performance_sufficient: boolean;
  available_labeled_samples: number;
}

export interface ModelHealthData {
  model_version: string;
  champion_algorithm: string;
  calibration_method: string;
  overall_status: 'HEALTHY' | 'WARNING' | 'CRITICAL' | 'INSUFFICIENT_DATA';
  timestamp: string;
  prediction_count: number;
  feature_drift_status: string;
  prediction_drift_status: string;
  performance_monitoring_status: string;
}

export interface ModelMonitoringOverview {
  model_health: ModelHealthData;
  model_version: string;
  champion_model: string;
  calibration_method: string;
  prediction_count: number;
  last_observation_timestamp?: string;
  data_sufficiency: DataSufficiencyData;
  drift: FeatureDriftData;
  prediction_distribution: PredictionDistributionData;
  performance: ModelPerformanceData;
  calibration: ModelCalibrationData;
}

/** Single-request aggregate endpoint fetching full monitoring dashboard overview */
export async function fetchModelMonitoringOverview(): Promise<ModelMonitoringOverview> {
  const response = await apiClient.get<ModelMonitoringOverview>('/model-monitoring/overview');
  return response.data;
}
