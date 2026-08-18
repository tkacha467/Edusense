import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  ShieldAlert, 
  CheckCircle2, 
  AlertTriangle, 
  RefreshCw, 
  Database, 
  Layers, 
  TrendingUp, 
  Cpu, 
  Info,
  Clock,
  Sparkles,
  BarChart2,
  Lock
} from 'lucide-react';
import { fetchModelMonitoringOverview } from '../api/modelMonitoringApi';
import type { ModelMonitoringOverview } from '../api/modelMonitoringApi';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';

export function ModelMonitoringPage() {
  const [data, setData] = useState<ModelMonitoringOverview | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const overview = await fetchModelMonitoringOverview();
      setData(overview);
    } catch (err: any) {
      console.error("[ModelMonitoringPage] Error fetching monitoring data:", err);
      const msg = err?.response?.data?.detail || err?.message || "Unable to load model monitoring analytics.";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (isLoading) {
    return (
      <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6 animate-pulse">
        <div className="h-10 bg-slate-800/60 rounded-xl w-1/3" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="h-40 bg-slate-800/60 rounded-2xl" />
          <div className="h-40 bg-slate-800/60 rounded-2xl" />
          <div className="h-40 bg-slate-800/60 rounded-2xl" />
        </div>
        <div className="h-64 bg-slate-800/60 rounded-2xl" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 max-w-md mx-auto text-center space-y-4">
        <div className="bg-rose-500/10 p-4 rounded-full w-16 h-16 flex items-center justify-center mx-auto border border-rose-500/20">
          <AlertTriangle className="w-8 h-8 text-rose-500" />
        </div>
        <h3 className="text-xl font-bold text-white">Monitoring Telemetry Error</h3>
        <p className="text-sm text-slate-400">{error}</p>
        <Button onClick={loadData} variant="outline" className="mt-2">
          <RefreshCw className="w-4 h-4 mr-2" />
          Retry Connection
        </Button>
      </div>
    );
  }

  if (!data) return null;

  const { model_health, data_sufficiency, drift, prediction_distribution, performance, calibration } = data;
  const overallStatus = model_health.overall_status;

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white">Model Observability & Drift</h1>
            <span className={`px-3 py-1 rounded-full text-xs font-bold border flex items-center space-x-1.5 ${
              overallStatus === 'HEALTHY' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' :
              overallStatus === 'WARNING' ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' :
              overallStatus === 'CRITICAL' ? 'bg-rose-500/10 text-rose-400 border-rose-500/30' :
              'bg-slate-800 text-slate-400 border-slate-700'
            }`}>
              <Activity className="w-3.5 h-3.5" />
              <span>{overallStatus}</span>
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Real-time inference telemetry, Population Stability Index (PSI) feature drift, and calibration metrics for deployed champion model.
          </p>
        </div>
        <Button onClick={loadData} variant="outline" size="sm" className="border-slate-700 hover:bg-slate-800 text-slate-300">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh Metrics
        </Button>
      </div>

      {/* Overview Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Model Health Card */}
        <Card className="bg-slate-900 border-slate-800 shadow-xl">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center space-x-2">
              <Cpu className="w-4 h-4 text-indigo-400" />
              <span>Model Architecture</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <div className="text-xl font-bold text-white">{data.champion_model}</div>
              <div className="text-xs text-indigo-400 font-mono mt-0.5">Version: {data.model_version}</div>
            </div>
            <div className="pt-2 border-t border-slate-800 text-xs text-slate-400 space-y-1">
              <div>Calibration: <strong className="text-slate-200">{data.calibration_method}</strong></div>
              <div>Last Observation: <strong className="text-slate-200">{data.last_observation_timestamp ? new Date(data.last_observation_timestamp).toLocaleTimeString() : 'None Recorded'}</strong></div>
            </div>
          </CardContent>
        </Card>

        {/* Data Sufficiency Card */}
        <Card className="bg-slate-900 border-slate-800 shadow-xl">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center space-x-2">
              <Database className="w-4 h-4 text-amber-400" />
              <span>Data Sufficiency</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <div className="text-3xl font-extrabold text-white">{data_sufficiency.prediction_count}</div>
              <div className="text-xs text-slate-400 mt-0.5">Total Inference Observations</div>
            </div>
            <div className="pt-2 border-t border-slate-800 text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-slate-400">Drift Threshold (N ≥ 30):</span>
                <span className={`font-bold ${data_sufficiency.drift_sufficient ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {data_sufficiency.drift_sufficient ? 'Sufficient' : `${data_sufficiency.prediction_count}/30`}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Outcome Evaluation (N ≥ 50):</span>
                <span className={`font-bold ${data_sufficiency.performance_sufficient ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {data_sufficiency.performance_sufficient ? 'Sufficient' : `${data_sufficiency.available_labeled_samples}/50`}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Prediction Distribution Summary */}
        <Card className="bg-slate-900 border-slate-800 shadow-xl">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center space-x-2">
              <BarChart2 className="w-4 h-4 text-emerald-400" />
              <span>Inference Distribution</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {prediction_distribution.status === 'INSUFFICIENT_DATA' ? (
              <div className="text-xs text-slate-400 py-3">
                <span className="bg-slate-800 px-2 py-1 rounded text-amber-400 font-semibold">INSUFFICIENT_DATA</span>
                <p className="mt-2">Collecting inference telemetry observations...</p>
              </div>
            ) : (
              <>
                <div className="flex justify-between items-baseline">
                  <div>
                    <span className="text-xs text-slate-400">Mean P(forget):</span>
                    <div className="text-xl font-bold text-emerald-400">
                      {((prediction_distribution.mean_forget_probability || 0) * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <span className="text-xs text-slate-400">Median P(forget):</span>
                    <div className="text-xl font-bold text-indigo-400">
                      {((prediction_distribution.median_forget_probability || 0) * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
                <div className="pt-2 border-t border-slate-800 text-xs flex justify-between text-slate-400">
                  <span>HIGH: <strong className="text-rose-400">{prediction_distribution.distribution?.HIGH_percentage}%</strong></span>
                  <span>MED: <strong className="text-amber-400">{prediction_distribution.distribution?.MEDIUM_percentage}%</strong></span>
                  <span>LOW: <strong className="text-emerald-400">{prediction_distribution.distribution?.LOW_percentage}%</strong></span>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Feature Data Drift Panel (PSI) */}
      <Card className="bg-slate-900 border-slate-800 shadow-xl">
        <CardHeader>
          <CardTitle className="text-base font-bold text-white flex items-center space-x-2">
            <Layers className="w-5 h-5 text-indigo-400" />
            <span>Population Stability Index (PSI) Feature Drift</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {drift.status === 'INSUFFICIENT_DATA' ? (
            <div className="p-6 bg-slate-950/60 border border-slate-800 rounded-xl text-center space-y-2">
              <Info className="w-6 h-6 text-amber-400 mx-auto" />
              <div className="text-sm font-semibold text-white">Feature Drift Status: INSUFFICIENT_DATA</div>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Statistical PSI drift evaluation requires at least {drift.required_samples || 30} production inference observations (Current: {drift.sample_size}).
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {drift.feature_drift_results.map((item) => (
                <div key={item.feature_name} className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-semibold text-white font-mono">{item.feature_name}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      item.status === 'LOW' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      item.status === 'WARNING' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                      'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                    }`}>
                      {item.status}
                    </span>
                  </div>
                  <div className="flex justify-between items-baseline pt-1">
                    <span className="text-xs text-slate-400">PSI Score:</span>
                    <span className="text-sm font-bold text-white">{item.psi_score.toFixed(4)}</span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full ${
                        item.status === 'LOW' ? 'bg-emerald-500' :
                        item.status === 'WARNING' ? 'bg-amber-500' : 'bg-rose-500'
                      }`}
                      style={{ width: `${Math.min(100, item.psi_score * 300)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Model Performance & Discrimination Panel */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Performance Discrimination */}
        <Card className="bg-slate-900 border-slate-800 shadow-xl">
          <CardHeader>
            <CardTitle className="text-base font-bold text-white flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-emerald-400" />
              <span>Model Performance & Discrimination</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {performance.status === 'INSUFFICIENT_DATA' ? (
              <div className="p-6 bg-slate-950/60 border border-slate-800 rounded-xl text-center space-y-2">
                <Info className="w-6 h-6 text-amber-400 mx-auto" />
                <div className="text-sm font-semibold text-white">Performance Metrics: INSUFFICIENT_DATA</div>
                <p className="text-xs text-slate-400">
                  Labeled outcome evaluation requires at least {performance.required_labeled_samples || 50} completed post-revision assessments (Current: {performance.available_labeled_samples}).
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl">
                  <span className="text-xs text-slate-400">PR-AUC</span>
                  <div className="text-xl font-bold text-emerald-400 mt-1">{performance.PR_AUC?.toFixed(4)}</div>
                </div>
                <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl">
                  <span className="text-xs text-slate-400">ROC-AUC</span>
                  <div className="text-xl font-bold text-indigo-400 mt-1">{performance.ROC_AUC?.toFixed(4)}</div>
                </div>
                <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl">
                  <span className="text-xs text-slate-400">Recall</span>
                  <div className="text-xl font-bold text-white mt-1">{performance.Recall?.toFixed(4)}</div>
                </div>
                <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl">
                  <span className="text-xs text-slate-400">Brier Score</span>
                  <div className="text-xl font-bold text-amber-400 mt-1">{performance.Brier_Score?.toFixed(4)}</div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Probability Calibration */}
        <Card className="bg-slate-900 border-slate-800 shadow-xl">
          <CardHeader>
            <CardTitle className="text-base font-bold text-white flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-amber-400" />
              <span>Probability Calibration</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">Calibration Strategy:</span>
                <span className="font-semibold text-white">{calibration.calibration_method}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Brier Score (MSE):</span>
                <span className="font-mono font-bold text-amber-400">{calibration.brier_score !== undefined ? calibration.brier_score.toFixed(4) : 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Expected Calibration Error (ECE):</span>
                <span className="font-mono font-bold text-emerald-400">
                  {calibration.expected_calibration_error !== undefined && calibration.expected_calibration_error !== null ? calibration.expected_calibration_error.toFixed(4) : 'INSUFFICIENT_DATA'}
                </span>
              </div>
            </div>

            {/* Retraining Policy Safeguard Notice */}
            <div className="p-3 bg-indigo-500/10 border border-indigo-500/30 rounded-xl flex items-start space-x-2 text-xs text-indigo-300">
              <Lock className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
              <div>
                <strong className="text-white block mb-0.5">Retraining Safety Invariant</strong>
                Automatic model retraining is intentionally disabled. Detected drift triggers research audit warnings for human review before candidate model updates.
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default ModelMonitoringPage;
