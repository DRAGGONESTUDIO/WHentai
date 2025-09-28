# WHentai - Adult Cartoon Video Aggregator

A web application that scrapes adult cartoon videos from https://www.cartoonpornvideos.com and displays them in a user-friendly interface.

## Features

- Scrapes video titles, thumbnails, and external links from cartoonpornvideos.com
- Displays videos in a responsive web interface
- Links to original video sources
- Categorizes and sorts videos
- Responsive design for all devices

## Project Structure

- `app.py` - Flask web server
- `cartoon_scraper.py` - Main scraper for cartoonpornvideos.com
- `videos.json` - Scraped video data in JSON format
- `index.html` - Main web page
- `script.js` - JavaScript for dynamic content loading
- `styles.css` - Styling for the web interface
- `run_scraper.bat` - Batch file to run the scraper
- `start_server.bat` - Batch file to start the web server

## Installation

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. (Optional) For Playwright support:
   ```bash
   pip install -r requirements-playwright.txt
   playwright install
   ```

## Usage

### Scraping Videos

To scrape videos from cartoonpornvideos.com:

1. Run the scraper:
   ```bash
   python cartoon_scraper.py
   ```
   
   Or double-click `run_scraper.bat`

2. The scraper will:
   - Extract video information from the site
   - Save data to `videos.json`
   - Display progress and results

### Running the Web Server

To view the scraped videos in a web interface:

1. Start the web server:
   ```bash
   python app.py
   ```
   
   Or double-click `start_server.bat`

2. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

## Configuration

The scraper can be configured by modifying constants in `cartoon_scraper.py`:

- `USE_PLAYWRIGHT`: Set to `True` to use Playwright instead of requests (for JavaScript-heavy sites)
- `MAX_ITEMS`: Maximum number of items to scrape (safety cap)
- `REQUEST_DELAY`: Delay between requests to be respectful to the server
- `TIMEOUT`: HTTP request timeout
- `PROXIES`: Proxy configuration if needed

## Data Format

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

- The scraper respects robots.txt and site resources with delays between requests
- For JavaScript-heavy sites, enable Playwright mode by setting `USE_PLAYWRIGHT = True`
- The web interface loads videos dynamically from `videos.json`
- Videos link directly to their original sources on external sites