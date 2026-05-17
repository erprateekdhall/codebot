import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { Conversation, Message } from '../types/chat';
import { storage } from '../utils/storage';

interface ChatContextType {
  conversations: Conversation[];
  activeConversationId: string | null;
  activeConversation: Conversation | null;
  createConversation: () => void;
  loadConversation: (id: string) => void;
  deleteConversation: (id: string) => void;
  updateMessages: (messages: Message[]) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);

  useEffect(() => {
    // Load conversations from localStorage
    const loaded = storage.getConversations();
    setConversations(loaded);

    // Create a default conversation if none exist
    if (loaded.length === 0) {
      createNewConversation();
    } else {
      setActiveConversationId(loaded[0].id);
    }
  }, []);

  useEffect(() => {
    // Save conversations whenever they change
    if (conversations.length > 0) {
      storage.saveConversations(conversations);
    }
  }, [conversations]);

  const createNewConversation = () => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: `Conversation ${conversations.length + 1}`,
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    setConversations((prev) => [newConversation, ...prev]);
    setActiveConversationId(newConversation.id);
  };

  const loadConversation = (id: string) => {
    setActiveConversationId(id);
  };

  const deleteConversation = (id: string) => {
    setConversations((prev) => prev.filter((c) => c.id !== id));

    if (activeConversationId === id) {
      const remaining = conversations.filter((c) => c.id !== id);
      if (remaining.length > 0) {
        setActiveConversationId(remaining[0].id);
      } else {
        createNewConversation();
      }
    }
  };

  const updateMessages = (messages: Message[]) => {
    setConversations((prev) =>
      prev.map((conv) => {
        if (conv.id === activeConversationId) {
          // Update title based on first user message
          const firstUserMessage = messages.find(m => m.role === 'user');
          const title = firstUserMessage
            ? firstUserMessage.content.substring(0, 50) + (firstUserMessage.content.length > 50 ? '...' : '')
            : conv.title;

          return {
            ...conv,
            messages,
            title,
            updatedAt: new Date(),
          };
        }
        return conv;
      })
    );
  };

  const activeConversation = conversations.find((c) => c.id === activeConversationId) || null;

  return (
    <ChatContext.Provider
      value={{
        conversations,
        activeConversationId,
        activeConversation,
        createConversation: createNewConversation,
        loadConversation,
        deleteConversation,
        updateMessages,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within ChatProvider');
  }
  return context;
};
