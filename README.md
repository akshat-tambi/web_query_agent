# Ripplica Web Query Application

An AI-powered web query application with intelligent scraping, caching, and a modern React frontend.

## Architecture

This project is structured as a **frontend-backend architecture**:

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
- npm or yarn

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

### Automated Setup (Recommended)

Run the automated setup script:
```bash
./start.sh
```

This script will:
- Check dependencies
- Set up Python virtual environment
- Install all backend dependencies
- Install Playwright browsers
- Install frontend dependencies
- Start both backend and frontend servers

### Manual Setup

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
python run.py
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
ripplica-project/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   ├── config.py       # Configuration
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt    # Python dependencies
│   ├── run.py             # Server startup
│   └── .env               # Environment variables
├── frontend/               # React frontend
│   ├── src/
│   │   ├── services/      # API service
│   │   ├── App.tsx        # Main component
│   │   └── ...
│   ├── package.json       # Node dependencies
│   └── .env              # Environment variables
├── data/                  # Shared data directory
│   ├── query_cache.faiss  # FAISS index
│   └── query_metadata.json # Cache metadata
└── start.sh              # Automated startup script
```

## Configuration

### Backend Configuration (`backend/.env`)
- `GEMINI_API_KEY`: Your Google Gemini API key
- `API_HOST`: Server host (default: 0.0.0.0)
- `API_PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (true/false)
- `MAX_SEARCH_RESULTS`: Maximum search results (default: 5)
- `DEFAULT_SEARCH_ENGINE`: Default search engine (bing/google/duckduckgo)

### Frontend Configuration (`frontend/.env`)
- `VITE_API_BASE_URL`: Backend API URL (default: http://localhost:8000)

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
python run.py  # Runs with auto-reload in debug mode
```

### Frontend Development
```bash
cd frontend
npm run dev  # Runs with hot reload
```

### Building for Production

#### Backend
```bash
cd backend
pip install gunicorn
gunicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm run build
npm run preview  # Preview production build
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
