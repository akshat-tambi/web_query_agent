"""
Configuration management for the backend API
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings"""
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    
    # AI/ML Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # FAISS Configuration
    FAISS_INDEX_PATH: Path = DATA_DIR / "query_cache.faiss"
    FAISS_METADATA_PATH: Path = DATA_DIR / "query_metadata.json"
    
    # Search Configuration
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    DEFAULT_SEARCH_ENGINE: str = os.getenv("DEFAULT_SEARCH_ENGINE", "bing")
    
    # CORS Configuration
    CORS_ORIGINS: list = [
        "http://localhost:3000",  # React dev server
        "http://localhost:3001",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",  # Vite dev server
    ]
    
    # Cache Configuration
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    
    def __init__(self):
        # Ensure data directory exists
        self.DATA_DIR.mkdir(exist_ok=True)
        
        # Validate required settings
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")


# Global settings instance
settings = Settings()
