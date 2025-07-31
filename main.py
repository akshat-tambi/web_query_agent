#!/usr/bin/env python3
"""
Web Browser Query Agent
Main entry point for the CLI application
"""

import os
import sys
import json
import asyncio
import warnings
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_google_genai")
warnings.filterwarnings("ignore", category=FutureWarning, module="torch")
warnings.filterwarnings("ignore", message=".*tokenizers.*", category=UserWarning)

# Set environment variable to suppress tokenizer parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import click
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import Document
from langchain.chains.summarize import load_summarize_chain

from config import config

# Global variables for caching models
embedding_model = None
llm = None
faiss_index = None
query_metadata = []

def initialize_models():
    """Initialize AI models and FAISS index"""
    global embedding_model, llm, faiss_index, query_metadata
    
    try:
        # Initialize Gemini
        genai.configure(api_key=config.GEMINI_API_KEY)
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=config.GEMINI_API_KEY,
            temperature=0.3
        )
        
        # Initialize embedding model
        print("📦 Loading embedding model...")
        embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        
        # Load or create FAISS index
        load_faiss_index()
        
        print("✅ Models initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing models: {e}")
        sys.exit(1)

def load_faiss_index():
    """Load existing FAISS index or create new one"""
    global faiss_index, query_metadata
    
    try:
        if config.FAISS_INDEX_PATH.exists() and config.FAISS_METADATA_PATH.exists():
            print("📂 Loading existing FAISS index...")
            faiss_index = faiss.read_index(str(config.FAISS_INDEX_PATH))
            
            with open(config.FAISS_METADATA_PATH, 'r') as f:
                query_metadata = json.load(f)
            
            print(f"✅ Loaded FAISS index with {faiss_index.ntotal} entries")
        else:
            print("🆕 Creating new FAISS index...")
            # Create new index (384 dimensions for all-MiniLM-L6-v2)
            dimension = 384
            faiss_index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
            query_metadata = []
            
    except Exception as e:
        print(f"❌ Error loading FAISS index: {e}")
        # Create fallback index
        dimension = 384
        faiss_index = faiss.IndexFlatIP(dimension)
        query_metadata = []

def save_faiss_index():
    """Save FAISS index and metadata to disk"""
    try:
        faiss.write_index(faiss_index, str(config.FAISS_INDEX_PATH))
        
        with open(config.FAISS_METADATA_PATH, 'w') as f:
            json.dump(query_metadata, f, indent=2)
            
    except Exception as e:
        print(f"❌ Error saving FAISS index: {e}")

# Core agent functions
def validate_query(query: str) -> bool:
    """
    Validate if the query is a valid web search query using Gemini
    
    Args:
        query: User input query
        
    Returns:
        bool: True if valid, False if invalid
    """
    try:
        print(f"🔍 Validating query: {query}")
        
        validation_prompt = f"""
        Analyze the following user input. Is it a query that can be answered by a web search?
        
        Examples of VALID queries:
        - "What is the capital of France?"
        - "Best restaurants in Tokyo"
        - "How to learn Python programming"
        - "Latest news about AI"
        
        Examples of INVALID queries:
        - "Walk my pet"
        - "Add apples to grocery list"
        - "Remind me to call mom"
        - "Turn off the lights"
        
        User input: "{query}"
        
        Respond with only the word "VALID" or "INVALID".
        """
        
        response = llm.invoke(validation_prompt)
        result = response.content.strip().upper()
        
        is_valid = result == "VALID"
        print(f"{'✅' if is_valid else '❌'} Query validation: {result}")
        
        return is_valid
        
    except Exception as e:
        print(f"❌ Error validating query: {e}")
        # Default to valid if validation fails
        return True

def get_summary_from_cache(query: str) -> Optional[str]:
    """
    Check if a similar query exists in cache using FAISS vector search
    
    Args:
        query: User input query
        
    Returns:
        str: Cached summary if found, None otherwise
    """
    try:
        print(f"🔍 Searching cache for: {query}")
        
        if faiss_index.ntotal == 0:
            print("📭 Cache is empty")
            return None
        
        # Generate embedding for the query
        query_embedding = embedding_model.encode([query], convert_to_tensor=False, normalize_embeddings=True)
        query_vector = np.array(query_embedding, dtype=np.float32)
        
        # Search for similar queries
        similarities, indices = faiss_index.search(query_vector, k=1)
        
        # Check if similarity is above threshold
        if similarities[0][0] >= config.SIMILARITY_THRESHOLD:
            cached_index = indices[0][0]
            cached_data = query_metadata[cached_index]
            
            print(f"� Found similar query: '{cached_data['query']}' (similarity: {similarities[0][0]:.3f})")
            return cached_data['summary']
        else:
            print(f"🔍 No similar queries found (best similarity: {similarities[0][0]:.3f})")
            return None
            
    except Exception as e:
        print(f"❌ Error searching cache: {e}")
        return None

def get_summary_from_web(query: str) -> str:
    """
    Search web, scrape content, and generate summary using Playwright + BeautifulSoup + LangChain
    
    Args:
        query: User input query
        
    Returns:
        str: Generated summary from web content
    """
    try:
        print(f"🌐 Searching web for: {query}")
        
        # Import web scraper functions
        from web_scraper import scrape_web_content, generate_summary_with_langchain
        
        # Run async web scraping
        urls_and_content = asyncio.run(scrape_web_content(
            query, 
            config.MAX_SEARCH_RESULTS, 
            config.SEARCH_ENGINE
        ))
        
        if not urls_and_content:
            return "❌ No content found for this query."
        
        print(f"📄 Scraped content from {len(urls_and_content)} pages")
        
        # Prepare documents for summarization
        documents = []
        for url, content in urls_and_content:
            # Truncate content if too long
            if len(content) > config.MAX_CONTENT_LENGTH:
                content = content[:config.MAX_CONTENT_LENGTH] + "..."
            
            documents.append(Document(
                page_content=content,
                metadata={"source": url}
            ))
        
        # Generate summary using LangChain
        print("🤖 Generating summary...")
        summary = generate_summary_with_langchain(documents, query, llm, config.MAX_CONTENT_LENGTH)
        
        return summary
        
    except Exception as e:
        print(f"❌ Error getting summary from web: {e}")
        return f"❌ Error occurred while processing your query: {str(e)}"

@click.command()
@click.argument('query', required=False)
@click.option('--interactive', '-i', is_flag=True, help='Run in interactive mode')
def main(query, interactive):
    """
    Web Browser Query Agent
    
    Process web queries with intelligent caching and summarization.
    """
    print("🔍 Web Browser Query Agent")
    print("=" * 30)
    
    try:
        # Validate configuration
        config.validate()
        print("✅ Configuration validated")
        
        # Initialize models
        initialize_models()
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Interactive mode
    if interactive or not query:
        print("\n💬 Interactive mode (type 'quit' to exit)")
        while True:
            try:
                user_query = input("\nEnter your query: ").strip()
                if user_query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                if user_query:
                    process_query(user_query)
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
    else:
        # Single query mode
        process_query(query)

def process_query(query: str) -> None:
    """Process a single query through the agent pipeline"""
    print(f"\n🔄 Processing: {query}")
    
    # Step 1: Validate query
    if not validate_query(query):
        print("❌ This is not a valid query.")
        return
    
    # Step 2: Check cache
    cached_summary = get_summary_from_cache(query)
    if cached_summary:
        print("📋 Found in cache!")
        print(f"\n📄 Summary:\n{cached_summary}")
        return
    
    # Step 3: Search web and generate summary
    print("🌐 No cache found, searching web...")
    summary = get_summary_from_web(query)
    
    # Step 4: Save to cache
    save_to_cache(query, summary)
    
    # Step 5: Return result
    print(f"\n📄 Summary:\n{summary}")

def save_to_cache(query: str, summary: str) -> None:
    """
    Save query and summary to cache using FAISS vector storage
    
    Args:
        query: Original user query
        summary: Generated summary
    """
    try:
        print(f"💾 Saving to cache: {query[:50]}...")
        
        # Generate embedding for the query
        query_embedding = embedding_model.encode([query], convert_to_tensor=False, normalize_embeddings=True)
        query_vector = np.array(query_embedding, dtype=np.float32)
        
        # Add to FAISS index
        faiss_index.add(query_vector)
        
        # Add metadata
        query_metadata.append({
            "query": query,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        })
        
        # Save to disk
        save_faiss_index()
        
        print(f"✅ Cached successfully! Total entries: {faiss_index.ntotal}")
        
    except Exception as e:
        print(f"❌ Error saving to cache: {e}")

if __name__ == "__main__":
    main()
