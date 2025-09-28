# WHentai Project Summary

## Overview
This project scrapes adult cartoon videos from https://www.cartoonpornvideos.com and displays them in a web interface. The videos link directly to their original sources on external sites.

## Key Components

### 1. Web Scraper (`cartoon_scraper.py`)
- Successfully scrapes ~9,000 videos from cartoonpornvideos.com
- Extracts titles, thumbnails, detail URLs, and external URLs
- Saves data to `videos.json`
- Respects site resources with delays between requests
- Handles pagination to collect videos from multiple pages

### 2. Web Interface
- `index.html` - Main page with video listings
- `script.js` - Dynamic loading of videos from JSON
- `styles.css` - Responsive styling
- `app.py` - Flask web server to serve the interface

### 3. Batch Files
- `run_scraper.bat` - Runs the scraper
- `start_server.bat` - Starts the web server

### 4. Data File
- `videos.json` - Contains scraped video data (9,092 videos)

## How It Works

1. **Scraping**: The scraper extracts video information from cartoonpornvideos.com including:
   - Video titles
   - Thumbnail images
   - Detail page URLs
   - External URLs (links to original video sources)

2. **Data Storage**: All scraped data is saved to `videos.json` in JSON format

3. **Web Interface**: The Flask web server serves a responsive web interface that:
   - Loads video data from `videos.json`
   - Displays videos in a grid layout
   - Links each video to its original source
   - Provides sorting and filtering options

## Usage

1. **Scrape Videos**: Run `run_scraper.bat` or `python cartoon_scraper.py`
2. **Start Web Server**: Run `start_server.bat` or `python app.py`
3. **View Videos**: Open browser to http://localhost:8000

## Features

- Responsive web design that works on desktop and mobile
- Video thumbnails with titles and metadata
- Direct links to original video sources
- Sorting and filtering capabilities
- Error handling and logging
- Respectful scraping with delays between requests

## Technical Details

- Built with Python, Flask, BeautifulSoup4, and JavaScript
- Uses requests library for HTTP requests
- Implements proper error handling and logging
- Follows web scraping best practices
- Compatible with Windows (tested on Windows 24H2)

## Files

- `app.py` - Flask web server
- `cartoon_scraper.py` - Main scraper
- `videos.json` - Scraped video data
- `index.html` - Main web page
- `script.js` - Client-side JavaScript
- `styles.css` - CSS styling
- `run_scraper.bat` - Scraper launcher
- `start_server.bat` - Server launcher
- `README*.md` - Documentation files
- `requirements*.txt` - Dependency files