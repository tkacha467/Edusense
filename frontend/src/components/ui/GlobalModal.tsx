import React from 'react';
import { useModal } from '../../contexts/ModalContext';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from './Modal';
import { Button } from './Button';
import { AlertTriangle, CheckCircle2, Info, AlertCircle, Loader2 } from 'lucide-react';

export const GlobalModal: React.FC = () => {
  const { isOpen, config, closeModal, isLoading, setIsLoading } = useModal();

  if (!config) return null;

  const handleConfirm = async () => {
    if (config.onConfirm) {
      setIsLoading(true);
      try {
        await config.onConfirm();
        closeModal();
      } catch (error) {
        setIsLoading(false);
        // Error handling would ideally be shown in the modal or via a toast
      }
    } else {
      closeModal();
    }
  };

  const getIcon = () => {
    switch (config.type) {
      case 'danger': return <AlertTriangle className="w-12 h-12 text-red-500 mb-4" />;
      case 'warning': return <AlertCircle className="w-12 h-12 text-amber-500 mb-4" />;
      case 'success': return <CheckCircle2 className="w-12 h-12 text-emerald-500 mb-4" />;
      case 'info': return <Info className="w-12 h-12 text-blue-500 mb-4" />;
      default: return null;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && closeModal()}>
      <DialogContent className={config.type !== 'custom' ? 'sm:max-w-[425px] text-center' : ''}>
        {config.type !== 'custom' ? (
          <>
            <div className="flex flex-col items-center">
              {getIcon()}
              <DialogHeader>
                <DialogTitle className="text-xl text-center">{config.title}</DialogTitle>
                {config.message && (
                  <DialogDescription className="text-center mt-2 text-base">
                    {config.message}
                  </DialogDescription>
                )}
              </DialogHeader>
            </div>
            
            <DialogFooter className="mt-6 flex gap-2 sm:justify-center">
              <Button
                variant="outline"
                onClick={() => {
                  if (config.onCancel) config.onCancel();
                  closeModal();
                }}
                disabled={isLoading}
                className="w-full sm:w-auto"
              >
                {config.cancelText || 'Cancel'}
              </Button>
              <Button
                variant={config.type === 'danger' ? 'destructive' : 'default'}
                onClick={handleConfirm}
                disabled={isLoading}
                className="w-full sm:w-auto"
              >
                {isLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                {config.confirmText || 'Confirm'}
              </Button>
            </DialogFooter>
          </>
        ) : (
          config.customComponent
        )}
      </DialogContent>
    </Dialog>
  );
};
