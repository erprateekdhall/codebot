import React from 'react';
import { MessageSquare, Trash2 } from 'lucide-react';
import { Card } from '../common/Card';
import type { Conversation } from '../../types/chat';
import { formatters } from '../../utils/formatters';

interface ConversationListProps {
  conversations: Conversation[];
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  activeConversationId?: string;
}

export const ConversationList: React.FC<ConversationListProps> = ({
  conversations,
  onSelect,
  onDelete,
  activeConversationId,
}) => {
  if (conversations.length === 0) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center text-dark-400">
          <MessageSquare className="w-16 h-16 mx-auto mb-4 text-dark-300" />
          <h3 className="text-xl font-medium text-dark-600 mb-2">
            No Conversations Yet
          </h3>
          <p className="text-sm">
            Start a chat to begin building your conversation history
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {conversations.map((conversation) => {
        const isActive = conversation.id === activeConversationId;
        const lastMessage = conversation.messages[conversation.messages.length - 1];
        const preview = lastMessage
          ? formatters.truncateText(lastMessage.content, 100)
          : 'No messages';

        return (
          <Card
            key={conversation.id}
            className={`p-4 cursor-pointer transition-all ${
              isActive ? 'ring-2 ring-primary-500' : ''
            }`}
            onClick={() => onSelect(conversation.id)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-dark-800 truncate mb-1">
                  {conversation.title}
                </h4>
                <p className="text-sm text-dark-500 line-clamp-2 mb-2">
                  {preview}
                </p>
                <div className="flex items-center space-x-4 text-xs text-dark-400">
                  <span>{conversation.messages.length} messages</span>
                  <span>{formatters.formatDate(conversation.updatedAt)}</span>
                </div>
              </div>

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(conversation.id);
                }}
                className="ml-3 p-2 text-dark-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </Card>
        );
      })}
    </div>
  );
};
