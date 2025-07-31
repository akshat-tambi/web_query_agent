"""
Configuration management for Ripplica Query Agent
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the query agent"""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent
    DATA_DIR = PROJECT_ROOT / "data"
    
    # API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Embedding Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # FAISS Configuration
    FAISS_INDEX_PATH = PROJECT_ROOT / os.getenv("FAISS_INDEX_PATH", "data/query_cache.faiss")
    FAISS_METADATA_PATH = PROJECT_ROOT / os.getenv("FAISS_METADATA_PATH", "data/query_metadata.json")
    
    # Search Configuration
    MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))
    SEARCH_ENGINE = os.getenv("SEARCH_ENGINE", "duckduckgo")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "10000"))
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present"""
        errors = []
        
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is required")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        # Create data directory if it doesn't exist
        cls.DATA_DIR.mkdir(exist_ok=True)
        
        return True

# Create config instance
config = Config()
