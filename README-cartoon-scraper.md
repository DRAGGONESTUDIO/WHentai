# Cartoon Porn Videos Scraper

A Python scraper for https://www.cartoonpornvideos.com that extracts video information from both popular videos and categories, and outputs to a JSON file.

## Features

- Scrapes video titles, thumbnails, detail URLs, and external URLs
- Two modes:
  - DEFAULT: Fast, lightweight scraping using requests + BeautifulSoup
  - FALLBACK: JavaScript support using Playwright headless Chromium
- Respects site resources with configurable delays
- Deduplicates results
- Only updates output file when content changes

## Requirements

- Python 3.6+
- requests
- beautifulsoup4

Optional (for Playwright mode):
- playwright

## Installation

1. Install the required packages:
   ```bash
   pip install -r requirements-cartoon.txt
   ```

2. (Optional) For Playwright support:
   ```bash
   pip install playwright
   playwright install
   ```

## Usage

1. Run the scraper:
   ```bash
   python cartoon_porn_scraper.py
   ```

2. The output will be saved to `videos.json`

## Configuration

You can modify the behavior by editing the constants at the top of [cartoon_porn_scraper.py](file:///d%3A/Website%20Project/WHentai/cartoon_porn_scraper.py):

- `USE_PLAYWRIGHT`: Set to `True` to use Playwright instead of requests (for JavaScript-heavy sites)
- `MAX_ITEMS`: Maximum number of items to scrape (safety cap)
- `REQUEST_DELAY`: Delay between requests to be respectful to the server
- `TIMEOUT`: HTTP request timeout
- `PROXIES`: Proxy configuration if needed

## Output Format

The scraper outputs a JSON file with the following structure:

```json
[
  {
    "title": "Video Title",
    "thumbnail": "https://example.com/thumbnail.jpg",
    "detail_url": "https://www.cartoonpornvideos.com/video/12345/video-title",
    "external_url": "https://external-site.com/video.mp4"
  }
]
```

## Notes

- The scraper uses heuristics to extract information, which may need adjustment if the site structure changes
- External URLs are extracted based on heuristics (links with target="_blank", rel="nofollow", etc.)
- The scraper respects robots.txt and site resources with delays between requests
- For JavaScript-heavy sites, enable Playwright mode by setting `USE_PLAYWRIGHT = True`