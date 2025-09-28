#!/usr/bin/env python3
"""
Enhanced Scraper for multiple sources to add more videos to WHentai
Supports scraping from:
- https://www.cartoonpornvideos.com/popular
- https://www.cartoonpornvideos.com/recent
- https://www.cartoonpornvideos.com/trending
- https://www.cartoonpornvideos.com/most-viewed

Outputs: videos.json (list of objects with title, thumbnail, detail_url, external_url)
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time
import random
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime

# === CONFIG ===
BASE = "https://www.cartoonpornvideos.com"
SOURCES = [
    "/popular",      # Popular videos
    "/recent",       # Recent videos
    "/trending",     # Trending videos
    "/most-viewed"   # Most viewed videos
]
OUT_FILE = "videos.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WHentaiScraper/1.0; +https://yourdomain.example/)",
    "Accept-Language": "en-US,en;q=0.9"
}
REQUEST_DELAY = (0.5, 1.5)  # Delay between requests
TIMEOUT = 15  # HTTP timeout
MAX_ITEMS_PER_SOURCE = 5000  # Increased to get more videos per source
MAX_PAGES_PER_SOURCE = 50    # Increased to get more pages per source
USE_PLAYWRIGHT = False  # set True if pages require JS to render external links

# Add pagination support
MAX_PAGES = 100  # Increased from 5 to 100 for more pages

# Optional: use proxied requests (if required)
PROXIES = None
# PROXIES = {"http": "http://user:pass@host:port", "https": "http://user:pass@host:port"}

# === Helpers ===
def quiet_sleep():
    time.sleep(random.uniform(*REQUEST_DELAY))

def is_external_link(href):
    if not href:
        return False
    parsed = urlparse(href)
    if not parsed.netloc:
        return False
    return parsed.netloc.lower() not in (urlparse(BASE).netloc.lower(), "")

def make_absolute(href, base=BASE):
    if not href:
        return ""
    return urljoin(base, href)

# === Core scraping using requests + BS4 ===
def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, proxies=PROXIES)
    resp.raise_for_status()
    return resp.text

def parse_listing(html):
    """
    Parse listing pages and return a list of items with:
      - title
      - thumbnail (absolute URL)
      - detail_url (absolute)
      - duration
      - views
      - upload_date
    """
    soup = BeautifulSoup(html, "html.parser")
    items = []

    # Heuristic: find all cards/tiles linking to detail pages
    video_items = soup.select(".video-item, .item, .thumb, .video, .video-block")
    
    # If no specific video items found, try a more general approach
    if not video_items:
        anchors = soup.select("a")  # broad; we'll filter below
    else:
        anchors = []
        for item in video_items:
            # Find anchor tags within video items
            anchor = item.find("a")
            if anchor:
                anchors.append(anchor)

    seen = set()
    for a in anchors:
        img = a.find("img")
        href = None
        # Safely get href attribute
        try:
            from bs4 import Tag
            href = a.get('href') if isinstance(a, Tag) else None
        except:
            href = None
        if not img or not href:
            continue
            
        # Title heuristics: alt attribute or adjacent text
        title = ""
        # Safely get alt attribute from img
        try:
            from bs4 import Tag
            title = img.get('alt', '') if img and isinstance(img, Tag) else ""
        except:
            pass
        # If no alt, try title attribute from anchor
        if not title:
            try:
                from bs4 import Tag
                title = a.get('title', '') if a and isinstance(a, Tag) else ""
            except:
                pass
        # If still no title, get text content
        if not title:
            try:
                text_content = a.get_text() if hasattr(a, 'get_text') else ""
                title = text_content.strip() if text_content else ""
            except:
                pass
        if not title:
            # try parent container header text
            try:
                header = a.find_previous(["h3","h2","h4"])
                if header:
                    header_text = header.get_text() if hasattr(header, 'get_text') else ""
                    title = header_text.strip() if header_text else ""
            except:
                pass
        if not title:
            continue
            
        detail_url = make_absolute(href)
        thumbnail = ""
        # Safely get thumbnail attributes
        try:
            from bs4 import Tag
            thumbnail = img.get('src', '') if img and isinstance(img, Tag) else ""
        except:
            try:
                from bs4 import Tag
                thumbnail = img.get('data-src', '') if img and isinstance(img, Tag) else ""
            except:
                pass
        thumbnail = make_absolute(thumbnail, base=detail_url)
        title_str = str(title) if title else ""
        key = (title_str.strip(), detail_url)
        if key in seen:
            continue
        seen.add(key)
        
        # Try to extract additional metadata
        duration = ""
        views = ""
        upload_date = ""
        
        # Look for duration information
        duration_elem = a.find_next(class_=re.compile(r'duration|time', re.I))
        if duration_elem:
            duration_text = duration_elem.get_text().strip() if hasattr(duration_elem, 'get_text') else ""
            # Extract duration in format like "15:30" or "22 min"
            duration_match = re.search(r'(\d+:\d+|\d+\s*(?:min|minutes?))', duration_text)
            if duration_match:
                duration = duration_match.group(1)
        
        # Look for views information
        views_elem = a.find_next(class_=re.compile(r'views?|watched', re.I))
        if views_elem:
            views_text = views_elem.get_text().strip() if hasattr(views_elem, 'get_text') else ""
            # Extract views like "1.2M views" or "980K"
            views_match = re.search(r'([\d.,]+[KM]?)', views_text)
            if views_match:
                views = views_match.group(1)
        
        # Look for date information
        date_elem = a.find_next(class_=re.compile(r'date|timeago|uploaded', re.I))
        if date_elem:
            date_text = date_elem.get_text().strip() if hasattr(date_elem, 'get_text') else ""
            # Extract date information
            if date_text:
                upload_date = date_text
        
        items.append({
            "title": title_str.strip(),
            "thumbnail": thumbnail,
            "detail_url": detail_url,
            "duration": duration,
            "views": views,
            "upload_date": upload_date,
            "scraped_at": datetime.now().isoformat()  # Add timestamp when scraped
        })
        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break

    return items

def find_pagination_links(soup):
    """
    Find pagination links on the page.
    Returns a list of page URLs to scrape.
    """
    pagination_links = []
    
    # Look for common pagination patterns
    # Pattern 1: Links with numeric text
    for a in soup.select("a"):
        href = a.get('href')
        if not href:
            continue
            
        text = a.get_text().strip() if hasattr(a, 'get_text') else ""
        # Check if text is a number (page number)
        if text.isdigit() and int(text) > 1:
            abs_url = make_absolute(href)
            if abs_url not in pagination_links:
                pagination_links.append(abs_url)
                
    # Pattern 2: Links with "page" in URL
    for a in soup.select("a"):
        href = a.get('href')
        if not href:
            continue
            
        abs_url = make_absolute(href)
        if "page" in abs_url.lower() and abs_url not in pagination_links:
            pagination_links.append(abs_url)
            
    return pagination_links[:MAX_PAGES_PER_SOURCE-1]  # Don't include the first page, limit to MAX_PAGES

def extract_external_from_detail(detail_html, detail_url):
    """
    Given the HTML of a detail page, try to extract the original uploader/external link.
    """
    soup = BeautifulSoup(detail_html, "html.parser")
    
    # First, check for meta refresh redirect (common for these redirect pages)
    meta_refresh = soup.find("meta", attrs={"http-equiv": "refresh"})
    if meta_refresh:
        content = ""
        try:
            from bs4 import Tag
            content = meta_refresh.get('content', '') if isinstance(meta_refresh, Tag) else ""
        except:
            pass
        if content:
            # Extract URL from content like "0;url=https://example.com"
            url_match = re.search(r'url=([^;]+)', str(content), re.IGNORECASE)
            if url_match:
                redirect_url = url_match.group(1).strip()
                absolute_redirect = make_absolute(redirect_url, base=detail_url)
                if is_external_link(absolute_redirect):
                    return absolute_redirect
    
    # Collect candidate anchors
    candidates = []
    for a in soup.find_all("a", href=True):
        href = ""
        # Safely get href attribute
        try:
            from bs4 import Tag
            href = a.get('href', '') if isinstance(a, Tag) else ""
        except:
            pass
        href = str(href).strip() if href else ""
        if not href:
            continue
        absolute = make_absolute(href, base=detail_url)
        if is_external_link(absolute):
            score = 0
            # Safely check target attribute
            try:
                from bs4 import Tag
                if isinstance(a, Tag) and a.get('target', '') == "_blank":
                    score += 3
            except Exception:
                pass
            # Safely get rel attribute
            rel = []
            try:
                from bs4 import Tag
                if isinstance(a, Tag):
                    rel_attr = a.get('rel')
                    rel = rel_attr if isinstance(rel_attr, list) else []
            except:
                pass
            if isinstance(rel, list):
                if "nofollow" in rel:
                    score += 2
            # Safely get class attribute
            cls = ""
            try:
                from bs4 import Tag
                if isinstance(a, Tag):
                    class_attr = a.get('class')
                    cls = " ".join(class_attr) if isinstance(class_attr, list) else str(class_attr)
            except:
                pass
            if "external" in cls or "download" in cls or "host" in cls or "watch" in cls:
                score += 3
            # text-based heuristics
            text = ""
            try:
                text_content = a.get_text() if hasattr(a, 'get_text') else ""
                text = str(text_content).lower() if text_content else ""
            except:
                pass
            if any(k in text for k in ("watch", "video", "open", "play", "download", "continue", "click", "link")):
                score += 2
            candidates.append((score, absolute, text, str(a)))

    # sort by score desc
    if not candidates:
        # If no external links found, but the detail_url itself is external, return it
        if is_external_link(detail_url):
            return detail_url
        return ""
    candidates.sort(key=lambda x: x[0], reverse=True)
    # return highest-scoring link
    return candidates[0][1]

# === Optional Playwright-backed fetch for JS pages ===
def fetch_with_playwright(url):
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        raise RuntimeError("Playwright not installed. Install playwright and run `playwright install`") from e

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=HEADERS.get("User-Agent"))
        page.goto(url, timeout=30000)
        # wait for network idle or small delay
        page.wait_for_load_state("networkidle", timeout=15000)
        html = page.content()
        browser.close()
        return html

def main():
    print(f"Starting enhanced scraping from {len(SOURCES)} sources...")
    all_videos = []
    
    # Load existing videos if file exists
    if os.path.exists(OUT_FILE):
        try:
            with open(OUT_FILE, "r", encoding="utf-8") as f:
                all_videos = json.load(f)
            print(f"Loaded {len(all_videos)} existing videos from {OUT_FILE}")
        except Exception as e:
            print(f"Could not load existing videos: {e}")
            all_videos = []
    
    # Track processed URLs to avoid duplicates
    processed_urls = {video.get("detail_url") for video in all_videos if video.get("detail_url")}
    
    # Process each source
    for source_path in SOURCES:
        print(f"\n=== Scraping from {BASE}{source_path} ===")
        
        try:
            # Fetch the first page
            start_url = BASE + source_path
            print(f"Fetching {start_url}")
            
            if USE_PLAYWRIGHT:
                html = fetch_with_playwright(start_url)
            else:
                html = fetch_html(start_url)
                
            soup = BeautifulSoup(html, "html.parser")
            
            # Parse videos from the first page
            videos = parse_listing(html)
            print(f"Found {len(videos)} videos on the first page")
            
            # Add new videos, avoiding duplicates
            new_videos = 0
            for video in videos:
                detail_url = video.get("detail_url")
                if detail_url and detail_url not in processed_urls:
                    # Try to extract external URL if not already present
                    if not video.get("external_url"):
                        try:
                            print(f"Fetching detail page: {detail_url}")
                            if USE_PLAYWRIGHT:
                                detail_html = fetch_with_playwright(detail_url)
                            else:
                                detail_html = fetch_html(detail_url)
                            external_url = extract_external_from_detail(detail_html, detail_url)
                            video["external_url"] = external_url
                            print(f"Extracted external URL: {external_url}")
                        except Exception as e:
                            print(f"Could not fetch detail page for {detail_url}: {e}")
                            video["external_url"] = ""
                    
                    all_videos.append(video)
                    processed_urls.add(detail_url)
                    new_videos += 1
                    
                    # Add delay between requests
                    quiet_sleep()
            
            print(f"Added {new_videos} new videos from the first page")
            
            # Find pagination links
            pagination_links = find_pagination_links(soup)
            print(f"Found {len(pagination_links)} pagination links")
            
            # Process additional pages (limit to MAX_PAGES_PER_SOURCE)
            for page_url in pagination_links[:MAX_PAGES_PER_SOURCE-1]:
                if len(all_videos) >= MAX_ITEMS_PER_SOURCE * len(SOURCES):
                    break
                    
                print(f"Fetching {page_url}")
                try:
                    if USE_PLAYWRIGHT:
                        html = fetch_with_playwright(page_url)
                    else:
                        html = fetch_html(page_url)
                        
                    videos = parse_listing(html)
                    print(f"Found {len(videos)} videos on {page_url}")
                    
                    # Add new videos, avoiding duplicates
                    new_videos = 0
                    for video in videos:
                        detail_url = video.get("detail_url")
                        if detail_url and detail_url not in processed_urls:
                            # Try to extract external URL if not already present
                            if not video.get("external_url"):
                                try:
                                    print(f"Fetching detail page: {detail_url}")
                                    if USE_PLAYWRIGHT:
                                        detail_html = fetch_with_playwright(detail_url)
                                    else:
                                        detail_html = fetch_html(detail_url)
                                    external_url = extract_external_from_detail(detail_html, detail_url)
                                    video["external_url"] = external_url
                                    print(f"Extracted external URL: {external_url}")
                                except Exception as e:
                                    print(f"Could not fetch detail page for {detail_url}: {e}")
                                    video["external_url"] = ""
                            
                            all_videos.append(video)
                            processed_urls.add(detail_url)
                            new_videos += 1
                            
                            # Add delay between requests
                            quiet_sleep()
                            
                            # Check if we've reached the limit
                            if len(all_videos) >= MAX_ITEMS_PER_SOURCE * len(SOURCES):
                                break
                    
                    print(f"Added {new_videos} new videos from {page_url}")
                    
                except Exception as e:
                    print(f"Could not fetch {page_url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping {source_path}: {e}")
            continue
    
    # Save all videos to JSON file
    print(f"\nSaving {len(all_videos)} videos to {OUT_FILE}")
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_videos, f, ensure_ascii=False, indent=2)
    
    print("Done!")

if __name__ == "__main__":
    main()