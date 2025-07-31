"""
Pydantic models for request/response schemas
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for web query"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    max_results: Optional[int] = Field(5, ge=1, le=20, description="Maximum number of results")
    search_engine: Optional[str] = Field("bing", description="Search engine to use")
    use_cache: Optional[bool] = Field(True, description="Whether to use cached results")


class SearchResult(BaseModel):
    """Individual search result"""
    url: str
    title: Optional[str] = None
    content: str
    relevance_score: Optional[float] = None


class QueryResponse(BaseModel):
    """Response model for web query"""
    query: str
    answer: str
    sources: List[SearchResult]
    cached: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)
    processing_time: Optional[float] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
