import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Send, 
  Clock, 
  ExternalLink, 
  Database, 
  Sparkles,
  Zap,
  MessageSquare,
  Link2,
  CheckCircle,
  History,
  Settings,
  Brain
} from 'lucide-react';
import ApiService, { handleApiError } from './services/api';
import type { QueryResponse, CacheStats } from './services/api';
import { formatMarkdownText } from './utils/textFormatter';
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
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    const history = localStorage.getItem('web-query-agent-search-history');
    if (history) {
      setSearchHistory(JSON.parse(history));
    }
  }, []);

  useEffect(() => {
    loadCacheStats();
  }, []);

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
      
      const newHistory = [query.trim(), ...searchHistory.filter(q => q !== query.trim())].slice(0, 8);
      setSearchHistory(newHistory);
      localStorage.setItem('web-query-agent-search-history', JSON.stringify(newHistory));
      
      loadCacheStats();
    } catch (error) {
      setError(handleApiError(error));
    } finally {
      setLoading(false);
    }
  };

  const handleHistoryClick = (historyQuery: string) => {
    setQuery(historyQuery);
  };

  const quickSuggestions = [
    "What are the latest AI developments?",
    "Explain quantum computing",
    "Best practices for web development",
    "Climate change solutions 2024"
  ];

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>
            <Brain className="header-icon" />
            Web Query Agent
          </h1>
          <div className="status-indicators">
            {cacheStats && (
              <div className="status-indicator healthy">
                <Database size={16} />
                <span>{cacheStats.total_cached_queries} cached</span>
              </div>
            )}
            <div className="status-indicator healthy">
              <Zap size={16} />
              <span>AI Ready</span>
            </div>
          </div>
        </div>
      </header>

      <main className="main-content">
        <div className="query-section">
          <form onSubmit={handleSubmit} className="query-form">
            <div className="search-input-container">
              <Search className="search-icon" size={20} />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask me anything about the web..."
                className="search-input"
                disabled={loading}
              />
            </div>

            {!query && !response && (
              <div className="quick-suggestions">
                <h4>Try asking about:</h4>
                <div className="suggestions-grid">
                  {quickSuggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      type="button"
                      className="suggestion-chip"
                      onClick={() => setQuery(suggestion)}
                    >
                      <Sparkles size={14} />
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {searchHistory.length > 0 && !loading && (
              <div className="search-history">
                <h4>
                  <History size={16} />
                  Recent searches
                </h4>
                <div className="history-chips">
                  {searchHistory.slice(0, 4).map((historyQuery, index) => (
                    <button
                      key={index}
                      type="button"
                      className="history-chip"
                      onClick={() => handleHistoryClick(historyQuery)}
                    >
                      <Clock size={12} />
                      {historyQuery.length > 40 ? `${historyQuery.slice(0, 40)}...` : historyQuery}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="advanced-toggle">
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="toggle-button"
              >
                <Settings size={16} />
                {showAdvanced ? 'Hide' : 'Show'} Advanced Options
              </button>
            </div>

            {showAdvanced && (
              <div className="options-grid">
                <div className="option-group">
                  <label>Max Results</label>
                  <select
                    value={maxResults}
                    onChange={(e) => setMaxResults(Number(e.target.value))}
                    disabled={loading}
                  >
                    <option value={3}>3 results</option>
                    <option value={5}>5 results</option>
                    <option value={10}>10 results</option>
                    <option value={15}>15 results</option>
                  </select>
                </div>

                <div className="option-group">
                  <label>Search Engine</label>
                  <select
                    value={searchEngine}
                    onChange={(e) => setSearchEngine(e.target.value)}
                    disabled={loading}
                  >
                    <option value="bing">Bing</option>
                    <option value="google">Google</option>
                  </select>
                </div>

                <div className="option-group">
                  <label className="checkbox-option">
                    <input
                      type="checkbox"
                      checked={useCache}
                      onChange={(e) => setUseCache(e.target.checked)}
                      disabled={loading}
                    />
                    Enable smart caching for faster results
                  </label>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="submit-button"
            >
              {loading ? (
                <>
                  <Clock className="loading-spinner" size={20} />
                  Processing...
                </>
              ) : (
                <>
                  <Send size={20} />
                  Search & Analyze
                </>
              )}
            </button>
          </form>
        </div>

        {loading && (
          <div className="loading-section">
            <div className="loading-content">
              <Sparkles className="loading-spinner" size={32} />
              <h3>Analyzing the web for you</h3>
              <p>
                {response ? 
                  'Generating intelligent response...' : 
                  'Searching across multiple sources and analyzing content. This may take 30-60 seconds for new queries. Cached results are instant!'
                }
              </p>
            </div>
          </div>
        )}

        {error && (
          <div className="error-message">
            <h3>
              <ExternalLink size={20} />
              Something went wrong
            </h3>
            <p>{error}</p>
          </div>
        )}

        {response && (
          <div className="response-section">
            <div className="response-header">
              <h2>
                <MessageSquare size={24} />
                AI Analysis
              </h2>
              <div className="response-meta">
                {response.cached && (
                  <span className="cache-badge">
                    <CheckCircle size={14} />
                    Cached
                  </span>
                )}
                {response.processing_time && (
                  <span className="cache-badge">
                    <Clock size={14} />
                    {response.processing_time.toFixed(1)}s
                  </span>
                )}
              </div>
            </div>

            <div className="response-content">
              <div className="ai-answer-section">
                <div className="ai-answer-header">
                  <Brain size={20} />
                  <h3>Summary</h3>
                </div>
                <div className="response-text">
                  {formatMarkdownText(response.answer)}
                </div>
              </div>

              {response.sources.length > 0 && (
                <div className="sources-section">
                  <h3>
                    <Link2 size={20} />
                    Sources ({response.sources.length})
                  </h3>
                  <div className="sources-grid">
                    {response.sources.map((source, index) => (
                      <a
                        key={index}
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="source-card"
                      >
                        <div className="source-title">
                          <ExternalLink size={16} />
                          {source.title || `Source ${index + 1}`}
                        </div>
                        <div className="source-url">{source.url}</div>
                        <div className="source-content">
                          {source.content.length > 150 
                            ? `${source.content.slice(0, 150)}...` 
                            : source.content
                          }
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
