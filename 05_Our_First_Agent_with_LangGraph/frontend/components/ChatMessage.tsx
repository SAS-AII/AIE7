import React from 'react';
import ReactMarkdown from 'react-markdown';
import clsx from 'clsx';
import { UserIcon, CpuChipIcon } from '@heroicons/react/24/outline';
import { ChatMessage } from '@/utils/api';
import { defaultMarkdownConfig } from '@/utils/markdownPlugins';
import LoadingDots from './LoadingDots';

interface ChatMessageProps {
  message: ChatMessage;
  isStreaming?: boolean;
  className?: string;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ 
  message, 
  isStreaming = false,
  className 
}) => {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';
  const isEmpty = !message.content || message.content.trim() === '';

  return (
    <div 
      className={clsx(
        'flex w-full gap-4 py-4 px-4 message-slide-up',
        isUser ? 'bg-transparent' : 'bg-gray-50 dark:bg-gray-800/50',
        className
      )}
    >
      {/* Avatar */}
      <div className="flex-shrink-0">
        <div 
          className={clsx(
            'w-8 h-8 rounded-full flex items-center justify-center',
            isUser 
              ? 'bg-chess-accent text-white' 
              : 'bg-chess-dark text-white'
          )}
        >
          {isUser ? (
            <UserIcon className="w-5 h-5" />
          ) : (
            <CpuChipIcon className="w-5 h-5" />
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {/* Role indicator */}
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
            {isUser ? 'You' : 'Chess Assistant'}
          </span>
          {message.timestamp && (
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {new Date(message.timestamp).toLocaleTimeString()}
            </span>
          )}
        </div>

        {/* Message content */}
        <div className="prose prose-sm prose-gray dark:prose-invert max-w-none">
          {isEmpty && isStreaming ? (
            <div className="flex items-center gap-2 py-2">
              <LoadingDots size="sm" />
              <span className="text-sm text-gray-500 dark:text-gray-400">
                Thinking...
              </span>
            </div>
          ) : isEmpty ? (
            <div className="text-gray-500 dark:text-gray-400 italic">
              No response
            </div>
          ) : (
            <ReactMarkdown
              {...defaultMarkdownConfig}
              className="markdown"
            >
              {message.content}
            </ReactMarkdown>
          )}
          
          {/* Streaming indicator */}
          {isStreaming && !isEmpty && (
            <div className="inline-flex items-center gap-1 ml-2">
              <div className="w-2 h-2 bg-chess-accent rounded-full animate-pulse" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage; 