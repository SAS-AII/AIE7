const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

// Types for API requests and responses
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: number;
}

// Updated interfaces to match backend Pydantic models exactly
export interface PlayerAnalysisRequest {
  username?: string; // Optional - will be requested if missing
  openai_key: string;
  langsmith_key: string;
  tavily_key: string;
  qdrant_api_key?: string;
  qdrant_url?: string;
}

export interface PGNAnalysisRequest {
  pgn: string;
  openai_key: string;
  langsmith_key: string;
  tavily_key: string;
  qdrant_api_key?: string;
  qdrant_url?: string;
}

export interface RecentGamesRequest {
  username?: string; // Optional - will be requested if missing
  num_games: number;
  openai_key: string;
  langsmith_key: string;
  tavily_key: string;
  qdrant_api_key?: string;
  qdrant_url?: string;
}

export interface HealthResponse {
  status: string;
}

export interface ApiError {
  error: string;
  details?: string;
  status_code?: number;
}

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
  const response = await fetch(`${apiUrl}/analyze/player`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
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

// PGN analysis endpoint
export const analyzePGN = async (
  request: PGNAnalysisRequest
): Promise<ReadableStream<Uint8Array> | string> => {
  const response = await fetch(`${apiUrl}/analyze/pgn`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
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
  const response = await fetch(`${apiUrl}/analyze/recent-games`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
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
    openai_key?: string;
    langsmith_key?: string;
    tavily_key?: string;
    qdrant_api_key?: string;
    qdrant_url?: string;
  }
): Promise<string> => {
  const formData = new FormData();
  formData.append('file', file);

  // Add API keys to form data
  if (apiKeys.openai_key) {
    formData.append('openai_key', apiKeys.openai_key);
  }
  if (apiKeys.langsmith_key) {
    formData.append('langsmith_key', apiKeys.langsmith_key);
  }
  if (apiKeys.tavily_key) {
    formData.append('tavily_key', apiKeys.tavily_key);
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
      if (done) break;
      
      const chunk = decoder.decode(value, { stream: true });
      onChunk(chunk);
    }
    onComplete?.();
  } catch (error) {
    onError?.(error instanceof Error ? error : new Error('Stream error'));
  } finally {
    reader.releaseLock();
  }
};

export { apiUrl }; 