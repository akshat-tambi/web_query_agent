# Web Query Agent

An AI-powered web query agent with intelligent scraping, semantic caching, and a modern React frontend.

## Architecture└── 🚀 Development Workflow
    1. cd backend && python3 run.py     # Start backend
    2. cd frontend && npm run dev        # Start frontend (new terminal)

🔗 URLs (when running):
  Frontend:  http://localhost:5173
  Backend:   http://localhost:8000

- **Backend**: FastAPI REST API with AI/ML capabilities
- **Frontend**: Modern React application built with Vite
- **AI/ML**: Google Gemini for responses, SentenceTransformers for embeddings, FAISS for caching

## Features

### Backend Features
- 🔍 **Intelligent Web Scraping**: Uses Playwright to scrape multiple search engines
- 🤖 **AI-Powered Responses**: Leverages Google Gemini for generating comprehensive answers
- 💾 **Smart Caching**: FAISS-based semantic caching for faster responses
- 🚀 **Fast API**: RESTful API built with FastAPI
- 📊 **Real-time Processing**: Asynchronous processing for better performance

### Frontend Features
- 🎨 **Modern UI**: Clean, responsive React interface
- ⚡ **Built with Vite**: Fast development and build process
- 🎯 **Real-time Status**: Shows backend health and cache statistics
- 🔧 **Configurable**: Adjustable search parameters
- 📱 **Responsive**: Works on desktop and mobile devices

## Quick Start

### Prerequisites
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
   - Search engine (Bing, Google, DuckDuckGo)
   - Enable/disable caching
4. **Click Submit** and wait for the AI-generated response
5. **View sources** and click links to visit original content

## API Documentation

When the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

### Main Endpoints

- `POST /api/v1/query` - Process a web query
- `GET /api/v1/health` - Health check
- `GET /api/v1/cache/stats` - Cache statistics
- `POST /api/v1/initialize` - Initialize AI models

## Project Structure

```
📁 AI Web Query Application
======================================

🗂️  Project Root
├── � package.json        # Root scripts & dependencies
├── �🔧 Backend (FastAPI)
│   ├── app/
│   │   ├── api/           # REST API endpoints  
│   │   ├── models/        # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── config.py      # Configuration
│   │   └── main.py        # FastAPI application
│   ├── data/              # 💾 Cache files (FAISS)
│   ├── requirements.txt   # Python dependencies
│   ├── run.py            # Server startup
│   ├── .env              # Environment variables
│   └── COMMANDS.md       # Backend commands
│
├── 🎨 Frontend (React + Vite)
│   ├── src/
│   │   ├── services/     # API client
│   │   ├── App.tsx       # Main component
│   │   └── ...           # Other components
│   ├── package.json      # Node dependencies & scripts
│   ├── tsconfig.json     # TypeScript configuration
│   └── .env              # Environment variables
│
└── � Available Commands
    npm run dev             # Start both services
    npm run dev:backend     # Backend only
    npm run dev:frontend    # Frontend only
    npm run install:all     # Install all dependencies
    npm run build           # Build for production
    npm run health          # Check system health

🔗 URLs (when running):
  Frontend:  http://localhost:5173
  Backend:   http://localhost:8000
  API Docs:  http://localhost:8000/docs

```

## Configuration

### Backend Configuration (`backend/.env`)
- `GEMINI_API_KEY`: Your Google Gemini API key **(Required)**
- `API_HOST`: Server host (default: 0.0.0.0)
- `API_PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (true/false)
- `EMBEDDING_DIMENSION`: Vector dimension (default: 384)
- `SIMILARITY_THRESHOLD`: Cache similarity threshold (default: 0.85)
- `MAX_CONTENT_LENGTH`: Content truncation length (default: 500)
- `ERROR_MESSAGE_PREFIX`: Error message prefix (default: "I encountered an error")
- `MAX_SEARCH_RESULTS`: Maximum search results (default: 5)
- `DEFAULT_SEARCH_ENGINE`: Default search engine (bing/google/duckduckgo)
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

# Health check
python3 ../health-check.py
```

### Frontend Commands
```bash
cd frontend

npm run dev             # Start development server
npm run build           # Build for production
npm run preview         # Preview production build
npm run lint            # Run ESLint
npm run lint:fix        # Fix ESLint issues
npm run type-check      # TypeScript type checking
npm run clean           # Clean node_modules and dist
```

## Development

### Full Stack Development
Start both services in separate terminals:

**Terminal 1 - Backend:**
```bash
cd backend
python3 run.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Building for Production

#### Frontend
```bash
cd frontend
npm run build
npm run preview  # Preview production build
```

#### Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not found"**
   - Make sure you've added your API key to `backend/.env`
   - Restart the backend server after adding the key

2. **"Backend server not responding"**
   - Check if the backend is running on port 8000
   - Verify the API_BASE_URL in frontend/.env

3. **Playwright browser issues**
   - Run `playwright install` in the backend directory
   - Make sure you have sufficient disk space

4. **Port already in use**
   - Backend (8000): Change `API_PORT` in backend/.env
   - Frontend (5173): Use `npm run dev -- --port 3000`

### Logs and Debugging

- Backend logs are printed to console
- Check browser console for frontend errors
- Use the `/health` endpoint to verify backend status

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

If you encounter any issues or have questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Open an issue on GitHub
