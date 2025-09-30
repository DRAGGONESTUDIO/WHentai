# WHentai - Adult Video Aggregator

A web application that scrapes adult videos from https://www.example.com and displays them in a user-friendly interface.

For detailed information about this specific project, see [README-WHENTAI.md](README-WHENTAI.md).

## General Web Scraping Features

- Uses `requests` and `BeautifulSoup4` by default for lightweight scraping
- Optional `Playwright` support for JavaScript-heavy sites
- Built-in delay between requests to be respectful to servers
- User-agent spoofing to appear as a real browser
- Error handling and logging
- Resource cleanup

## Installation

1. Install the basic requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. (Optional) For Playwright support:
   ```bash
   pip install -r requirements-playwright.txt
   playwright install
   ```

## Usage

### Basic Usage

```python
from scraper import WebScraper

# Initialize the scraper
scraper = WebScraper(delay_range=(1, 3))  # Delay between 1-3 seconds

try:
    # Fetch a page
    soup = scraper.get_page("https://example.com")
    
    if soup:
        # Extract data
        title = scraper.extract_text(soup, "title")
        print(f"Title: {title}")
finally:
    # Clean up resources
    scraper.close()
```

### Enabling Playwright

To use Playwright instead of requests (for JavaScript-heavy sites):

1. Set `USE_PLAYWRIGHT = True` in `scraper.py`
2. Install Playwright dependencies (see Installation section)

### Extracting Data

The scraper provides helper methods for common extraction tasks:

```python
# Extract text content
title = scraper.extract_text(soup, "title")

# Extract links
links = scraper.extract_links(soup, base_url)

# Extract attribute values
src = scraper.extract_attribute(soup, "img", "src")
```

## Examples

See `example_scraper.py` for detailed usage examples.

## Configuration

- `delay_range`: Tuple of (min, max) seconds to delay between requests
- `USER_AGENT`: Browser user agent string
- `USE_PLAYWRIGHT`: Boolean flag to enable Playwright support

## Error Handling

The scraper includes basic error handling and logging. All exceptions are caught and logged, returning `None` when operations fail.
