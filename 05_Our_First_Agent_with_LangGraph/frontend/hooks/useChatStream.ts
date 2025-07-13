import { useState, useCallback, useRef } from 'react';
import { ChatMessage } from '@/components/ChatMessage';

interface UseChatStreamOptions {
  onError?: (error: Error) => void;
  onComplete?: () => void;
  onChunk?: (chunk: string) => void;
}

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  isStreaming: boolean;
}

export const useChatStream = (options: UseChatStreamOptions = {}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);

  const addMessage = useCallback((message: ChatMessage) => {
    setMessages(prev => [...prev, message]);
  }, []);

  const updateMessage = useCallback((messageId: string, updates: Partial<ChatMessage>) => {
    setMessages(prev => 
      prev.map(msg => 
        msg.id === messageId 
          ? { ...msg, ...updates }
          : msg
      )
    );
  }, []);

  const removeMessage = useCallback((messageId: string) => {
    setMessages(prev => prev.filter(msg => msg.id !== messageId));
  }, []);

  const updateLastMessage = useCallback((content: string) => {
    setMessages(prev => {
      const newMessages = [...prev];
      const lastMessage = newMessages[newMessages.length - 1];
      
      if (lastMessage && lastMessage.role === 'assistant') {
        lastMessage.content = content;
      }
      
      return newMessages;
    });
  }, []);

  const appendToLastMessage = useCallback((chunk: string) => {
    setMessages(prev => {
      const newMessages = [...prev];
      const lastMessage = newMessages[newMessages.length - 1];
      
      if (lastMessage && lastMessage.role === 'assistant') {
        lastMessage.content += chunk;
      }
      
      return newMessages;
    });
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const stopStreaming = useCallback(() => {
    setIsStreaming(false);
    setIsLoading(false);
  }, []);

  const state: ChatState = {
    messages,
    isLoading,
    error,
    isStreaming,
  };

  return {
    state,
    actions: {
      addMessage,
      updateMessage,
      removeMessage,
      updateLastMessage,
      appendToLastMessage,
      clearMessages,
      stopStreaming,
    },
  };
}; 