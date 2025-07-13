const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

// Types for API requests and responses
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: number;
}

export interface ChatRequest {
  message: string;
  openai_api_key?: string;
  langsmith_api_key?: string;
  tavily_api_key?: string;
  qdrant_api_key?: string;
  qdrant_url?: string;
}

export interface ChatResponse {
  response: string;
  error?: string;
}

export interface HealthResponse {
  status: string;
  timestamp?: string;
}

export interface PGNAnalysisRequest {
  pgn_content: string;
  openai_api_key?: string;
  langsmith_api_key?: string;
  tavily_api_key?: string;
  qdrant_api_key?: string;
  qdrant_url?: string;
}

export interface PlayerAnalysisRequest {
  username: string;
  openai_api_key?: string;
  langsmith_api_key?: string;
  tavily_api_key?: string;
  qdrant_api_key?: string;
  qdrant_url?: string;
}

export interface RecentGamesRequest {
  username: string;
  limit?: number;
  openai_api_key?: string;
  langsmith_api_key?: string;
  tavily_api_key?: string;
  qdrant_api_key?: string;
  qdrant_url?: string;
}

export interface ApiError {
  error: string;
  details?: string;
  status_code?: number;
}

// Utility function to create headers with API keys
const createHeaders = (apiKeys: {
  openai_api_key?: string;
  langsmith_api_key?: string;
  tavily_api_key?: string;
  qdrant_api_key?: string;
  qdrant_url?: string;
}): HeadersInit => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  // Add API keys as headers if provided
  if (apiKeys.openai_api_key) {
    headers['X-OpenAI-API-Key'] = apiKeys.openai_api_key;
  }
  if (apiKeys.langsmith_api_key) {
    headers['X-LangSmith-API-Key'] = apiKeys.langsmith_api_key;
  }
  if (apiKeys.tavily_api_key) {
    headers['X-Tavily-API-Key'] = apiKeys.tavily_api_key;
  }
  if (apiKeys.qdrant_api_key) {
    headers['X-Qdrant-API-Key'] = apiKeys.qdrant_api_key;
  }
  if (apiKeys.qdrant_url) {
    headers['X-Qdrant-URL'] = apiKeys.qdrant_url;
  }

  return headers;
};

// Generic fetch wrapper with error handling
const fetchWithErrorHandling = async <T>(
  url: string,
  options: RequestInit
): Promise<T> => {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.error || 
        errorData.detail || 
        `HTTP ${response.status}: ${response.statusText}`
      );
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('An unknown error occurred');
  }
};

// Health check endpoint
export const checkHealth = async (): Promise<HealthResponse> => {
  return fetchWithErrorHandling<HealthResponse>(`${apiUrl}/health`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });
};

// Player analysis endpoint
export const analyzePlayer = async (
  request: PlayerAnalysisRequest
): Promise<ReadableStream<Uint8Array> | string> => {
  const headers = createHeaders(request);
  
  const response = await fetch(`${apiUrl}/analyze/player`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      username: request.username,
      ...(request.openai_api_key && { openai_api_key: request.openai_api_key }),
      ...(request.langsmith_api_key && { langsmith_api_key: request.langsmith_api_key }),
      ...(request.tavily_api_key && { tavily_api_key: request.tavily_api_key }),
      ...(request.qdrant_api_key && { qdrant_api_key: request.qdrant_api_key }),
      ...(request.qdrant_url && { qdrant_url: request.qdrant_url }),
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.error || 
      errorData.detail || 
      `HTTP ${response.status}: ${response.statusText}`
    );
  }

  // Return the readable stream for streaming responses
  return response.body || '';
};

// PGN analysis endpoint
export const analyzePGN = async (
  request: PGNAnalysisRequest
): Promise<ReadableStream<Uint8Array> | string> => {
  const headers = createHeaders(request);
  
  const response = await fetch(`${apiUrl}/analyze/pgn`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      pgn_content: request.pgn_content,
      ...(request.openai_api_key && { openai_api_key: request.openai_api_key }),
      ...(request.langsmith_api_key && { langsmith_api_key: request.langsmith_api_key }),
      ...(request.tavily_api_key && { tavily_api_key: request.tavily_api_key }),
      ...(request.qdrant_api_key && { qdrant_api_key: request.qdrant_api_key }),
      ...(request.qdrant_url && { qdrant_url: request.qdrant_url }),
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.error || 
      errorData.detail || 
      `HTTP ${response.status}: ${response.statusText}`
    );
  }

  return response.body || '';
};

// Recent games analysis endpoint
export const analyzeRecentGames = async (
  request: RecentGamesRequest
): Promise<ReadableStream<Uint8Array> | string> => {
  const headers = createHeaders(request);
  
  const response = await fetch(`${apiUrl}/analyze/recent-games`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      username: request.username,
      limit: request.limit || 5,
      ...(request.openai_api_key && { openai_api_key: request.openai_api_key }),
      ...(request.langsmith_api_key && { langsmith_api_key: request.langsmith_api_key }),
      ...(request.tavily_api_key && { tavily_api_key: request.tavily_api_key }),
      ...(request.qdrant_api_key && { qdrant_api_key: request.qdrant_api_key }),
      ...(request.qdrant_url && { qdrant_url: request.qdrant_url }),
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.error || 
      errorData.detail || 
      `HTTP ${response.status}: ${response.statusText}`
    );
  }

  return response.body || '';
};

// Upload PNG file endpoint
export const uploadPNG = async (
  file: File,
  apiKeys: {
    openai_api_key?: string;
    langsmith_api_key?: string;
    tavily_api_key?: string;
    qdrant_api_key?: string;
    qdrant_url?: string;
  }
): Promise<string> => {
  const formData = new FormData();
  formData.append('file', file);

  // Add API keys to form data
  if (apiKeys.openai_api_key) {
    formData.append('openai_api_key', apiKeys.openai_api_key);
  }
  if (apiKeys.langsmith_api_key) {
    formData.append('langsmith_api_key', apiKeys.langsmith_api_key);
  }
  if (apiKeys.tavily_api_key) {
    formData.append('tavily_api_key', apiKeys.tavily_api_key);
  }
  if (apiKeys.qdrant_api_key) {
    formData.append('qdrant_api_key', apiKeys.qdrant_api_key);
  }
  if (apiKeys.qdrant_url) {
    formData.append('qdrant_url', apiKeys.qdrant_url);
  }

  const response = await fetch(`${apiUrl}/upload/png`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.error || 
      errorData.detail || 
      `HTTP ${response.status}: ${response.statusText}`
    );
  }

  const result = await response.json();
  return result.analysis || 'Analysis completed successfully';
};

// Stream reader utility for handling streaming responses
export const readStream = async (
  stream: ReadableStream<Uint8Array>,
  onChunk: (chunk: string) => void,
  onError?: (error: Error) => void,
  onComplete?: () => void
): Promise<void> => {
  const reader = stream.getReader();
  const decoder = new TextDecoder();

  try {
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        onComplete?.();
        break;
      }

      const chunk = decoder.decode(value, { stream: true });
      onChunk(chunk);
    }
  } catch (error) {
    onError?.(error instanceof Error ? error : new Error('Stream reading failed'));
  } finally {
    reader.releaseLock();
  }
};

export { apiUrl }; 