import React from 'react';
import ReactMarkdown from 'react-markdown';
import clsx from 'clsx';
import { 
  UserIcon, 
  CpuChipIcon, 
  DocumentTextIcon, 
  GlobeAltIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline';
import LoadingDots from './LoadingDots';

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  isLoading?: boolean;
  isError?: boolean;
  agentUsed?: string;
  ragSources?: number;
}

interface ChatMessageProps {
  message: ChatMessage;
  className?: string;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ 
  message, 
  className 
}) => {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  const getAgentIcon = (agentUsed?: string) => {
    switch (agentUsed) {
      case 'rag_agent':
        return <DocumentTextIcon className="w-4 h-4" />;
      case 'chess_agent':
        return <GlobeAltIcon className="w-4 h-4" />;
      default:
        return <CpuChipIcon className="w-4 h-4" />;
    }
  };

  const getAgentName = (agentUsed?: string) => {
    switch (agentUsed) {
      case 'rag_agent':
        return 'Knowledge Agent';
      case 'chess_agent':
        return 'Chess.com Agent';
      case 'final_response':
        return 'General Agent';
      default:
        return 'Chess Assistant';
    }
  };

  return (
    <div 
      className={clsx(
        'group relative',
        className
      )}
    >
      <div className={clsx(
        'flex gap-4 p-4 rounded-lg',
        isUser 
          ? 'bg-blue-50 dark:bg-blue-900/20 ml-8' 
          : 'bg-white dark:bg-gray-800 mr-8'
      )}>
        {/* Avatar */}
        <div className="flex-shrink-0">
          <div 
            className={clsx(
              'w-8 h-8 rounded-full flex items-center justify-center',
              isUser 
                ? 'bg-blue-500 text-white' 
                : message.isError
                ? 'bg-red-500 text-white'
                : 'bg-gradient-to-br from-purple-500 to-blue-600 text-white'
            )}
          >
            {isUser ? (
              <UserIcon className="w-5 h-5" />
            ) : message.isError ? (
              <ExclamationTriangleIcon className="w-5 h-5" />
            ) : (
              <CpuChipIcon className="w-5 h-5" />
            )}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Header for assistant messages */}
          {isAssistant && (
            <div className="flex items-center gap-2 mb-2">
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {getAgentName(message.agentUsed)}
              </span>
              
              {message.agentUsed && (
                <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
                  {getAgentIcon(message.agentUsed)}
                  <span>{message.agentUsed.replace('_', ' ')}</span>
                </div>
              )}
              
              {message.ragSources && message.ragSources > 0 && (
                <div className="flex items-center gap-1 text-xs text-green-600 dark:text-green-400">
                  <DocumentTextIcon className="w-4 h-4" />
                  <span>{message.ragSources} sources</span>
                </div>
              )}
            </div>
          )}

          {/* Message content */}
          <div className="prose prose-sm max-w-none dark:prose-invert">
            {message.isLoading ? (
              <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
                <LoadingDots />
                <span className="text-sm">Thinking...</span>
              </div>
            ) : message.content ? (
              <ReactMarkdown
                components={{
                  // Customize link styling
                  a: ({ node, ...props }) => (
                    <a 
                      {...props} 
                      className="text-blue-600 dark:text-blue-400 hover:underline"
                      target="_blank"
                      rel="noopener noreferrer"
                    />
                  ),
                  // Customize code styling
                  code: ({ node, inline, ...props }) => (
                    <code 
                      {...props}
                      className={clsx(
                        inline 
                          ? 'bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded text-sm'
                          : 'block bg-gray-100 dark:bg-gray-700 p-3 rounded-lg text-sm overflow-x-auto'
                      )}
                    />
                  ),
                  // Customize list styling
                  ul: ({ node, ...props }) => (
                    <ul {...props} className="list-disc list-inside space-y-1" />
                  ),
                  ol: ({ node, ...props }) => (
                    <ol {...props} className="list-decimal list-inside space-y-1" />
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            ) : (
              <div className="text-gray-400 dark:text-gray-500 italic">
                No content
              </div>
            )}
          </div>

          {/* Timestamp */}
          <div className="mt-2 text-xs text-gray-400 dark:text-gray-500">
            {message.timestamp.toLocaleTimeString()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage; 