"""
Example script demonstrating how to use the scraper.py module.
"""

from scraper import WebScraper

def main():
    # Initialize the scraper
    scraper = WebScraper(delay_range=(1, 2))
    
    try:
        # Example 1: Basic page scraping
        print("=== Basic Page Scraping ===")
        url = "https://httpbin.org/html"
        soup = scraper.get_page(url)
        
        if soup:
            # Extract the title
            title = scraper.extract_text(soup, "title")
            print(f"Page title: {title}")
            
            # Extract heading
            heading = scraper.extract_text(soup, "h1")
            print(f"Main heading: {heading}")
            
            # Extract paragraph text
            paragraph = scraper.extract_text(soup, "p")
            print(f"Paragraph text: {paragraph}")
        
        # Example 2: Link extraction
        print("\n=== Link Extraction ===")
        url = "https://httpbin.org/"
        soup = scraper.get_page(url)
        
        if soup:
            # Extract all links
            links = scraper.extract_links(soup, url)
            print(f"Found {len(links)} links")
            
            # Print first 5 links
            for link in links[:5]:
                print(f" - {link}")
                
        # Example 3: Attribute extraction
        print("\n=== Attribute Extraction ===")
        url = "https://httpbin.org/"
        soup = scraper.get_page(url)
        
        if soup:
            # Extract href attributes from links
            for i, link in enumerate(soup.select("a")[:3]):
                href = link.get("href", "")
                text = link.get_text(strip=True)
                print(f"Link {i+1}: {text} -> {href}")
                
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Always close the scraper to clean up resources
        scraper.close()

if __name__ == "__main__":
    main()