import React, { useState, useEffect } from 'react';
import { Search, Send, Clock, ExternalLink, Server, Database } from 'lucide-react';
import ApiService, { handleApiError } from './services/api';
import type { QueryResponse, CacheStats } from './services/api';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [maxResults, setMaxResults] = useState(5);
  const [searchEngine, setSearchEngine] = useState('bing');
  const [useCache, setUseCache] = useState(true);
  const [cacheStats, setCacheStats] = useState<CacheStats | null>(null);
  const [backendStatus, setBackendStatus] = useState<'unknown' | 'healthy' | 'error'>('unknown');

  // Check backend health on component mount
  useEffect(() => {
    checkBackendHealth();
    loadCacheStats();
  }, []);

  const checkBackendHealth = async () => {
    try {
      await ApiService.healthCheck();
      setBackendStatus('healthy');
    } catch (error) {
      setBackendStatus('error');
      console.error('Backend health check failed:', error);
    }
  };

  const loadCacheStats = async () => {
    try {
      const stats = await ApiService.getCacheStats();
      setCacheStats(stats);
    } catch (error) {
      console.error('Failed to load cache stats:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const result = await ApiService.processQuery({
        query: query.trim(),
        max_results: maxResults,
        search_engine: searchEngine,
        use_cache: useCache,
      });
      setResponse(result);
      // Refresh cache stats after successful query
      loadCacheStats();
    } catch (error) {
      setError(handleApiError(error));
    } finally {
      setLoading(false);
    }
  };

  const initializeAI = async () => {
    try {
      setLoading(true);
      await ApiService.initializeAI();
      checkBackendHealth();
    } catch (error) {
      setError(handleApiError(error));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>
            <Search className="header-icon" />
            Ripplica Web Query
          </h1>
          <div className="status-indicators">
            <div className={`status-indicator ${backendStatus}`}>
              <Server size={16} />
              <span>Backend: {backendStatus}</span>
            </div>
            {cacheStats && (
              <div className="status-indicator healthy">
                <Database size={16} />
                <span>Cache: {cacheStats.total_cached_queries} queries</span>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="main-content">
        <div className="query-section">
          <form onSubmit={handleSubmit} className="query-form">
            <div className="input-group">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask me anything about the web..."
                className="query-input"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="submit-button"
              >
                {loading ? <Clock className="spinning" /> : <Send />}
              </button>
            </div>

            <div className="options">
              <div className="option-group">
                <label>Max Results:</label>
                <select
                  value={maxResults}
                  onChange={(e) => setMaxResults(Number(e.target.value))}
                  disabled={loading}
                >
                  <option value={3}>3</option>
                  <option value={5}>5</option>
                  <option value={10}>10</option>
                  <option value={15}>15</option>
                </select>
              </div>

              <div className="option-group">
                <label>Search Engine:</label>
                <select
                  value={searchEngine}
                  onChange={(e) => setSearchEngine(e.target.value)}
                  disabled={loading}
                >
                  <option value="bing">Bing</option>
                  <option value="google">Google</option>
                  <option value="duckduckgo">DuckDuckGo</option>
                </select>
              </div>

              <div className="option-group">
                <label>
                  <input
                    type="checkbox"
                    checked={useCache}
                    onChange={(e) => setUseCache(e.target.checked)}
                    disabled={loading}
                  />
                  Use Cache
                </label>
              </div>
            </div>
          </form>

          {backendStatus === 'error' && (
            <div className="error-section">
              <p>Backend server is not responding. Would you like to initialize it?</p>
              <button onClick={initializeAI} disabled={loading} className="init-button">
                Initialize AI Service
              </button>
            </div>
          )}
        </div>

        {error && (
          <div className="error-message">
            <h3>Error</h3>
            <p>{error}</p>
          </div>
        )}

        {response && (
          <div className="response-section">
            <div className="response-header">
              <h2>Response</h2>
              <div className="response-meta">
                {response.cached && (
                  <span className="cache-indicator">📋 Cached</span>
                )}
                {response.processing_time && (
                  <span className="time-indicator">
                    ⏱️ {response.processing_time.toFixed(2)}s
                  </span>
                )}
              </div>
            </div>

            <div className="answer-section">
              <h3>Answer</h3>
              <div className="answer-content">
                {response.answer}
              </div>
            </div>

            {response.sources.length > 0 && (
              <div className="sources-section">
                <h3>Sources ({response.sources.length})</h3>
                <div className="sources-list">
                  {response.sources.map((source, index) => (
                    <div key={index} className="source-item">
                      <div className="source-header">
                        <h4>
                          <a
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="source-link"
                          >
                            {source.title || `Source ${index + 1}`}
                            <ExternalLink size={14} />
                          </a>
                        </h4>
                        <span className="source-url">{source.url}</span>
                      </div>
                      <p className="source-content">{source.content}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
