import axios from 'axios';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000, // 30 seconds timeout for queries
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types for API requests and responses
export interface QueryRequest {
  query: string;
  max_results?: number;
  search_engine?: string;
  use_cache?: boolean;
}

export interface SearchResult {
  url: string;
  title?: string;
  content: string;
  relevance_score?: number;
}

export interface QueryResponse {
  query: string;
  answer: string;
  sources: SearchResult[];
  cached: boolean;
  timestamp: string;
  processing_time?: number;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
}

export interface CacheStats {
  total_cached_queries: number;
  faiss_index_size: number;
  cache_enabled: boolean;
}

// API Service Class
export class ApiService {
  // Health check
  static async healthCheck(): Promise<HealthResponse> {
    const response = await api.get<HealthResponse>('/health');
    return response.data;
  }

  // Process query
  static async processQuery(request: QueryRequest): Promise<QueryResponse> {
    const response = await api.post<QueryResponse>('/query', request);
    return response.data;
  }

  // Initialize AI service
  static async initializeAI(): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/initialize');
    return response.data;
  }

  // Get cache stats
  static async getCacheStats(): Promise<CacheStats> {
    const response = await api.get<CacheStats>('/cache/stats');
    return response.data;
  }
}

// Error handling wrapper
export const handleApiError = (error: any): string => {
  if (axios.isAxiosError(error)) {
    if (error.response) {
      // Server responded with error status
      const detail = error.response.data?.detail;
      if (detail && typeof detail === 'object' && detail.error) {
        return detail.error;
      }
      return detail || error.response.data?.message || `Server error: ${error.response.status}`;
    } else if (error.request) {
      // Network error
      return 'Network error - please check if the backend server is running';
    }
  }
  return error.message || 'An unexpected error occurred';
};

export default ApiService;
