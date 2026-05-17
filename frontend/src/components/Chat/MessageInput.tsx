import React, { useState, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';
import { Button } from '../common/Button';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export const MessageInput: React.FC<MessageInputProps> = ({ onSend, disabled }) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-dark-200 p-4 bg-white">
      <div className="flex items-end space-x-2">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about your codebase... (Enter to send, Shift+Enter for newline)"
          disabled={disabled}
          className="flex-1 resize-none border border-dark-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-[60px] max-h-[200px]"
          rows={2}
        />
        <Button
          onClick={handleSend}
          disabled={!message.trim() || disabled}
          className="h-[60px]"
        >
          <Send className="w-5 h-5" />
        </Button>
      </div>
      <p className="text-xs text-dark-500 mt-2">
        Tip: Ask about authentication, search for functions, or request code explanations
      </p>
    </div>
  );
};
