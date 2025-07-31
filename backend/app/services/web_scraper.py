"""
Web scraping service using Playwright
"""

import asyncio
from typing import List, Tuple, Optional
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class WebScraperService:
    """Service for web scraping operations"""
    
    def __init__(self):
        self.browser = None
        self.page = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def scrape_web_content(
        self, 
        query: str, 
        max_results: int = 5, 
        search_engine: str = "bing"
    ) -> List[Tuple[str, str, Optional[str]]]:
        """
        Scrape web content based on search query
        
        Args:
            query: Search query
            max_results: Maximum number of URLs to scrape
            search_engine: Search engine to use ("bing", "google", "duckduckgo")
            
        Returns:
            List of (url, content, title) tuples
        """
        urls_and_content = []
        
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
            
            await self.page.goto(search_url, wait_until="networkidle")
            
            # Wait for results to load
            await self.page.wait_for_selector(result_selector, timeout=10000)
            
            # Extract search result URLs
            urls = await self._extract_urls(result_selector, link_selector, search_engine, max_results)
            
            logger.info(f"Found {len(urls)} URLs to scrape")
            
            # Scrape content from each URL
            for i, url in enumerate(urls):
                try:
                    logger.info(f"Scraping {i+1}/{len(urls)}: {url[:60]}...")
                    
                    content, title = await self._scrape_url_content(url)
                    
                    if content and len(content) > 200:  # Only include substantial content
                        urls_and_content.append((url, content, title))
                    
                except Exception as e:
                    logger.error(f"Error scraping {url}: {str(e)[:50]}...")
                    continue
                    
        except Exception as e:
            logger.error(f"Error during web search: {e}")
            
        return urls_and_content
    
    async def _extract_urls(
        self, 
        result_selector: str, 
        link_selector: Optional[str], 
        search_engine: str, 
        max_results: int
    ) -> List[str]:
        """Extract URLs from search results"""
        urls = []
        
        if link_selector:  # Google case
            result_elements = await self.page.query_selector_all(result_selector)
            for element in result_elements[:max_results]:
                parent_link = await element.query_selector('xpath=../../..//a[@href]')
                if parent_link:
                    href = await parent_link.get_attribute('href')
                    if href and href.startswith('http') and search_engine not in href:
                        urls.append(href)
        else:  # Bing/DuckDuckGo case
            result_elements = await self.page.query_selector_all(result_selector)
            for element in result_elements[:max_results]:
                href = await element.get_attribute('href')
                if href and href.startswith('http') and search_engine not in href:
                    urls.append(href)
        
        return urls
    
    async def _scrape_url_content(self, url: str) -> Tuple[str, Optional[str]]:
        """Scrape content and title from a specific URL"""
        await self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
        
        # Extract HTML content
        html_content = await self.page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else None
        
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
        
        return clean_text, title


# Convenience function for standalone usage
async def scrape_web_content(
    query: str, 
    max_results: int = 5, 
    search_engine: str = "bing"
) -> List[Tuple[str, str, Optional[str]]]:
    """
    Standalone function to scrape web content
    """
    async with WebScraperService() as scraper:
        return await scraper.scrape_web_content(query, max_results, search_engine)
