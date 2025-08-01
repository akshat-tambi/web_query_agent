import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    BACKEND_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BACKEND_ROOT / "data"
    
    # Model Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # AI Service Configuration
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))
    MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH", "500"))
    ERROR_MESSAGE_PREFIX: str = os.getenv("ERROR_MESSAGE_PREFIX", "I encountered an error")
    
    # FAISS Configuration
    FAISS_INDEX_PATH: Path = DATA_DIR / "query_cache.faiss"
    FAISS_METADATA_PATH: Path = DATA_DIR / "query_metadata.json"
    
    # Search Configuration
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    DEFAULT_SEARCH_ENGINE: str = os.getenv("DEFAULT_SEARCH_ENGINE", "bing")
    
    # CORS Configuration
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS", "*"
    ).split(",")
    
    # Cache Configuration
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    
    def __init__(self):
        self.DATA_DIR.mkdir(exist_ok=True)

        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")

settings = Settings()
