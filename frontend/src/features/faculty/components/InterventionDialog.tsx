import React, { useState, useEffect } from 'react';
import { X, Send, AlertTriangle, CheckCircle2, ShieldAlert, Sparkles, Loader2 } from 'lucide-react';
import { createIntervention } from '../api/facultyApi';
import type { InterventionRecord } from '../api/facultyApi';

interface InterventionDialogProps {
  isOpen: boolean;
  onClose: () => void;
  studentId: string;
  studentName: string;
  skillId: string;
  skillName: string;
  currentRisk: 'LOW' | 'MEDIUM' | 'HIGH';
  forgetProbability: number;
  onSuccess?: (record: InterventionRecord) => void;
}

export function InterventionDialog({
  isOpen,
  onClose,
  studentId,
  studentName,
  skillId,
  skillName,
  currentRisk,
  forgetProbability,
  onSuccess
}: InterventionDialogProps) {
  const [interventionType, setInterventionType] = useState<'REVISION' | 'PRACTICE' | 'TARGETED_ASSESSMENT'>('REVISION');
  const [priority, setPriority] = useState<'URGENT' | 'HIGH' | 'MEDIUM' | 'LOW'>(currentRisk === 'HIGH' ? 'URGENT' : 'HIGH');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen && !isSubmitting) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, isSubmitting, onClose]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isSubmitting) return;

    setIsSubmitting(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      const record = await createIntervention({
        student_id: studentId,
        skill_id: skillId,
        intervention_type: interventionType,
        priority: priority,
        notes: notes || `Faculty targeted ${interventionType.toLowerCase()} intervention for ${skillName}.`
      });

      setSuccessMsg(`Intervention successfully sent to ${studentName}'s revision queue!`);
      if (onSuccess) onSuccess(record);
      setTimeout(() => {
        setIsSubmitting(false);
        setSuccessMsg(null);
        onClose();
      }, 1200);
    } catch (err: any) {
      console.error("[InterventionDialog] Error sending intervention:", err);
      const msg = err?.response?.data?.detail || err?.message || "Failed to create intervention. Please try again.";
      setErrorMsg(msg);
      setIsSubmitting(false);
    }
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200"
      role="dialog"
      aria-modal="true"
      aria-labelledby="intervention-dialog-title"
    >
      <div className="bg-slate-900 border border-slate-800 w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-5 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 id="intervention-dialog-title" className="text-lg font-bold text-white">Targeted Learning Intervention</h3>
              <p className="text-xs text-slate-400">Send personalized intervention to student revision queue</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            disabled={isSubmitting}
            className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-800 transition-colors disabled:opacity-50"
            aria-label="Close dialog"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* Student & Skill Info Card */}
          <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4 space-y-2">
            <div className="flex justify-between items-center text-xs text-slate-400">
              <span>Student: <strong className="text-slate-200">{studentName}</strong></span>
              <span className={`px-2 py-0.5 rounded-full font-bold text-[10px] ${
                currentRisk === 'HIGH' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30' :
                currentRisk === 'MEDIUM' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' :
                'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
              }`}>
                {currentRisk} RISK
              </span>
            </div>
            <div className="text-sm font-semibold text-white">
              Skill: {skillName}
            </div>
            <div className="flex items-center space-x-2 text-xs text-slate-400">
              <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
              <span>Model Forgetting Risk: <strong className="text-amber-300">{(forgetProbability * 100).toFixed(1)}%</strong></span>
            </div>
          </div>

          {/* Messages */}
          {errorMsg && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-xs text-rose-300 flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{errorMsg}</span>
            </div>
          )}

          {successMsg && (
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-xs text-emerald-300 flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
              <span>{successMsg}</span>
            </div>
          )}

          {/* Intervention Type Selection */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">Intervention Type</label>
            <div className="grid grid-cols-3 gap-2">
              {(['REVISION', 'PRACTICE', 'TARGETED_ASSESSMENT'] as const).map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setInterventionType(type)}
                  className={`px-3 py-2 text-xs font-medium rounded-xl border transition-all text-center ${
                    interventionType === type 
                      ? 'bg-indigo-600/30 border-indigo-500 text-white shadow-sm' 
                      : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:bg-slate-800'
                  }`}
                >
                  {type === 'TARGETED_ASSESSMENT' ? 'ASSESSMENT' : type}
                </button>
              ))}
            </div>
          </div>

          {/* Priority Selection */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">Intervention Priority</label>
            <div className="grid grid-cols-4 gap-2">
              {(['URGENT', 'HIGH', 'MEDIUM', 'LOW'] as const).map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => setPriority(p)}
                  className={`px-2 py-1.5 text-xs font-semibold rounded-lg border transition-all text-center ${
                    priority === p 
                      ? 'bg-indigo-600/30 border-indigo-500 text-white shadow-sm' 
                      : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:bg-slate-800'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          {/* Faculty Notes */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Pedagogical Notes (Optional)</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add specific instructions for the student's revision task..."
              rows={3}
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white bg-slate-800/60 hover:bg-slate-800 rounded-xl transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 rounded-xl transition-colors shadow-lg shadow-indigo-600/20 flex items-center space-x-2 disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                  <span>Sending...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4 text-white" />
                  <span>Send Intervention</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
