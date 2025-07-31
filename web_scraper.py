# Simple web scraper helper functions
import asyncio
from typing import List, Tuple
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain

async def scrape_web_content(query: str, max_results: int = 5) -> List[Tuple[str, str]]:
    """
    Scrape web content using Playwright
    
    Args:
        query: Search query
        max_results: Maximum number of URLs to scrape
        
    Returns:
        List of (url, content) tuples
    """
    urls_and_content = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Search on Bing (more bot-friendly)
            search_url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
            await page.goto(search_url, wait_until="networkidle")
            
            # Wait for results to load
            await page.wait_for_selector('.b_algo h2 a', timeout=10000)
            
            # Extract search result URLs
            result_elements = await page.query_selector_all('.b_algo h2 a')
            urls = []
            
            for element in result_elements[:max_results]:
                href = await element.get_attribute('href')
                if href and href.startswith('http') and 'bing.com' not in href:
                    urls.append(href)
            
            print(f"🔗 Found {len(urls)} URLs to scrape")
            
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

def generate_summary_with_langchain(documents: List[Document], query: str, llm) -> str:
    """
    Generate summary using a single API call to avoid rate limits
    
    Args:
        documents: List of documents to summarize
        query: Original query for context
        llm: Language model instance
        
    Returns:
        str: Generated summary
    """
    try:
        if not documents:
            return "❌ No content available to summarize."
        
        # Combine all content into a single text with reasonable length
        combined_content = ""
        for doc in documents:
            # Limit each document to prevent excessive length
            content = doc.page_content[:2000]  # Limit per document
            combined_content += f"\n\nSource: {doc.metadata.get('source', 'Unknown')}\n{content}"
        
        # Limit total content length to stay within API limits
        max_content_length = 8000  # Conservative limit for Gemini
        if len(combined_content) > max_content_length:
            combined_content = combined_content[:max_content_length] + "\n\n[Content truncated...]"
        
        # Create a single prompt for summarization
        prompt = f"""Based on the following web content about "{query}", provide a comprehensive summary:

{combined_content}

Please provide a clear, informative summary that answers the query "{query}" based on the above content."""
        
        # Make a single API call
        response = llm.invoke(prompt)
        return response.content
        
    except Exception as e:
        print(f"❌ Error generating summary: {e}")
        return f"❌ Error generating summary: {str(e)}"
