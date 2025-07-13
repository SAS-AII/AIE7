import React, { useCallback, useState } from 'react';
import { CogIcon, TrashIcon, ArrowDownIcon } from '@heroicons/react/24/outline';
import { useAutoScroll } from '@/hooks/useAutoScroll';
import { useChatStream } from '@/hooks/useChatStream';
import { useSettings } from '@/contexts/SettingsContext';
import { toast } from 'react-hot-toast';
import clsx from 'clsx';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import SettingsModal from './SettingsModal';

interface ChatContainerProps {
  className?: string;
}

const ChatContainer: React.FC<ChatContainerProps> = ({ className }) => {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const { 
    openaiKey, 
    langsmithKey, 
    tavilyKey, 
    qdrantKey, 
    qdrantUrl 
  } = useSettings();

  const { 
    containerRef, 
    scrollToBottom, 
    isAtBottom, 
    enableAutoScroll 
  } = useAutoScroll();

  const { state, actions } = useChatStream({
    onError: (error) => {
      toast.error(error.message);
    },
    onComplete: () => {
      scrollToBottom();
    },
    onChunk: () => {
      // Auto-scroll on each chunk if near bottom
      if (isAtBottom()) {
        scrollToBottom();
      }
    },
  });

  const handlePlayerAnalysis = useCallback((username: string) => {
    actions.analyzePlayerStream({
      username,
      openai_api_key: openaiKey,
      langsmith_api_key: langsmithKey,
      tavily_api_key: tavilyKey,
      qdrant_api_key: qdrantKey,
      qdrant_url: qdrantUrl,
    });
  }, [actions, openaiKey, langsmithKey, tavilyKey, qdrantKey, qdrantUrl]);

  const handlePGNAnalysis = useCallback((pgn: string) => {
    actions.analyzePGNStream({
      pgn_content: pgn,
      openai_api_key: openaiKey,
      langsmith_api_key: langsmithKey,
      tavily_api_key: tavilyKey,
      qdrant_api_key: qdrantKey,
      qdrant_url: qdrantUrl,
    });
  }, [actions, openaiKey, langsmithKey, tavilyKey, qdrantKey, qdrantUrl]);

  const handleRecentGamesAnalysis = useCallback((username: string, limit = 5) => {
    actions.analyzeRecentGamesStream({
      username,
      limit,
      openai_api_key: openaiKey,
      langsmith_api_key: langsmithKey,
      tavily_api_key: tavilyKey,
      qdrant_api_key: qdrantKey,
      qdrant_url: qdrantUrl,
    });
  }, [actions, openaiKey, langsmithKey, tavilyKey, qdrantKey, qdrantUrl]);

  const handleFileUpload = useCallback((file: File) => {
    actions.uploadPNGFile(file, {
      openai_api_key: openaiKey,
      langsmith_api_key: langsmithKey,
      tavily_api_key: tavilyKey,
      qdrant_api_key: qdrantKey,
      qdrant_url: qdrantUrl,
    });
  }, [actions, openaiKey, langsmithKey, tavilyKey, qdrantKey, qdrantUrl]);

  const handleClearChat = useCallback(() => {
    if (confirm('Are you sure you want to clear all messages?')) {
      actions.clearMessages();
      toast.success('Chat cleared');
    }
  }, [actions]);

  const isEmpty = state.messages.length === 0;

  return (
    <div className={clsx('flex flex-col h-screen', className)}>
      {/* Header */}
      <div className="flex-shrink-0 border-b bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm border-gray-200 dark:border-gray-700">
        <div className="max-w-chat mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-chess-accent rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Chess Assistant
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  AI-powered chess analysis and insights
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              {/* Clear chat button */}
              {!isEmpty && (
                <button
                  onClick={handleClearChat}
                  className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                  title="Clear chat"
                >
                  <TrashIcon className="w-5 h-5" />
                </button>
              )}
              
              {/* Settings button */}
              <button
                onClick={() => setIsSettingsOpen(true)}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                title="Settings"
              >
                <CogIcon className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Chat messages */}
      <div 
        ref={containerRef}
        className="flex-1 overflow-y-auto"
      >
        <div className="max-w-chat mx-auto">
          {isEmpty ? (
            <div className="flex items-center justify-center h-full px-4 py-12">
              <div className="text-center">
                <div className="w-16 h-16 bg-chess-accent/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-chess-accent" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Welcome to Chess Assistant
                </h3>
                <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-sm">
                  Get AI-powered analysis of chess players, games, and positions. 
                  Upload PGN files or enter Chess.com usernames to get started.
                </p>
                <div className="flex flex-col gap-2 text-sm text-gray-600 dark:text-gray-400">
                  <div className="flex items-center gap-2">
                    <span>📊</span>
                    <span>Analyze Chess.com players and their stats</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span>♟️</span>
                    <span>Review recent games and find patterns</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span>🎯</span>
                    <span>Get insights from PGN game files</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span>📸</span>
                    <span>Upload PNG images for position analysis</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="py-4">
              {state.messages.map((message, index) => (
                <ChatMessage
                  key={index}
                  message={message}
                  isStreaming={state.isStreaming && index === state.messages.length - 1}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Scroll to bottom button */}
      {!isAtBottom() && (
        <div className="absolute bottom-20 right-4 z-10">
          <button
            onClick={() => enableAutoScroll()}
            className="p-2 bg-chess-accent text-white rounded-full shadow-lg hover:bg-chess-accent/90 transition-colors"
            title="Scroll to bottom"
          >
            <ArrowDownIcon className="w-5 h-5" />
          </button>
        </div>
      )}

      {/* Chat input */}
      <div className="flex-shrink-0">
        <ChatInput
          onPlayerAnalysis={handlePlayerAnalysis}
          onPGNAnalysis={handlePGNAnalysis}
          onRecentGamesAnalysis={handleRecentGamesAnalysis}
          onFileUpload={handleFileUpload}
          onStop={actions.stopStreaming}
          isLoading={state.isLoading}
          isStreaming={state.isStreaming}
        />
      </div>

      {/* Settings modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </div>
  );
};

export default ChatContainer; 