# Web Query Agent

An intelligent AI-powered web query application that searches, analyzes, and provides comprehensive answers to your questions by scraping and processing web content in real-time. Built with React, FastAPI, and Google Gemini AI.

For development, start both services:

1. **Backend**: `cd backend && python3 run.py`
2. **Frontend**: `cd frontend && npm run dev` (new terminal)

🔗 URLs (when running):
- Frontend:  http://localhost:5173
- Backend:   http://localhost:8000

## Architecture

- **Backend**: FastAPI REST API with AI/ML capabilities
- **Frontend**: Modern React application built with Vite  
- **AI/ML**: Google Gemini for responses, SentenceTransformers for embeddings, FAISS for caching

## ✨ Key Features

### Backend Features
- 🔍 **Intelligent Web Scraping**: Uses Playwright to scrape multiple search engines (Bing, Google)
- 🤖 **AI-Powered Responses**: Leverages Google Gemini for generating comprehensive, context-aware answers
- 💾 **Smart Caching**: FAISS-based semantic caching for faster responses and reduced API costs
- ✅ **Query Validation**: AI validates queries before processing to ensure quality responses
- 🚀 **Fast API**: RESTful API built with FastAPI with automatic documentation
- 📊 **Real-time Processing**: Asynchronous processing for better performance

### Frontend Features
- 🎨 **Modern UI**: Clean, responsive React interface with modern design
- ⚡ **Built with Vite**: Fast development and build process with TypeScript support
- 🎯 **Real-time Status**: Shows backend health and cache statistics
- 🔧 **Configurable**: Adjustable search parameters and engine selection
- 📱 **Responsive**: Works seamlessly on desktop and mobile devices
- 📝 **Rich Text**: Markdown rendering for bold/italic text in responses
- 📚 **Search History**: Track and revisit previous queries

## Quick Start

### Prerequisites
- **Python 3.8+** and **Node.js 16+**
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/akshat-tambi/web_query_agent.git
   cd web_query_agent
   ```

2. **Environment Setup**:
- Python 3.8+
- Node.js 16+
- npm

### Environment Setup

1. **Clone or navigate to the project directory**

2. **Set up environment variables**:
   ```bash
   # Backend environment
   cp backend/.env.example backend/.env
   # Edit backend/.env and add your GEMINI_API_KEY
   
   # Frontend environment  
   cp frontend/.env.example frontend/.env
   # Adjust API_BASE_URL if needed
   ```

3. **Get a Gemini API Key**:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it to `backend/.env` as `GEMINI_API_KEY=your_key_here`

### Development Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Start the server
python3 run.py
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Usage

1. **Open your browser** and go to `http://localhost:5173`
2. **Enter your query** in the search box
3. **Configure options** (optional):
   - Max results (3-15)
   - Search engine (Bing, Google)
   - Enable/disable caching
4. **Click Submit** and wait for the AI-generated response
5. **View sources** and click links to visit original content

### Main Endpoints

- `POST /api/v1/query` - Process a web query  
- `GET /api/v1/cache/stats` - Cache statistics

## Project Structure

```
Web Query Agent
├── � package.json           # Root scripts & dependencies  
├── 🏗️ backend/               # FastAPI Backend
│   ├── app/
│   │   ├── api/              # REST API endpoints  
│   │   ├── models/           # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   ├── config.py         # Configuration
│   │   └── main.py           # FastAPI application
│   ├── data/                 # 💾 Cache files (FAISS)
│   ├── requirements.txt      # Python dependencies
│   ├── run.py               # Server startup
│   └── .env                 # Environment variables
│
├── 🎨 frontend/              # React + Vite Frontend
    ├── src/
    │   ├── services/        # API client
    │   ├── utils/           # Utilities (text formatting)
    │   ├── App.tsx          # Main component
    │   └── App.css          # Modern styling
    ├── package.json         # Node dependencies & scripts
    ├── tsconfig.json        # TypeScript configuration
    └── .env                 # Environment variables
```

**🔗 URLs (when running):**
- Frontend:  http://localhost:5173
- Backend:   http://localhost:8000

## Configuration

### Backend Configuration (`backend/.env`)
- `GEMINI_API_KEY`: Your Google Gemini API key **(Required)**
- `API_HOST`: Server host (default: 0.0.0.0)
- `API_PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (true/false)
- `EMBEDDING_MODEL`: Sentence transformer model (default: all-MiniLM-L6-v2)
- `EMBEDDING_DIMENSION`: Vector dimension (default: 384)
- `SIMILARITY_THRESHOLD`: Cache similarity threshold (default: 0.85)
- `MAX_CONTENT_LENGTH`: Content truncation length (default: 500)
- `ERROR_MESSAGE_PREFIX`: Error message prefix (default: "I encountered an error")
- `MAX_SEARCH_RESULTS`: Maximum search results (default: 5)
- `DEFAULT_SEARCH_ENGINE`: Default search engine (bing/google)
- `CACHE_TTL`: Cache time-to-live in seconds (default: 3600)
- `CORS_ORIGINS`: Allowed frontend origins (comma-separated)

### Frontend Configuration (`frontend/.env`)
- `VITE_API_BASE_URL`: Backend API URL (default: http://localhost:8000)

## Available Commands

### Backend Commands
```bash
cd backend

# Development
python3 run.py           # Start with auto-reload

# Production  
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
```

### Frontend Commands
```bash
cd frontend
npm run dev             # Start development server
```