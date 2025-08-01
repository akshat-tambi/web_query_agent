import time
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from ..models.schemas import QueryRequest, QueryResponse
from ..services.ai_service import ai_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    start_time = time.time()
    
    try:
        logger.info(f"Processing query: {request.query}")
        
        # process
        answer, sources, cached = await ai_service.process_query(
            query=request.query,
            max_results=request.max_results,
            search_engine=request.search_engine,
            use_cache=request.use_cache
        )
        
        processing_time = time.time() - start_time
        
        # create response
        response = QueryResponse(
            query=request.query,
            answer=answer,
            sources=sources,
            cached=cached,
            processing_time=processing_time
        )
        
        logger.info(f"Query processed in {processing_time:.2f}s (cached: {cached})")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )


@router.get("/cache/stats")
async def get_cache_stats():
    try:
        if not ai_service._initialized:
            await ai_service.initialize()
        
        total_entries = len(ai_service.query_metadata)
        faiss_size = ai_service.faiss_index.ntotal if ai_service.faiss_index else 0
        
        return {
            "total_cached_queries": total_entries,
            "faiss_index_size": faiss_size,
            "cache_enabled": True
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cache stats: {str(e)}"
        )
