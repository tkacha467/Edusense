import React from 'react';
import { useToast } from '../../contexts/ToastContext';
import type { ToastType } from '../../contexts/ToastContext';
import { CheckCircle2, AlertCircle, Info, AlertTriangle, X, Loader2 } from 'lucide-react';

const icons: Record<ToastType, React.ElementType> = {
  success: CheckCircle2,
  error: AlertCircle,
  info: Info,
  warning: AlertTriangle,
  loading: Loader2
};

const styles: Record<ToastType, string> = {
  success: 'bg-emerald-50 border-emerald-200 text-emerald-800',
  error: 'bg-red-50 border-red-200 text-red-800',
  info: 'bg-blue-50 border-blue-200 text-blue-800',
  warning: 'bg-amber-50 border-amber-200 text-amber-800',
  loading: 'bg-white border-gray-200 text-gray-800'
};

export const GlobalToast: React.FC = () => {
  const { toasts, removeToast } = useToast();

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
      {toasts.map((toast) => {
        const Icon = icons[toast.type];
        return (
          <div
            key={toast.id}
            className={`pointer-events-auto flex items-center justify-between p-4 rounded-xl shadow-lg border w-80 animate-in slide-in-from-right-8 duration-300 ${styles[toast.type]}`}
          >
            <div className="flex items-center gap-3">
              <Icon className={`w-5 h-5 ${toast.type === 'loading' ? 'animate-spin text-primary' : ''}`} />
              <p className="text-sm font-medium">{toast.message}</p>
            </div>
            {toast.type !== 'loading' && (
              <button
                onClick={() => removeToast(toast.id)}
                className="p-1 rounded-md hover:bg-black/5 transition-colors"
              >
                <X className="w-4 h-4 opacity-50 hover:opacity-100" />
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
};

