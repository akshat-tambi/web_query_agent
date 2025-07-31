# Web scraper helper functions
import asyncio
from typing import List, Tuple
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from langchain.schema import Document

async def scrape_web_content(query: str, max_results: int = 5, search_engine: str = "bing") -> List[Tuple[str, str]]:
    """
    Scrape web content using Playwright
    
    Args:
        query: Search query
        max_results: Maximum number of URLs to scrape
        search_engine: Search engine to use ("bing", "google", "duckduckgo")
        
    Returns:
        List of (url, content) tuples
    """
    urls_and_content = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Configure search URL based on engine
            if search_engine.lower() == "google":
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                result_selector = "h3"
                link_selector = "a"
            else:  # Default to Bing
                search_url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
                result_selector = '.b_algo h2 a'
                link_selector = None
            
            await page.goto(search_url, wait_until="networkidle")
            
            # Wait for results to load
            await page.wait_for_selector(result_selector, timeout=10000)
            
            # Extract search result URLs
            if link_selector:  # Google case
                result_elements = await page.query_selector_all(result_selector)
                urls = []
                for element in result_elements[:max_results]:
                    parent_link = await element.query_selector('xpath=../../..//a[@href]')
                    if parent_link:
                        href = await parent_link.get_attribute('href')
                        if href and href.startswith('http') and search_engine not in href:
                            urls.append(href)
            else:  # Bing/DuckDuckGo case
                result_elements = await page.query_selector_all(result_selector)
                urls = []
                for element in result_elements[:max_results]:
                    href = await element.get_attribute('href')
                    if href and href.startswith('http') and search_engine not in href:
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

def generate_summary_with_langchain(documents: List[Document], query: str, llm, max_content_length: int = 8000) -> str:
    """
    Generate summary using a single API call to avoid rate limits
    
    Args:
        documents: List of documents to summarize
        query: Original query for context
        llm: Language model instance
        max_content_length: Maximum content length for API call
        
    Returns:
        str: Generated summary
    """
    try:
        if not documents:
            return "❌ No content available to summarize."
        
        # Combine all content into a single text with reasonable length
        combined_content = ""
        doc_limit = max_content_length // len(documents) if documents else 2000
        
        for doc in documents:
            # Limit each document proportionally
            content = doc.page_content[:doc_limit]
            source = doc.metadata.get('source', 'Unknown')
            combined_content += f"\n\nSource: {source}\n{content}"
        
        # Limit total content length to stay within API limits
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
