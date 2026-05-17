import React from 'react';
import { ConversationList } from './ConversationList';
import type { Conversation } from '../../types/chat';

interface HistoryPanelProps {
  conversations: Conversation[];
  activeConversationId?: string;
  onSelectConversation: (id: string) => void;
  onDeleteConversation: (id: string) => void;
}

export const HistoryPanel: React.FC<HistoryPanelProps> = ({
  conversations,
  activeConversationId,
  onSelectConversation,
  onDeleteConversation,
}) => {
  // Sort conversations by most recent
  const sortedConversations = [...conversations].sort(
    (a, b) => b.updatedAt.getTime() - a.updatedAt.getTime()
  );

  return (
    <div className="h-full flex flex-col p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-dark-800 mb-2">
          Conversation History
        </h2>
        <p className="text-sm text-dark-500">
          {conversations.length} conversation{conversations.length !== 1 ? 's' : ''} saved
        </p>
      </div>

      <div className="flex-1 overflow-auto">
        <ConversationList
          conversations={sortedConversations}
          activeConversationId={activeConversationId}
          onSelect={onSelectConversation}
          onDelete={onDeleteConversation}
        />
      </div>
    </div>
  );
};
