import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json',
  },
});

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

export interface CacheStats {
  total_cached_queries: number;
  faiss_index_size: number;
  cache_enabled: boolean;
}

export class ApiService {
  static async processQuery(request: QueryRequest): Promise<QueryResponse> {
    const response = await api.post<QueryResponse>('/query', request);
    return response.data;
  }

  static async getCacheStats(): Promise<CacheStats> {
    const response = await api.get<CacheStats>('/cache/stats');
    return response.data;
  }
}
export const handleApiError = (error: any): string => {
  if (axios.isAxiosError(error)) {
    if (error.response) {
      const detail = error.response.data?.detail;
      if (detail && typeof detail === 'object' && detail.error) {
        return detail.error;
      }
      return detail || error.response.data?.message || `Server error: ${error.response.status}`;
    } else if (error.request) {
      if (error.code === 'ECONNABORTED') {
        return 'Query is taking longer than expected. This usually happens for new queries that require web scraping. Please try again - cached results will be much faster.';
      }
      return 'Network error - please check if the backend server is running';
    }
  }
  return error.message || 'An unexpected error occurred';
};

export default ApiService;
