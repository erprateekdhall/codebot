import React, { useState } from 'react';
import { PlusCircle } from 'lucide-react';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { Button } from '../common/Button';
import { chatService } from '../../services/chatService';
import type { Message } from '../../types/chat';

interface ChatWindowProps {
  conversationId: string;
  messages: Message[];
  onNewConversation: () => void;
  onMessagesUpdate: (messages: Message[]) => void;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  conversationId,
  messages,
  onNewConversation,
  onMessagesUpdate,
}) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    const updatedMessages = [...messages, userMessage];
    onMessagesUpdate(updatedMessages);

    setIsLoading(true);

    try {
      const response = await chatService.sendMessage({
        message: content,
        conversation_id: conversationId,
      });

      // Add assistant message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        sources: response.sources,
        gitInfo: response.git_info,
      };

      onMessagesUpdate([...updatedMessages, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);

      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date(),
      };

      onMessagesUpdate([...updatedMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-dark-200 bg-white">
        <h2 className="text-lg font-semibold text-dark-800">
          Code Assistant
        </h2>
        <Button
          variant="outline"
          size="sm"
          onClick={onNewConversation}
        >
          <PlusCircle className="w-4 h-4 mr-2" />
          New Chat
        </Button>
      </div>

      {/* Messages */}
      <MessageList messages={messages} isLoading={isLoading} />

      {/* Input */}
      <MessageInput onSend={handleSendMessage} disabled={isLoading} />
    </div>
  );
};
