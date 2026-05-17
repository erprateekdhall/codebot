import api from './api';
import type { ChatRequest, ChatResponse } from '../types/chat';

export const chatService = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/api/chat', request);
    return response.data;
  },

  // For future implementation of streaming
  sendMessageStream: async (request: ChatRequest): Promise<ReadableStream> => {
    const response = await fetch(`${api.defaults.baseURL}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.body) {
      throw new Error('No response body');
    }

    return response.body;
  },
};
