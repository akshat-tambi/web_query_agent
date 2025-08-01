import json
import asyncio
import logging
from typing import List, Optional, Dict, Any, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import Document

from ..config import settings
from ..models.schemas import SearchResult
from .web_scraper import WebScraperService

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.embedding_model: Optional[SentenceTransformer] = None
        self.llm: Optional[ChatGoogleGenerativeAI] = None
        self.faiss_index: Optional[faiss.Index] = None
        self.query_metadata: List[Dict[str, Any]] = []
        self._initialized = False
    
    async def initialize(self):
        if self._initialized:
            return
            
        try:
            logger.info("Initializing AI models...")
            genai.configure(api_key=settings.GEMINI_API_KEY)
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.3
            )
            await self._load_faiss_index()
            
            self._initialized = True
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AI models: {e}")
            raise
    
    async def _load_faiss_index(self):
        try:
            if settings.FAISS_INDEX_PATH.exists():
                logger.info("Loading existing FAISS index...")
                self.faiss_index = faiss.read_index(str(settings.FAISS_INDEX_PATH))
                
                if settings.FAISS_METADATA_PATH.exists():
                    with open(settings.FAISS_METADATA_PATH, 'r') as f:
                        self.query_metadata = json.load(f)
                
                logger.info(f"Loaded FAISS index with {self.faiss_index.ntotal} vectors")
            else:
                logger.info("Creating new FAISS index...")
                self.faiss_index = faiss.IndexFlatIP(settings.EMBEDDING_DIMENSION)
                self.query_metadata = []
                
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            self.faiss_index = faiss.IndexFlatIP(settings.EMBEDDING_DIMENSION)
            self.query_metadata = []
    
    async def save_faiss_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            settings.DATA_DIR.mkdir(exist_ok=True)
            faiss.write_index(self.faiss_index, str(settings.FAISS_INDEX_PATH))
            with open(settings.FAISS_METADATA_PATH, 'w') as f:
                json.dump(self.query_metadata, f, indent=2, default=str)
                
            logger.info("FAISS index and metadata saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
    
    async def process_query(
        self, 
        query: str, 
        max_results: int = 5, 
        search_engine: str = "bing",
        use_cache: bool = True
    ) -> Tuple[str, List[SearchResult], bool]:
        """
        Process a user query and return AI-generated answer with sources
        
        Returns:
            Tuple of (answer, sources, was_cached)
        """
        if not self._initialized:
            await self.initialize()
        
        if use_cache:
            cached_result = await self._check_cache(query)
            if cached_result:
                return cached_result["answer"], cached_result["sources"], True
        
        logger.info(f"Processing new query: {query}")
        async with WebScraperService() as scraper:
            scraped_data = await scraper.scrape_web_content(query, max_results, search_engine)
        
        if not scraped_data:
            return "I couldn't find any relevant information for your query.", [], False
        
        sources, documents = self._process_scraped_data(scraped_data)
        answer = await self._generate_answer(query, documents)
        
        if use_cache and not answer.startswith(settings.ERROR_MESSAGE_PREFIX):
            await self._cache_result(query, answer, sources)
        
        return answer, sources, False
    
    def _process_scraped_data(self, scraped_data: List[Tuple[str, str, Optional[str]]]) -> Tuple[List[SearchResult], List[Document]]:
        sources = []
        documents = []
        
        for url, content, title in scraped_data:
            search_result = SearchResult(
                url=url,
                title=title,
                content=content[:settings.MAX_CONTENT_LENGTH] + "..." if len(content) > settings.MAX_CONTENT_LENGTH else content
            )
            sources.append(search_result)
            
            doc = Document(
                page_content=content,
                metadata={"url": url, "title": title or ""}
            )
            documents.append(doc)
        
        return sources, documents
    
    async def _check_cache(self, query: str) -> Optional[Dict[str, Any]]:
        try:
            if self.faiss_index.ntotal == 0:
                return None
            
            query_embedding = self.embedding_model.encode([query])
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            
            similarities, indices = self.faiss_index.search(query_embedding, 1)
            
            if similarities[0][0] > settings.SIMILARITY_THRESHOLD:  
                cached_idx = indices[0][0]
                if cached_idx < len(self.query_metadata):
                    cached_data = self.query_metadata[cached_idx]
                    logger.info(f"Found cached result for query: {query}")
                    return cached_data
            
        except Exception as e:
            logger.error(f"Error checking cache: {e}")
        
        return None
    
    async def _cache_result(self, query: str, answer: str, sources: List[SearchResult]):
        try:
            query_embedding = self.embedding_model.encode([query])
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            
            self.faiss_index.add(query_embedding)
            
            metadata = {
                "query": query,
                "answer": answer,
                "sources": [source.dict() for source in sources],
                "timestamp": str(asyncio.get_event_loop().time())
            }
            self.query_metadata.append(metadata)
            await self.save_faiss_index()
            logger.info(f"Cached result for query: {query}")
            
        except Exception as e:
            logger.error(f"Error caching result: {e}")
    
    async def _generate_answer(self, query: str, documents: List[Document]) -> str:
        try:
            split_docs = self._split_documents(documents)
            context = self._create_context_from_documents(split_docs)
            prompt = self._create_answer_prompt(query, context)
            response = await self.llm.ainvoke(prompt)
            return response.content.strip() if hasattr(response, 'content') else str(response).strip()
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"{settings.ERROR_MESSAGE_PREFIX} while processing your query. Please try again."
    
    def _split_documents(self, documents: List[Document]) -> List[Document]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        
        split_docs = []
        for doc in documents:
            chunks = text_splitter.split_documents([doc])
            split_docs.extend(chunks)
        
        return split_docs[:10] if len(split_docs) > 10 else split_docs
    
    def _create_context_from_documents(self, documents: List[Document]) -> str:
        return "\n\n".join([doc.page_content[:500] for doc in documents])
    
    def _create_answer_prompt(self, query: str, context: str) -> str:
        """Create the prompt for answer generation"""
        return f"""
        Based on the following web content, provide a comprehensive and accurate answer to the user's question.
        
        Question: {query}
        
        Context from web sources:
        {context}
        
        Please provide a detailed, well-structured answer that directly addresses the question using the information from the sources. If the sources don't contain enough information to fully answer the question, please mention that.
        """

ai_service = AIService()
