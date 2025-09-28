# WHentai Video Automation System

This document explains how to automatically add more videos to your WHentai website and keep it updated with recent content.

## Overview

The automation system consists of several components:

1. **Enhanced Scraper** - Scrapes from multiple sources to get more videos
2. **Automated Scraper** - Runs the enhanced scraper and updates categories
3. **GitHub Actions Workflow** - Automatically runs the scraper on a schedule
4. **Vercel Configuration** - Enables deployment and scheduled scraping on Vercel

## How It Works

### 1. Enhanced Scraper (`enhanced_scraper.py`)

This scraper collects videos from multiple sources:
- Popular videos (`/popular`)
- Latest videos (`/latest`)
- Top videos (`/top`)

Features:
- Scrapes from 3 different sources
- Collects metadata (duration, views, upload date)
- Adds timestamps for tracking when videos were scraped
- Avoids duplicates by tracking detail URLs

### 2. Automated Scraper (`automated_scraper.py`)

This script orchestrates the entire process:
- Runs the enhanced scraper
- Updates video categories using `add_category_tags.py`
- Tracks recent videos (last 24 hours)
- Generates scraping summaries

### 3. GitHub Actions (`scrape.yml`)

Automatically runs the scraper every 6 hours:
- Checks out the code
- Sets up Python environment
- Runs the automated scraper
- Commits and pushes new videos
- Reports status

### 4. Vercel Configuration (`vercel.json`)

Enables deployment on Vercel with:
- Python runtime setup
- API routes for videos and scraping
- Scheduled scraping (every 6 hours)

## Setup Instructions

### For GitHub Deployment

1. Push your code to a GitHub repository
2. The GitHub Actions workflow will automatically run every 6 hours
3. View scraping status at `https://your-repo-url/scraping_summary.json`

### For Vercel Deployment

1. Create a new project on Vercel
2. Connect your GitHub repository
3. Vercel will automatically detect the Flask app
4. The scraper will run automatically every 6 hours

## Manual Testing

To test the system manually:

```bash
# Test the basic scraper
python cartoon_scraper.py

# Test the enhanced scraper
python enhanced_scraper.py

# Test the automated scraper
python automated_scraper.py

# Run all tests
python test_scraper.py
```

## API Endpoints

When deployed, the following API endpoints are available:

- `GET /api/videos` - Get all videos
- `GET /api/stats` - Get video statistics
- `GET /api/status` - Get scraping status
- `GET /scrape` - Manually trigger scraping

## Customization

### Adjust Scraping Frequency

To change how often scraping occurs, modify the cron schedule in `.github/workflows/scrape.yml`:

```yaml
# Every hour
cron: "0 * * * *"

# Every 6 hours (current)
cron: "0 */6 * * *"

# Every day at midnight
cron: "0 0 * * *"
```

### Add More Sources

To add more scraping sources, modify the `SOURCES` list in `enhanced_scraper.py`:

```python
SOURCES = [
    "/popular",
    "/latest",
    "/top",
    "/trending",  # Add new source
    "/recommended"  # Add another source
]
```

### Adjust Limits

Modify these constants in `enhanced_scraper.py` to control scraping limits:

```python
MAX_ITEMS_PER_SOURCE = 2000  # Max items per source
MAX_PAGES_PER_SOURCE = 20    # Max pages per source
```

## Monitoring

The system generates status reports that you can monitor:

- `scraping_summary.json` - Contains scraping results
- GitHub Actions logs - View detailed run logs
- Vercel logs - View deployment and scraping logs

## Troubleshooting

### If Scraping Fails

1. Check the GitHub Actions logs for error messages
2. Verify the website structure hasn't changed
3. Test locally with `python test_scraper.py`

### If No New Videos Are Added

1. Check if the sources have new content
2. Verify the duplicate detection is working correctly
3. Increase the scraping frequency

### If Deployment Fails

1. Check Vercel logs for deployment errors
2. Ensure all required files are committed
3. Verify the `vercel.json` configuration is correct

## Best Practices

1. **Don't scrape too frequently** - This can overload the source website
2. **Monitor for changes** - Website structures can change over time
3. **Backup your data** - Regularly backup your `videos.json` file
4. **Check for duplicates** - The system avoids duplicates but it's good to verify
5. **Respect robots.txt** - Always follow the source website's terms of service

## Extending the System

You can extend this system by:

1. **Adding more sources** - Create scrapers for other websites
2. **Improving metadata extraction** - Add more detailed video information
3. **Adding filtering** - Filter videos by quality, language, etc.
4. **Adding notifications** - Send alerts when scraping completes
5. **Adding analytics** - Track video performance and user engagement

The system is designed to be modular and extensible, making it easy to add new features as needed.