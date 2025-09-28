# Functional WHentai Website

A complete, functioning website that scrapes video content from https://www.cartoonpornvideos.com/popular and displays it on a responsive frontend.

## Features

1. **Automated Scraping**: Python scraper that extracts video titles, thumbnails, detail URLs, and external URLs
2. **Responsive Website**: Modern HTML/CSS/JavaScript frontend similar to Hanime
3. **Admin Panel**: Control panel to manually trigger scraping and view statistics
4. **Real-time Data**: Website displays real scraped data from cartoonpornvideos.com
5. **Proper Linking**: Videos link to external sources with fallback to detail pages

## How It Works

### 1. Scraping Process
The Python scraper ([cartoon_scraper.py](file://d%3A/Website%20Project/WHentai/cartoon_scraper.py)) extracts data from https://www.cartoonpornvideos.com/popular:
- Fetches the listing page
- Extracts video titles, thumbnails, and detail page URLs
- Visits each detail page to find external URLs
- Saves data to [videos.json](file://d%3A/Website%20Project/WHentai/videos.json)

### 2. Website Display
The frontend ([index.html](file://d%3A/Website%20Project/WHentai/index.html)) displays the scraped videos:
- Loads video data from [videos.json](file://d%3A/Website%20Project/WHentai/videos.json)
- Creates responsive video cards with thumbnails
- Links to external URLs when available, with fallback to detail pages

### 3. Admin Panel
The admin panel ([admin.html](file://d%3A/Website%20Project/WHentai/admin.html)) provides:
- Manual scraping trigger
- Video statistics
- Recent videos display

## Setup Instructions

### Prerequisites
- Python 3.6+
- pip (Python package installer)

### Installation
1. Install required packages:
   ```bash
   pip install -r requirements.txt
   pip install flask
   ```

2. Run the scraper to get initial data:
   ```bash
   python cartoon_scraper.py
   ```

3. Start the web server:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to:
   - Main website: http://localhost:8000
   - Admin panel: http://localhost:8000/admin.html

## File Structure

```
WHentai/
├── app.py              # Flask web application
├── cartoon_scraper.py  # Video scraping script
├── videos.json         # Scraped video data
├── index.html          # Main website page
├── admin.html          # Admin panel page
├── styles.css          # Website styling
├── script.js           # Main website JavaScript
├── admin.js            # Admin panel JavaScript
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Usage

### Viewing Videos
1. Visit http://localhost:8000
2. Browse trending and latest videos
3. Click on any video to be redirected to the external source

### Updating Video Data
1. Visit http://localhost:8000/admin.html
2. Click "Run Scraper" to fetch new videos
3. View updated statistics and recent videos

### Automatic Scraping
The scraper can be run automatically using cron jobs or task schedulers:
```bash
# Run every hour
0 * * * * cd /path/to/WHentai && python cartoon_scraper.py
```

## Customization

### Website Title
The website uses "Kerrico" as the title (as per user preference).

### Styling
Modify [styles.css](file://d%3A/Website%20Project/WHentai/styles.css) to change colors, fonts, and layouts.

### Scraper Configuration
Edit [cartoon_scraper.py](file://d%3A/Website%20Project/WHentai/cartoon_scraper.py) to adjust:
- Request delays
- Maximum items to scrape
- User agent
- Proxy settings

## Technical Details

### Data Format
Videos are stored in [videos.json](file://d%3A/Website%20Project/WHentai/videos.json) with the following structure:
```json
{
  "title": "Video Title",
  "thumbnail": "https://example.com/thumbnail.jpg",
  "detail_url": "https://www.cartoonpornvideos.com/video/12345/video-title",
  "external_url": "https://external-site.com/video.mp4"
}
```

### Link Handling
The frontend follows the user's preference for automated embedding:
- Links to `external_url` when available
- Falls back to `detail_url` when `external_url` is missing
- Opens all links in new tabs for better user experience

### Responsive Design
The website is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

## Troubleshooting

### Scraper Issues
If the scraper fails:
1. Check internet connection
2. Verify the source website is accessible
3. Check for CAPTCHA or blocking
4. Adjust request delays in the scraper

### Website Issues
If the website doesn't display videos:
1. Ensure [videos.json](file://d%3A/Website%20Project/WHentai/videos.json) exists and contains data
2. Check browser console for JavaScript errors
3. Verify the web server is running

## Security Notes

This is a development server only. For production use:
- Use a proper web server (Apache, Nginx, etc.)
- Implement proper authentication for admin panel
- Add rate limiting for scraping
- Use HTTPS for secure connections