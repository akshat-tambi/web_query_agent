#!/usr/bin/env python3
"""
Ripplica Web Browser Query Agent
Main entry point for the CLI application
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional,             print(f"📋 Found similar query: '{cached_data['query']}' (similarity: {similarities[0][0]:.3f})")
            return cached_data['summary']
        else:
            print(f"🔍 No similar queries found (best similarity: {similarities[0][0]:.3f})")
            return None
            
    except Exception as e:
        print(f"❌ Error searching cache: {e}")
        return Nonet, Any

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
from datetime import datetime

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
            temperature=0.3,
            convert_system_message_to_human=True
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
        
        # Run async web scraping
        urls_and_content = asyncio.run(scrape_web_content(query))
        
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
        summary = generate_summary_with_langchain(documents, query)
        
        return summary
        
    except Exception as e:
        print(f"❌ Error getting summary from web: {e}")
        return f"❌ Error occurred while processing your query: {str(e)}"

async def scrape_web_content(query: str) -> List[tuple]:
    """
    Scrape web content using Playwright
    
    Args:
        query: Search query
        
    Returns:
        List of (url, content) tuples
    """
    urls_and_content = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Search on DuckDuckGo
            search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
            await page.goto(search_url, wait_until="networkidle")
            
            # Wait for results to load
            await page.wait_for_selector('[data-testid="result"]', timeout=10000)
            
            # Extract search result URLs
            result_elements = await page.query_selector_all('[data-testid="result"] h2 a')
            urls = []
            
            for element in result_elements[:config.MAX_SEARCH_RESULTS]:
                href = await element.get_attribute('href')
                if href and href.startswith('http'):
                    urls.append(href)
            
            print(f"� Found {len(urls)} URLs to scrape")
            
            # Scrape content from each URL
            for i, url in enumerate(urls):
                try:
                    print(f"📖 Scraping {i+1}/{len(urls)}: {url[:60]}...")
                    
                    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    
                    # Extract text content using page.content() and BeautifulSoup
                    html_content = await page.content()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style", "nav", "header", "footer"]):
                        script.decompose()
                    
                    # Extract text from main content areas
                    content_selectors = [
                        'main', 'article', '.content', '#content', 
                        '.post', '.entry', 'p', 'h1', 'h2', 'h3'
                    ]
                    
                    text_content = ""
                    for selector in content_selectors:
                        elements = soup.select(selector)
                        for element in elements:
                            text_content += element.get_text() + " "
                    
                    # Clean up text
                    clean_text = ' '.join(text_content.split())
                    
                    if len(clean_text) > 200:  # Only include substantial content
                        urls_and_content.append((url, clean_text))
                    
                except Exception as e:
                    print(f"❌ Error scraping {url}: {str(e)[:50]}...")
                    continue
            
        except Exception as e:
            print(f"❌ Error during web search: {e}")
        
        finally:
            await browser.close()
    
    return urls_and_content

def generate_summary_with_langchain(documents: List[Document], query: str) -> str:
    """
    Generate summary using LangChain's map-reduce strategy
    
    Args:
        documents: List of documents to summarize
        query: Original query for context
        
    Returns:
        str: Generated summary
    """
    try:
        if not documents:
            return "❌ No content available to summarize."
        
        # Use text splitter to handle large documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        
        split_docs = text_splitter.split_documents(documents)
        
        # Create summarization chain
        chain = load_summarize_chain(
            llm,
            chain_type="map_reduce",
            verbose=False
        )
        
        # Generate summary with context
        prompt_template = f"""
        Based on the following content, provide a comprehensive summary that answers the query: "{query}"
        
        Focus on:
        1. Key information relevant to the query
        2. Important facts and details
        3. Multiple perspectives if available
        4. Actionable insights or recommendations
        
        Content to summarize:
        """
        
        # Add custom prompt context
        for doc in split_docs:
            doc.page_content = prompt_template + doc.page_content
        
        result = chain.invoke({"input_documents": split_docs})
        
        return result["output_text"]
        
    except Exception as e:
        print(f"❌ Error generating summary: {e}")
        return f"❌ Error generating summary: {str(e)}"

def save_to_cache(query: str, summary: str) -> None:
    """
    Save query and summary to cache for future use
    
    Args:
        query: Original user query
        summary: Generated summary
    """
    # TODO: Implement using FAISS vector storage
    print(f"� Saving to cache: {query[:50]}...")

@click.command()
@click.argument('query', required=False)
@click.option('--interactive', '-i', is_flag=True, help='Run in interactive mode')
def main(query, interactive):
    """
    Ripplica Web Browser Query Agent
    
    Process web queries with intelligent caching and summarization.
    """
    print("�🔍 Ripplica Query Agent")
    print("=" * 30)
    
    try:
        # Validate configuration
        config.validate()
        print("✅ Configuration validated")
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

if __name__ == "__main__":
    main()
