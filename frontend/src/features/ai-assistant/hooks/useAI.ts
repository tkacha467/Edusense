import { useMutation } from '@tanstack/react-query';
import { aiApi } from '../../../api/aiApi';

export function useAIChat() {
  return useMutation({
    mutationFn: aiApi.chat,
  });
}
