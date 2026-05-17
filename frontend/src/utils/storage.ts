import type { Conversation } from '../types/chat';

const STORAGE_KEY = 'codebot_conversations';

export const storage = {
  getConversations: (): Conversation[] => {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      if (!data) return [];

      const conversations = JSON.parse(data);
      // Convert date strings back to Date objects
      return conversations.map((conv: Conversation) => ({
        ...conv,
        createdAt: new Date(conv.createdAt),
        updatedAt: new Date(conv.updatedAt),
        messages: conv.messages.map(msg => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        })),
      }));
    } catch (error) {
      console.error('Error loading conversations:', error);
      return [];
    }
  },

  saveConversations: (conversations: Conversation[]): void => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
    } catch (error) {
      console.error('Error saving conversations:', error);
    }
  },

  clearConversations: (): void => {
    localStorage.removeItem(STORAGE_KEY);
  },
};
