import React, { useCallback, useState, useEffect } from 'react';
import { CogIcon, TrashIcon, ArrowDownIcon, DocumentPlusIcon, FolderOpenIcon } from '@heroicons/react/24/outline';
import { useAutoScroll } from '@/hooks/useAutoScroll';
import { useChatStream } from '@/hooks/useChatStream';
import { useSettings } from '@/contexts/SettingsContext';
import { toast } from 'react-hot-toast';
import clsx from 'clsx';
import { getApiUrl } from '@/utils/api';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import SettingsModal from './SettingsModal';
import KnowledgeModal from './KnowledgeModal';

export interface ChatContainerProps {
  className?: string;
}

const ChatContainer: React.FC<ChatContainerProps> = ({ className }) => {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isKnowledgeOpen, setIsKnowledgeOpen] = useState(false);
  const { 
    openaiKey, 
    langsmithKey, 
    tavilyKey, 
    qdrantKey, 
    qdrantUrl,
    showSettingsOnInit,
    setShowSettingsOnInit,
    hasRequiredKeys
  } = useSettings();

  const { 
    containerRef, 
    scrollToBottom, 
    isAtBottom, 
    enableAutoScroll 
  } = useAutoScroll();

  const [conversationState, setConversationState] = useState<any>({});

  const { state, actions } = useChatStream({
    onError: (error) => {
      toast.error(error.message);
    },
    onComplete: () => {
      scrollToBottom();
    },
    onChunk: () => {
      if (isAtBottom()) {
        scrollToBottom();
      }
    },
  });

  // Show settings modal on initialization when required keys are missing
  useEffect(() => {
    if (showSettingsOnInit && !hasRequiredKeys()) {
      setIsSettingsOpen(true);
    }
  }, [showSettingsOnInit, hasRequiredKeys]);

  const handleSendMessage = useCallback(async (message: string, attachedFile?: File) => {
    if (!hasRequiredKeys()) {
      toast.error('Please configure your API keys in settings first');
      setIsSettingsOpen(true);
      return;
    }

    // Add user message immediately for instant feedback
    const userMessage = {
      id: Date.now().toString(),
      content: message,
      role: 'user' as const,
      timestamp: new Date(),
    };

    actions.addMessage(userMessage);

    // Add loading message immediately
    const loadingMessage = {
      id: (Date.now() + 1).toString(),
      content: '',
      role: 'assistant' as const,
      timestamp: new Date(),
      isLoading: true,
    };

    actions.addMessage(loadingMessage);

    try {
      const response = await fetch(getApiUrl('/analyze/chat'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          state: conversationState,
          openai_key: openaiKey,
          langsmith_key: langsmithKey,
          tavily_key: tavilyKey,
          qdrant_api_key: qdrantKey,
          qdrant_url: qdrantUrl,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Update conversation state
      setConversationState(data.conversation_state || {});
      
      // Replace loading message with actual response
      actions.updateMessage(loadingMessage.id, {
        content: data.response,
        isLoading: false,
        agentUsed: data.agent_used,
        ragSources: data.rag_sources,
      });

    } catch (error) {
      console.error('Error sending message:', error);
      
      // Replace loading message with error message
      actions.updateMessage(loadingMessage.id, {
        content: 'Sorry, I encountered an error. Please try again.',
        isLoading: false,
        isError: true,
      });
      
      toast.error('Failed to send message. Please try again.');
    }
  }, [
    hasRequiredKeys, 
    actions, 
    conversationState, 
    openaiKey, 
    langsmithKey, 
    tavilyKey, 
    qdrantKey, 
    qdrantUrl, 
    conversationState, 
    actions
  ]);

  const handleClearChat = useCallback(() => {
    actions.clearMessages();
    setConversationState({});
    toast.success('Chat cleared');
  }, [actions]);

  const handleCloseSettings = useCallback(() => {
    setIsSettingsOpen(false);
    if (showSettingsOnInit && hasRequiredKeys()) {
      setShowSettingsOnInit(false);
    }
  }, [showSettingsOnInit, hasRequiredKeys, setShowSettingsOnInit]);

  return (
    <div className={clsx('flex flex-col h-full bg-gray-50 dark:bg-gray-900', className)}>
      {/* Header */}
      <div className="flex-shrink-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-4xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">♔</span>
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Chess Assistant
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Multi-Agent RAG System
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setIsKnowledgeOpen(true)}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Manage Knowledge Base"
              >
                <FolderOpenIcon className="w-5 h-5" />
              </button>
              
              <button
                onClick={() => setIsSettingsOpen(true)}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Settings"
              >
                <CogIcon className="w-5 h-5" />
              </button>
              
              <button
                onClick={handleClearChat}
                className="p-2 text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Clear Chat"
              >
                <TrashIcon className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div 
        ref={containerRef}
        className="flex-1 overflow-y-auto"
      >
        <div className="max-w-4xl mx-auto px-4 py-4 space-y-4">
          {state.messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mb-4">
                <span className="text-white font-bold text-2xl">♔</span>
              </div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Welcome to Chess Assistant
              </h2>
              <p className="text-gray-600 dark:text-gray-400 max-w-md">
                I'm your AI chess expert powered by multiple specialized agents and a knowledge base. 
                Ask me about chess theory, analyze games, or get player insights!
              </p>
              <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-md">
                <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                  <h3 className="font-medium text-gray-900 dark:text-white text-sm mb-1">
                    📚 Chess Knowledge
                  </h3>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    Ask about openings, endgames, tactics, and strategy
                  </p>
                </div>
                <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                  <h3 className="font-medium text-gray-900 dark:text-white text-sm mb-1">
                    🎯 Game Analysis
                  </h3>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    Analyze Chess.com players and games
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <>
              {state.messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              
              {!isAtBottom() && (
                <button
                  onClick={scrollToBottom}
                  className="fixed bottom-20 right-6 p-2 bg-blue-500 hover:bg-blue-600 text-white rounded-full shadow-lg transition-colors z-10"
                >
                  <ArrowDownIcon className="w-5 h-5" />
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {/* Input */}
      <div className="flex-shrink-0 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="max-w-4xl mx-auto p-4">
          <ChatInput
            onSendMessage={handleSendMessage}
            disabled={state.isLoading}
            placeholder="Ask me anything about chess..."
          />
        </div>
      </div>

      {/* Modals */}
      <SettingsModal 
        isOpen={isSettingsOpen} 
        onClose={handleCloseSettings} 
      />
      
      <KnowledgeModal 
        isOpen={isKnowledgeOpen} 
        onClose={() => setIsKnowledgeOpen(false)} 
      />
    </div>
  );
};

export default ChatContainer; 