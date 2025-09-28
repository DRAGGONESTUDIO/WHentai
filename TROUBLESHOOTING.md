# Troubleshooting Guide

## Common Issues and Solutions

### 1. Empty or Few External URLs

**Problem**: The scraper returns few or no `external_url` values.

**Solutions**:
1. **Check detail page structure**: 
   - Visit a sample detail page URL from your `videos.json`
   - Inspect the HTML to see how external links are structured
   - Look for iframes, download buttons, or links to external domains

2. **Enable Playwright mode**:
   If the detail pages are JavaScript-heavy:
   ```python
   USE_PLAYWRIGHT = True
   ```
   Then install Playwright:
   ```bash
   pip install -r requirements-playwright.txt
   python -m playwright install
   ```

3. **Refine link extraction heuristics**:
   Share a sample detail page HTML so the extraction logic can be improved.

### 2. GitHub Actions Not Working

**Problem**: The automated scraping workflow fails.

**Solutions**:
1. **Check repository permissions**:
   - Ensure the repository allows workflows to push changes
   - Verify the `GITHUB_TOKEN` has appropriate permissions

2. **Playwright issues**:
   If using Playwright, ensure the workflow installs browsers:
   ```yaml
   - name: Install dependencies
     run: |
       python -m pip install --upgrade pip
       pip install -r requirements.txt
       pip install -r requirements-playwright.txt
       python -m playwright install
   ```

3. **Schedule timing**:
   Adjust the cron schedule if hourly is too aggressive:
   ```yaml
   # Daily at midnight
   - cron: "0 0 * * *"
   
   # Weekly on Sundays
   - cron: "0 0 * * 0"
   ```

### 3. Rate Limiting or Blocking

**Problem**: The scraper gets HTTP errors or empty responses.

**Solutions**:
1. **Increase delays**:
   ```python
   REQUEST_DELAY = (2.0, 4.0)  # Increase delay between requests
   ```

2. **Add proxy support**:
   ```python
   PROXIES = {
       "http": "http://user:pass@proxy:port",
       "https": "http://user:pass@proxy:port"
   }
   ```

3. **Rotate user agents**:
   Modify the `HEADERS` section to include a list of user agents and rotate them.

### 4. Incorrect External Links

**Problem**: The scraper picks wrong links sometimes.

**Solutions**:
1. **Tighten heuristics**:
   - Modify scoring rules in `extract_external_from_detail` function
   - Add specific domain filters to prefer certain video hosts
   - Add CSS selector preferences for specific link classes

2. **Add domain blacklists**:
   - Filter out known advertising or tracking domains
   - Prioritize links to known video hosting platforms

### 5. Missing Thumbnails

**Problem**: Thumbnail URLs are empty or broken.

**Solutions**:
1. **Check image attributes**:
   - Inspect the listing page HTML to see what attributes images use
   - Common attributes: `src`, `data-src`, `data-original`, `data-lazy`

2. **Add more attribute checks**:
   Modify the thumbnail extraction logic to check additional attributes.

## Testing Your Setup

### Manual Testing

1. **Test dependencies**:
   ```bash
   python -c "import requests; from bs4 import BeautifulSoup; print('Base dependencies OK')"
   ```

2. **Test Playwright (if used)**:
   ```bash
   python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
   ```

3. **Run a single iteration**:
   ```bash
   python cartoon_scraper.py
   ```

### Debugging the Scraper

1. **Add verbose logging**:
   Uncomment or add print statements to see what the scraper is doing:
   ```python
   print(f"Found {len(anchors)} anchor tags with images")
   print(f"Processing item: {title}")
   ```

2. **Save intermediate HTML**:
   For debugging parsing issues, save HTML to files:
   ```python
   with open('debug_listing.html', 'w', encoding='utf-8') as f:
       f.write(html)
   ```

## Next Steps

If you're still having issues after trying these solutions:

1. **Share sample data**:
   - Provide a sample `videos.json` entry
   - Share the HTML of a problematic detail page
   - Include any error messages from the console

2. **Request specific improvements**:
   - Describe the exact behavior you're seeing
   - Explain what you'd like to change
   - Provide examples of what the correct output should look like

The scraper is designed to be adaptable to different site structures, so with the right information, the extraction logic can be refined to work better with your specific use case.