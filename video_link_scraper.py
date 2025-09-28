#!/usr/bin/env python3
"""
Video Link Scraper for: https://www.cartoonpornvideos.com/
Purpose: Extract original video links and thumbnails for display on our website
Outputs: videos.json (list of objects with title, thumbnail, detail_url, external_url)
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re
from urllib.parse import urljoin, urlparse

# === CONFIG ===
BASE_URL = "https://www.cartoonpornvideos.com"
CATEGORY_PATH = "/categories"  # Main categories page
OUT_FILE = "videos.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}
REQUEST_DELAY = (1, 2)  # Delay between requests to be respectful
TIMEOUT = 15
MAX_VIDEOS = 5000  # Limit for testing

def quiet_sleep():
    """Sleep for a random amount of time to be respectful to the server"""
    time.sleep(random.uniform(*REQUEST_DELAY))

def make_absolute(href, base=BASE_URL):
    """Convert relative URLs to absolute URLs"""
    if not href:
        return ""
    return urljoin(base, href)

def is_external_link(href):
    """Check if a link is external (not from cartoonpornvideos.com)"""
    if not href:
        return False
    parsed = urlparse(href)
    if not parsed.netloc:
        return False
    return parsed.netloc.lower() not in (urlparse(BASE_URL).netloc.lower(), "")

def fetch_html(url):
    """Fetch HTML content from a URL"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_video_links_from_category(category_url):
    """Extract video links from a category page"""
    print(f"Scraping category: {category_url}")
    html = fetch_html(category_url)
    if not html:
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    videos = []
    
    # Find video items - look for containers with video links
    video_containers = soup.select("div.item, div.video-item, div.thumb, div.video")
    
    for container in video_containers:
        # Try to find the video link and thumbnail
        link_elem = container.find("a")
        if not link_elem:
            continue
            
        if link_elem:
            detail_url = getattr(link_elem, 'get', lambda x, default='': default)("href", "") if hasattr(link_elem, 'get') else ""
        else:
            detail_url = ""
        if not detail_url:
            continue
            
        # Make absolute URL
        detail_url = make_absolute(detail_url)
        
        # Find thumbnail
        thumbnail = ""
        img_elem = container.find("img")
        if img_elem:
            thumbnail = getattr(img_elem, 'get', lambda x, default='': default)("src", "") if hasattr(img_elem, 'get') else ""
            if not thumbnail:
                thumbnail = getattr(img_elem, 'get', lambda x, default='': default)("data-src", "") if hasattr(img_elem, 'get') else ""
            thumbnail = make_absolute(thumbnail, detail_url)
        
        # Find title
        title = ""
        img_elem = container.find("img")
        if img_elem and hasattr(img_elem, 'get'):
            alt_text = getattr(img_elem, 'get', lambda x, default='': default)("alt", "")
            if alt_text and isinstance(alt_text, str):
                title = alt_text.strip()
        else:
            # Try to get title from link text or nearby elements
            title_elem = container.find("h3") or container.find("h2") or container.find("p")
            if title_elem:
                title = title_elem.get_text().strip()
            else:
                title = link_elem.get_text().strip()
        
        if title and detail_url:
            videos.append({
                "title": title,
                "thumbnail": thumbnail,
                "detail_url": detail_url,
                "external_url": ""  # Will be filled later
            })
    
    return videos

def extract_external_link_from_detail(detail_url):
    """Extract the original video link from a detail page"""
    print(f"  Extracting external link from: {detail_url}")
    html = fetch_html(detail_url)
    if not html:
        return ""
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Look for meta refresh redirects (common pattern)
    meta_refresh = soup.find("meta", attrs={"http-equiv": "refresh"})
    if meta_refresh and hasattr(meta_refresh, 'get'):
        content = getattr(meta_refresh, 'get', lambda x, default='': default)("content", "")
        url_match = None
        if content and isinstance(content, str):
            url_match = re.search(r'url=([^;]+)', content, re.IGNORECASE)
        if url_match:
            redirect_url = url_match.group(1).strip()
            absolute_redirect = make_absolute(redirect_url, detail_url)
            if is_external_link(absolute_redirect):
                return absolute_redirect
    
    # Look for direct external links
    candidates = []
    for a in soup.find_all("a", href=True):
        href = getattr(a, 'get', lambda x, default='': default)("href", "") if hasattr(a, 'get') else ""
        if not href:
            continue
            
        absolute = make_absolute(href, detail_url)
        if is_external_link(absolute):
            # Score based on attributes that suggest it's the main video link
            score = 0
            target_attr = getattr(a, 'get', lambda x, default='': default)("target", "") if hasattr(a, 'get') else ""
            if target_attr == "_blank":
                score += 3
            rel_attr = getattr(a, 'get', lambda x, default=None: default)("rel", []) if hasattr(a, 'get') else []
            if rel_attr and isinstance(rel_attr, list) and "nofollow" in rel_attr:
                score += 2
            class_attr = getattr(a, 'get', lambda x, default=None: default)("class", None) if hasattr(a, 'get') else None
            class_list = []
            if class_attr:
                if isinstance(class_attr, list):
                    class_list = class_attr
                elif isinstance(class_attr, str):
                    class_list = class_attr.split()
            if any(cls in class_list for cls in ["external", "download", "watch", "play"]):
                score += 3
            
            text = a.get_text().lower()
            if any(keyword in text for keyword in ["watch", "video", "play", "continue", "click", "link"]):
                score += 2
                
            candidates.append((score, absolute))
    
    # Return highest scoring link
    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]
    
    # If no external links found but the detail_url itself is external, return it
    if is_external_link(detail_url):
        return detail_url
        
    return ""

def get_all_categories():
    """Get all category URLs from the main categories page"""
    print("Fetching categories...")
    html = fetch_html(BASE_URL + CATEGORY_PATH)
    if not html:
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    categories = []
    
    # Find category links
    category_links = soup.select("div.categories a, div.category a, a[href*='/category/']")
    
    for link in category_links:
        href = link.get("href")
        if href and "/category/" in href:
            category_url = make_absolute(href)
            if category_url not in categories:
                categories.append(category_url)
    
    print(f"Found {len(categories)} categories")
    return categories

def main():
    """Main scraping function"""
    print("Starting video link scraper for cartoonpornvideos.com")
    
    # Get all categories
    categories = get_all_categories()
    if not categories:
        print("No categories found, trying popular videos page")
        categories = [BASE_URL + "/popular"]
    
    all_videos = []
    
    # Scrape videos from each category
    for i, category_url in enumerate(categories[:10]):  # Limit to first 10 categories for testing
        print(f"\nProcessing category {i+1}/{len(categories[:10])}")
        videos = extract_video_links_from_category(category_url)
        print(f"  Found {len(videos)} videos")
        all_videos.extend(videos)
        
        # Respectful delay
        quiet_sleep()
        
        # Limit total videos
        if len(all_videos) >= MAX_VIDEOS:
            break
    
    # Remove duplicates based on detail_url
    unique_videos = []
    seen_urls = set()
    for video in all_videos:
        if video["detail_url"] not in seen_urls:
            seen_urls.add(video["detail_url"])
            unique_videos.append(video)
    
    print(f"\nTotal unique videos found: {len(unique_videos)}")
    
    # Extract external links for each video (limited for testing)
    print("\nExtracting external video links...")
    for i, video in enumerate(unique_videos[:100]):  # Limit to first 100 for testing
        print(f"Processing video {i+1}/{len(unique_videos[:100])}")
        external_url = extract_external_link_from_detail(video["detail_url"])
        video["external_url"] = external_url
        quiet_sleep()
    
    # Save to JSON file
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(unique_videos, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved {len(unique_videos)} videos to {OUT_FILE}")

if __name__ == "__main__":
    main()