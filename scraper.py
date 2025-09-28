import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin, urlparse
import logging

# Optional Playwright support (uncomment USE_PLAYWRIGHT to enable)
USE_PLAYWRIGHT = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User agent to mimic a real browser
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

class WebScraper:
    def __init__(self, delay_range=(1, 3)):
        """
        Initialize the scraper with a delay range to be polite to servers.
        
        Args:
            delay_range (tuple): Min and max delay between requests in seconds
        """
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.delay_range = delay_range
        
        # Playwright components (only loaded if needed)
        self.playwright = None
        self.browser = None
        
    def get_page_with_requests(self, url, timeout=10):
        """
        Fetch a page using requests and BeautifulSoup.
        
        Args:
            url (str): URL to fetch
            timeout (int): Request timeout in seconds
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            logger.info(f"Fetching {url} with requests")
            time.sleep(random.uniform(*self.delay_range))
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url} with requests: {e}")
            return None
    
    def get_page_with_playwright(self, url, timeout=30000):
        """
        Fetch a page using Playwright (for JavaScript-heavy sites).
        
        Args:
            url (str): URL to fetch
            timeout (int): Request timeout in milliseconds
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            # Lazy import to avoid dependency issues if not needed
            from playwright.sync_api import sync_playwright
            
            logger.info(f"Fetching {url} with Playwright")
            
            # Initialize Playwright if not already done
            if not self.playwright:
                self.playwright = sync_playwright().start()
                self.browser = self.playwright.chromium.launch(headless=True)
            
            page = self.browser.new_page()
            page.set_default_timeout(timeout)
            page.goto(url)
            
            # Wait for page to load
            page.wait_for_load_state("networkidle")
            
            # Get page content
            content = page.content()
            page.close()
            
            return BeautifulSoup(content, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url} with Playwright: {e}")
            return None
    
    def get_page(self, url, timeout=30):
        """
        Fetch a page using either requests or Playwright.
        
        Args:
            url (str): URL to fetch
            timeout (int): Request timeout (seconds for requests, milliseconds for Playwright)
            
        Returns:
            BeautifulSoup object or None if failed
        """
        if USE_PLAYWRIGHT:
            return self.get_page_with_playwright(url, timeout * 1000)
        else:
            return self.get_page_with_requests(url, timeout)
    
    def extract_links(self, soup, base_url, link_selector="a"):
        """
        Extract all links from a page.
        
        Args:
            soup (BeautifulSoup): Parsed page content
            base_url (str): Base URL for resolving relative links
            link_selector (str): CSS selector for finding links
            
        Returns:
            list: List of absolute URLs
        """
        if not soup:
            return []
            
        links = []
        for link in soup.select(link_selector):
            href = link.get('href')
            if href:
                absolute_url = urljoin(base_url, href)
                links.append(absolute_url)
        return links
    
    def extract_text(self, soup, selector):
        """
        Extract text content using a CSS selector.
        
        Args:
            soup (BeautifulSoup): Parsed page content
            selector (str): CSS selector for the element
            
        Returns:
            str: Text content or empty string if not found
        """
        if not soup:
            return ""
            
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else ""
    
    def extract_attribute(self, soup, selector, attribute):
        """
        Extract an attribute value using a CSS selector.
        
        Args:
            soup (BeautifulSoup): Parsed page content
            selector (str): CSS selector for the element
            attribute (str): Attribute name to extract
            
        Returns:
            str: Attribute value or empty string if not found
        """
        if not soup:
            return ""
            
        element = soup.select_one(selector)
        return element.get(attribute, "") if element else ""
    
    def close(self):
        """Clean up resources."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

# Example usage
if __name__ == "__main__":
    scraper = WebScraper()
    
    try:
        # Example: scrape a page
        url = "https://example.com"
        soup = scraper.get_page(url)
        
        if soup:
            # Extract title
            title = scraper.extract_text(soup, "title")
            print(f"Page title: {title}")
            
            # Extract all links
            links = scraper.extract_links(soup, url)
            print(f"Found {len(links)} links")
            
            # Print first 5 links
            for link in links[:5]:
                print(f" - {link}")
    finally:
        scraper.close()