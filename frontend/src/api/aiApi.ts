import apiClient from './apiClient';

export interface ChatRequest {
  query: string;
}

export interface ChatResponse {
  query: string;
  answer: string;
  retrieved_context?: string;
  status: string;
}

export const aiApi = {
  chat: async (data: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>('/ai/chat', data);
    return response.data;
  },
};
