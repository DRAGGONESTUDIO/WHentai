# How to Add More Videos to Your WHentai Website

You currently have 60,120 videos on your WHentai website. Here are several ways to add even more videos:

## 1. Run the Enhanced Scraper Again

The enhanced scraper can find more videos from the same sources:

```bash
python enhanced_scraper.py
```

This will scrape from:
- https://www.cartoonpornvideos.com/popular
- And other sources that are working

## 2. Run the Maximum Videos Scraper

This combines multiple scraping strategies to get the most videos possible:

```bash
python max_videos_scraper.py
```

## 3. Run the Automated Scraper

This runs all available scrapers in sequence:

```bash
python automated_scraper.py
```

## 4. Schedule Automatic Scraping

To automatically add new videos on a regular basis, you can:

### For Windows:
Use Task Scheduler to run the scraper daily:
1. Open Task Scheduler
2. Create a new task
3. Set it to run `run_max_scraper.bat` daily

### For Linux/Mac:
Add a cron job to run the scraper daily:
```bash
# Add to crontab (crontab -e)
0 2 * * * cd /path/to/your/whentai && python max_videos_scraper.py
```

### For GitHub Actions:
The scraper is already set up to run automatically every 6 hours.

## 5. Manual Batch File Execution

You can also run the batch file for easy execution:

```bash
run_max_scraper.bat
```

## 6. Adding More Sources

If you want to add even more videos, you can:

1. Edit `enhanced_scraper.py` and add more sources to the `SOURCES` list
2. Create new scrapers for other websites
3. Modify the `MAX_ITEMS_PER_SOURCE` and `MAX_PAGES_PER_SOURCE` values to scrape more content

## Current Statistics

- Current video count: 60,120 videos
- Categories: Automatically tagged with relevant categories
- Recent videos: The scraper adds recent content automatically

## Best Practices

1. **Don't scrape too frequently** - This can overload the source website
2. **Monitor for duplicates** - The system automatically avoids duplicates
3. **Check for broken links** - Run the validation scripts periodically
4. **Backup your data** - Regularly backup your `videos.json` file

## Troubleshooting

If scraping stops working:
1. Check if the website structure has changed
2. Update the selectors in the scraper code
3. Check if the website is blocking requests (try using Playwright)
4. Verify your internet connection

## Monitoring New Additions

To see how many videos were added in the last run:
```bash
python -c "import json; data = json.load(open('videos.json', encoding='utf-8')); print(f'Current video count: {len(data)}')"
```

The system automatically tracks when each video was scraped in the `scraped_at` field.