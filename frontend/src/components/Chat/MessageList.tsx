import React, { useEffect, useRef } from 'react';
import { User, Bot, FileCode } from 'lucide-react';
import type { Message } from '../../types/chat';
import { CodeBlock } from './CodeBlock';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { formatters } from '../../utils/formatters';

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const renderMessageContent = (message: Message) => {
    const parts = message.content.split(/(```[\s\S]*?```)/g);

    return parts.map((part, index) => {
      if (part.startsWith('```')) {
        const code = part.replace(/```/g, '').trim();
        return <CodeBlock key={index} code={code} />;
      }
      return (
        <p key={index} className="whitespace-pre-wrap">
          {part}
        </p>
      );
    });
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {messages.length === 0 && !isLoading && (
        <div className="h-full flex items-center justify-center">
          <div className="text-center text-dark-400">
            <Bot className="w-16 h-16 mx-auto mb-4 text-dark-300" />
            <h3 className="text-xl font-medium text-dark-600 mb-2">
              Start a conversation
            </h3>
            <p className="text-sm">
              Ask me anything about your codebase!
            </p>
          </div>
        </div>
      )}

      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${
            message.role === 'user' ? 'justify-end' : 'justify-start'
          }`}
        >
          <div
            className={`flex max-w-3xl ${
              message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
            }`}
          >
            {/* Avatar */}
            <div
              className={`flex-shrink-0 ${
                message.role === 'user' ? 'ml-3' : 'mr-3'
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  message.role === 'user'
                    ? 'bg-primary-600'
                    : 'bg-dark-700'
                }`}
              >
                {message.role === 'user' ? (
                  <User className="w-5 h-5 text-white" />
                ) : (
                  <Bot className="w-5 h-5 text-white" />
                )}
              </div>
            </div>

            {/* Message Content */}
            <div className="flex-1">
              <div
                className={`rounded-lg p-4 ${
                  message.role === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-white border border-dark-200'
                }`}
              >
                <div className="prose max-w-none">
                  {renderMessageContent(message)}
                </div>

                {/* Sources */}
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-dark-200">
                    <p className="text-sm font-medium text-dark-600 mb-2 flex items-center">
                      <FileCode className="w-4 h-4 mr-1" />
                      Sources ({message.sources.length})
                    </p>
                    <div className="space-y-2">
                      {message.sources.map((source, idx) => (
                        <div
                          key={idx}
                          className="text-sm bg-dark-50 rounded p-2"
                        >
                          <p className="font-mono text-xs text-dark-600">
                            {source.file}:{source.start_line}-{source.end_line}
                          </p>
                          {source.relevance_score !== undefined && (
                            <p className="text-xs text-dark-500 mt-1">
                              Relevance: {formatters.formatRelevanceScore(source.relevance_score)}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Timestamp */}
              <p className="text-xs text-dark-500 mt-1 px-1">
                {formatters.formatTimestamp(message.timestamp)}
              </p>
            </div>
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="flex justify-start">
          <div className="flex max-w-3xl">
            <div className="flex-shrink-0 mr-3">
              <div className="w-8 h-8 rounded-full bg-dark-700 flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
            </div>
            <div className="bg-white border border-dark-200 rounded-lg p-4">
              <LoadingSpinner size="sm" />
              <p className="text-sm text-dark-500 ml-2 inline-block">
                Analyzing...
              </p>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};
