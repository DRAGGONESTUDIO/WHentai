# Scraper Explanation & Usage Guide

## How the Scraper Finds Original Uploader Links

The scraping process works in two stages:

### Stage 1: Listing Page Scraping
1. The script fetches the listing page (`/popular`)
2. It finds all anchor (`<a>`) tags that contain an `<img>` element (thumbnails)
3. For each candidate, it extracts:
   - Title (from `alt` attribute, `title` attribute, or text content)
   - Thumbnail URL (from `src` or `data-src` attributes)
   - Detail page URL

### Stage 2: Detail Page Scraping
For each item, the scraper visits the detail page and:
1. Finds all `<a href>` tags with external domains (not the same as the base site)
2. Scores candidates based on these heuristics:
   - `target="_blank"` (+2 points)
   - `rel="nofollow"` (+1 point)
   - CSS classes containing "external", "download", "host", or "watch" (+2 points)
   - Text containing "watch", "video", "open", "play", or "download" (+2 points)
3. Selects the highest-scoring external link as the `external_url`

This heuristic approach works well for sites that link to external hosting pages. If the detail pages only embed players (iframes etc.), the extractor can be extended to also inspect `<iframe src="...">` and meta tags.

## GitHub Actions Workflow

The scraper can run automatically using GitHub Actions:

1. Scheduled runs every hour (configurable)
2. Manual triggering via GitHub UI
3. Automatically commits changes to `videos.json` if content has changed

To adjust the schedule, modify the cron expression:
```yaml
on:
  schedule:
    - cron: "0 * * * *" # every hour
```

For less frequent scraping, you might use:
- `"0 0 * * *"` - daily at midnight
- `"0 0 * * 0"` - weekly on Sundays

## Frontend & Linking Behavior

To display the scraped videos on your static site:

1. Read the `videos.json` file
2. For each video, create a card with a link that prefers the external URL:

```html
<a href="${video.external_url || video.detail_url}" target="_blank" rel="noopener noreferrer">
  <img src="${video.thumbnail}" alt="${video.title}">
  <div class="title">${video.title}</div>
</a>
```

This approach:
- Links directly to the original uploader when available
- Falls back to the detail page if no external URL was found
- Opens links in a new tab for better user experience
- Includes security attributes (`rel="noopener noreferrer"`)

## Troubleshooting & Next Steps

### Issue: JavaScript-heavy listing pages
If the listing page requires JavaScript to render properly:
1. Set `USE_PLAYWRIGHT = True` in the scraper script
2. Ensure Playwright is installed in the GitHub Actions workflow
3. The workflow already includes Playwright installation when the environment variable is set

### Issue: Few or no external_url values
If the scraper returns few or no external URLs:
1. Share an example detail page URL
2. The link extraction heuristics can be refined for that specific page structure
3. Alternative selectors can be implemented (e.g., for iframe-based embeds or specific download links)

### Issue: Wrong external links
If the scraper sometimes picks incorrect links:
1. The heuristics can be tightened to prefer specific patterns
2. Custom CSS selectors can be added for more precise targeting
3. Share a sample detail page HTML for refinement

## Manual Testing

To test the scraper manually:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the scraper:
   ```bash
   python cartoon_scraper.py
   ```

3. Check the output in `videos.json`

For Playwright mode:
1. Install additional dependencies:
   ```bash
   pip install -r requirements-playwright.txt
   python -m playwright install
   ```

2. Set `USE_PLAYWRIGHT = True` in the script
3. Run the scraper as above