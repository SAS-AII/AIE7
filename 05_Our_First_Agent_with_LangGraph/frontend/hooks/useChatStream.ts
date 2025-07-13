import { useState, useCallback, useRef } from 'react';
import { 
  analyzePlayer, 
  analyzePGN, 
  analyzeRecentGames, 
  uploadPNG, 
  readStream,
  ChatMessage,
  PlayerAnalysisRequest,
  PGNAnalysisRequest,
  RecentGamesRequest
} from '@/utils/api';

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
  const currentStreamRef = useRef<ReadableStreamDefaultReader | null>(null);

  const addMessage = useCallback((message: ChatMessage) => {
    setMessages(prev => [...prev, message]);
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
    if (currentStreamRef.current) {
      currentStreamRef.current.cancel();
      currentStreamRef.current = null;
    }
    setIsStreaming(false);
    setIsLoading(false);
  }, []);

  const handleStreamResponse = useCallback(async (
    streamPromise: Promise<ReadableStream<Uint8Array> | string>,
    userMessage: string
  ) => {
    setIsLoading(true);
    setIsStreaming(true);
    setError(null);

    // Add user message
    addMessage({
      role: 'user',
      content: userMessage,
      timestamp: Date.now(),
    });

    // Add initial empty assistant message
    addMessage({
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
    });

    try {
      const response = await streamPromise;
      
      if (typeof response === 'string') {
        // Non-streaming response
        updateLastMessage(response);
        options.onComplete?.();
      } else {
        // Streaming response
        const reader = response.getReader();
        currentStreamRef.current = reader;
        
        await readStream(
          response,
          (chunk) => {
            appendToLastMessage(chunk);
            options.onChunk?.(chunk);
          },
          (error) => {
            setError(error.message);
            options.onError?.(error);
          },
          () => {
            options.onComplete?.();
          }
        );
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setError(errorMessage);
      updateLastMessage(`Error: ${errorMessage}`);
      options.onError?.(error instanceof Error ? error : new Error(errorMessage));
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
      currentStreamRef.current = null;
    }
  }, [addMessage, updateLastMessage, appendToLastMessage, options]);

  const analyzePlayerStream = useCallback(async (request: PlayerAnalysisRequest) => {
    const userMessage = `Analyze player: ${request.username}`;
    await handleStreamResponse(analyzePlayer(request), userMessage);
  }, [handleStreamResponse]);

  const analyzePGNStream = useCallback(async (request: PGNAnalysisRequest) => {
    const userMessage = `Analyze PGN game`;
    await handleStreamResponse(analyzePGN(request), userMessage);
  }, [handleStreamResponse]);

  const analyzeRecentGamesStream = useCallback(async (request: RecentGamesRequest) => {
    const userMessage = `Analyze recent games for ${request.username} (limit: ${request.num_games || 5})`;
    await handleStreamResponse(analyzeRecentGames(request), userMessage);
  }, [handleStreamResponse]);

  const uploadPNGFile = useCallback(async (
    file: File,
    apiKeys: {
      openai_key?: string;
      langsmith_key?: string;
      tavily_key?: string;
      qdrant_api_key?: string;
      qdrant_url?: string;
    }
  ) => {
    setIsLoading(true);
    setError(null);

    // Add user message
    addMessage({
      role: 'user',
      content: `Uploaded PNG file: ${file.name}`,
      timestamp: Date.now(),
    });

    // Add initial empty assistant message
    addMessage({
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
    });

    try {
      const result = await uploadPNG(file, apiKeys);
      updateLastMessage(result);
      options.onComplete?.();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setError(errorMessage);
      updateLastMessage(`Error: ${errorMessage}`);
      options.onError?.(error instanceof Error ? error : new Error(errorMessage));
    } finally {
      setIsLoading(false);
    }
  }, [addMessage, updateLastMessage, options]);

  const state: ChatState = {
    messages,
    isLoading,
    error,
    isStreaming,
  };

  return {
    state,
    actions: {
      analyzePlayerStream,
      analyzePGNStream,
      analyzeRecentGamesStream,
      uploadPNGFile,
      addMessage,
      updateLastMessage,
      clearMessages,
      stopStreaming,
    },
  };
}; 