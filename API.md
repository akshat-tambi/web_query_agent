# API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Quick Start
```bash
# Start the application
npm run dev

# Or start backend only
npm run dev:backend
```

## Endpoints

### Health Check
- **GET** `/health`
- **Description**: Check if the API is running
- **Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

### Query Processing
- **POST** `/query`
- **Description**: Process a web query with AI enhancement (backend automatically handles caching)
- **Request Body**:
```json
{
  "query": "What are the top tourist places in Delhi?",
  "max_results": 5,
  "search_engine": "bing"
}
```
- **Response**:
```json
{
  "query": "What are the top tourist places in Delhi?",
  "answer": "Based on the latest information...",
  "sources": [
    {
      "url": "https://example.com",
      "title": "Delhi Tourism Guide",
      "content": "Truncated content for display..."
    }
  ],
  "cached": false,
  "processing_time": 45.2,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Cache Statistics
- **GET** `/cache/stats`
- **Description**: Get current cache statistics
- **Response**:
```json
{
  "total_cached_queries": 15,
  "faiss_index_size": 15,
  "cache_enabled": true
}
```

### AI Service Initialization
- **POST** `/initialize`
- **Description**: Manually initialize AI models (normally done automatically)
- **Response**:
```json
{
  "message": "AI service initialized successfully"
}
```

### Error Responses
All endpoints may return error responses in the following format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `500`: Internal Server Error
- `503`: Service Unavailable

## Query Parameters

### `/query` endpoint
- `max_results` (integer, 1-20): Number of search results to process (default: 5)
- `search_engine` (string): Search engine to use - "bing", "google" (default: "bing")

**Note**: Caching is now handled automatically by the backend for optimal performance.

## Configuration

### Cache Behavior
- **Automatic**: Backend automatically handles caching decisions
- **Semantic similarity**: Uses vector embeddings for intelligent cache matching
- **Error exclusion**: Failed queries are never cached
- **Similarity threshold**: Configurable via `SIMILARITY_THRESHOLD` environment variable (default: 0.85)

### Timeouts
- Web scraping: 60 seconds per page
- Total query processing: ~2 minutes maximum
- Client should set request timeout to at least 120 seconds

## Environment Configuration

### Required Environment Variables
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### Optional Configuration
```bash
# AI Service Configuration
EMBEDDING_DIMENSION=384
SIMILARITY_THRESHOLD=0.85
MAX_CONTENT_LENGTH=500
ERROR_MESSAGE_PREFIX="I encountered an error"

# API Configuration  
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Search Configuration
MAX_SEARCH_RESULTS=5
DEFAULT_SEARCH_ENGINE=bing

# Cache Configuration
CACHE_TTL=3600

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Development
- Backend runs on `http://localhost:8000` with auto-reload
- Frontend runs on `http://localhost:5173` with hot reload
- Cache files stored in `backend/data/`
- Use `npm run dev` to start both services
- Use `npm run health` to check service status
