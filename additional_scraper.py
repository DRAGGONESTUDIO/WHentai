#!/usr/bin/env python3
"""
Additional Scraper for WHentai - Focuses on specific categories to add more videos
This scraper targets specific categories to maximize video count
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
# Additional specific categories to scrape
SPECIFIC_CATEGORIES = [
    "/category/3d",
    "/category/hentai",
    "/category/manga",
    "/category/anime",
    "/category/toon",
    "/category/cartoon",
    "/category/big-tits",
    "/category/anal",
    "/category/blowjob",
    "/category/creampie",
    "/category/lesbian",
    "/category/bdsm",
    "/category/pov",
    "/category/gangbang",
    "/category/asian",
    "/category/bbw",
    "/category/teen",
    "/category/milf",
    "/category/amateur",
    "/category/compilation"
]

OUT_FILE = "videos.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WHentaiAdditionalScraper/1.0; +https://yourdomain.example/)",
    "Accept-Language": "en-US,en;q=0.9"
}
REQUEST_DELAY = (1.0, 2.0)  # Slightly longer delay to be respectful
TIMEOUT = 20  # Increased timeout
MAX_ITEMS_PER_CATEGORY = 2000  # Items per category
MAX_PAGES_PER_CATEGORY = 25    # Pages per category

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
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.text

def parse_category_page(html):
    """
    Parse category pages and return a list of items with metadata
    """
    soup = BeautifulSoup(html, "html.parser")
    items = []

    # Find video items using multiple selectors
    selectors = [
        ".video-item", ".item", ".thumb", ".video", ".video-block", 
        ".video-thumb", ".thumb-block", ".item-col"
    ]
    
    video_items = []
    for selector in selectors:
        items_found = soup.select(selector)
        if items_found:
            video_items.extend(items_found)
        if len(video_items) > 50:  # Stop if we found enough items
            break
    
    # If no specific video items found, try a more general approach
    if not video_items:
        anchors = soup.select("a[href*='/video/']")  # Look for video links specifically
    else:
        anchors = []
        for item in video_items:
            # Find anchor tags within video items
            anchor = item.find("a")
            if anchor and anchor.get('href'):
                anchors.append(anchor)
            # Also look for direct video links
            video_links = item.select("a[href*='/video/']")
            anchors.extend(video_links)

    seen = set()
    for a in anchors:
        href = a.get('href')
        if not href:
            continue
            
        img = a.find("img")
        if not img:
            # Try to find image in parent elements
            img = a.find_parent().find("img") if a.find_parent() else None
            
        # Title heuristics
        title = ""
        # Try alt attribute from img
        if img:
            title = img.get('alt', '')
        
        # Try title attribute from anchor
        if not title:
            title = a.get('title', '')
            
        # Try text content
        if not title:
            title = a.get_text().strip()
            
        # Try parent container header text
        if not title:
            header = a.find_previous(["h3", "h2", "h4"])
            if header:
                title = header.get_text().strip()
                
        if not title:
            continue
            
        detail_url = make_absolute(href)
        thumbnail = ""
        
        # Get thumbnail
        if img:
            thumbnail = img.get('src', '') or img.get('data-src', '')
        thumbnail = make_absolute(thumbnail, base=detail_url)
        
        title_str = str(title) if title else ""
        key = (title_str.strip(), detail_url)
        if key in seen:
            continue
        seen.add(key)
        
        # Extract metadata
        duration = ""
        views = ""
        upload_date = ""
        
        # Look for duration
        duration_elem = a.find_next(class_=re.compile(r'duration|time', re.I)) or a.find_parent().find(class_=re.compile(r'duration|time', re.I))
        if duration_elem:
            duration_text = duration_elem.get_text().strip()
            duration_match = re.search(r'(\d+:\d+|\d+\s*(?:min|minutes?))', duration_text)
            if duration_match:
                duration = duration_match.group(1)
        
        # Look for views
        views_elem = a.find_next(class_=re.compile(r'views?|watched', re.I)) or a.find_parent().find(class_=re.compile(r'views?|watched', re.I))
        if views_elem:
            views_text = views_elem.get_text().strip()
            views_match = re.search(r'([\d.,]+[KM]?)', views_text)
            if views_match:
                views = views_match.group(1)
        
        # Look for date
        date_elem = a.find_next(class_=re.compile(r'date|timeago|uploaded', re.I)) or a.find_parent().find(class_=re.compile(r'date|timeago|uploaded', re.I))
        if date_elem:
            upload_date = date_elem.get_text().strip()
        
        items.append({
            "title": title_str.strip(),
            "thumbnail": thumbnail,
            "detail_url": detail_url,
            "duration": duration,
            "views": views,
            "upload_date": upload_date,
            "scraped_at": datetime.now().isoformat()
        })
        
        if len(items) >= MAX_ITEMS_PER_CATEGORY:
            break

    return items

def find_category_pagination_links(soup):
    """
    Find pagination links on category pages
    """
    pagination_links = []
    
    # Look for pagination links
    for a in soup.select("a"):
        href = a.get('href')
        if not href:
            continue
            
        text = a.get_text().strip()
        abs_url = make_absolute(href)
        
        # Check if it's a pagination link
        if (("page" in href.lower() or re.match(r'^\d+$', text)) and 
            abs_url not in pagination_links and
            "category" in abs_url):
            pagination_links.append(abs_url)
    
    return pagination_links[:MAX_PAGES_PER_CATEGORY-1]

def extract_external_from_detail(detail_html, detail_url):
    """
    Extract external URL from detail page
    """
    soup = BeautifulSoup(detail_html, "html.parser")
    
    # Check for meta refresh redirect
    meta_refresh = soup.find("meta", attrs={"http-equiv": "refresh"})
    if meta_refresh:
        content = meta_refresh.get('content', '')
        if content:
            url_match = re.search(r'url=([^;]+)', str(content), re.IGNORECASE)
            if url_match:
                redirect_url = url_match.group(1).strip()
                absolute_redirect = make_absolute(redirect_url, base=detail_url)
                if is_external_link(absolute_redirect):
                    return absolute_redirect
    
    # Collect candidate anchors
    candidates = []
    for a in soup.find_all("a", href=True):
        href = str(a.get('href', '')).strip()
        if not href:
            continue
            
        absolute = make_absolute(href, base=detail_url)
        if is_external_link(absolute):
            score = 0
            # Score based on attributes
            if a.get('target', '') == "_blank":
                score += 3
            if "nofollow" in a.get('rel', []):
                score += 2
            cls = " ".join(a.get('class', []))
            if any(keyword in cls.lower() for keyword in ["external", "download", "host", "watch"]):
                score += 3
            text = a.get_text().lower()
            if any(keyword in text for keyword in ["watch", "video", "open", "play", "download", "continue", "click", "link"]):
                score += 2
            candidates.append((score, absolute, text))

    # Return highest-scoring link
    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]
    
    # If no external links found, but the detail_url itself is external, return it
    if is_external_link(detail_url):
        return detail_url
        
    return ""

def scrape_category(category_path):
    """
    Scrape a specific category
    """
    print(f"Scraping category: {category_path}")
    all_items = []
    
    try:
        # Fetch the first page
        start_url = BASE + category_path
        print(f"Fetching {start_url}")
        html = fetch_html(start_url)
        soup = BeautifulSoup(html, "html.parser")
        
        # Parse videos from the first page
        items = parse_category_page(html)
        print(f"Found {len(items)} videos on the first page")
        all_items.extend(items)
        
        # Find pagination links
        pagination_links = find_category_pagination_links(soup)
        print(f"Found {len(pagination_links)} pagination links")
        
        # Process additional pages
        for page_url in pagination_links[:MAX_PAGES_PER_CATEGORY-1]:
            if len(all_items) >= MAX_ITEMS_PER_CATEGORY:
                break
                
            print(f"Fetching {page_url}")
            try:
                html = fetch_html(page_url)
                items = parse_category_page(html)
                print(f"Found {len(items)} videos on {page_url}")
                all_items.extend(items)
                
                # Add delay between requests
                quiet_sleep()
                
            except Exception as e:
                print(f"Could not fetch {page_url}: {e}")
                continue
                
    except Exception as e:
        print(f"Error scraping category {category_path}: {e}")
    
    return all_items

def main():
    print(f"Starting additional scraping from {len(SPECIFIC_CATEGORIES)} categories...")
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
    
    # Process each category
    for category_path in SPECIFIC_CATEGORIES:
        print(f"\n=== Scraping category {category_path} ===")
        
        items = scrape_category(category_path)
        print(f"Total items found in category: {len(items)}")
        
        # Add new items, avoiding duplicates
        new_items = 0
        for item in items:
            detail_url = item.get("detail_url")
            if detail_url and detail_url not in processed_urls:
                # Try to extract external URL if not already present
                if not item.get("external_url"):
                    try:
                        print(f"Fetching detail page: {detail_url}")
                        detail_html = fetch_html(detail_url)
                        external_url = extract_external_from_detail(detail_html, detail_url)
                        item["external_url"] = external_url
                        print(f"Extracted external URL: {external_url}")
                    except Exception as e:
                        print(f"Could not fetch detail page for {detail_url}: {e}")
                        item["external_url"] = ""
                
                all_videos.append(item)
                processed_urls.add(detail_url)
                new_items += 1
                
                # Add delay between requests
                quiet_sleep()
        
        print(f"Added {new_items} new videos from category {category_path}")
        
        # Check if we've reached a reasonable limit
        if len(all_videos) >= len(SPECIFIC_CATEGORIES) * MAX_ITEMS_PER_CATEGORY:
            print("Reached maximum video limit, stopping...")
            break
    
    # Save all videos to JSON file
    print(f"\nSaving {len(all_videos)} videos to {OUT_FILE}")
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_videos, f, ensure_ascii=False, indent=2)
    
    print("Additional scraping completed!")
    print(f"Total videos in file: {len(all_videos)}")

if __name__ == "__main__":
    main()