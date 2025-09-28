#!/usr/bin/env python3
"""
Mega Scraper for WHentai - Adds tens of thousands of videos by using multiple sources and aggressive scraping
"""

import json
import time
import random
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import re

# List of additional sources to scrape from - expanded list for maximum video collection
ADDITIONAL_SOURCES = [
    "https://www.cartoonpornvideos.com/popular",
    "https://www.cartoonpornvideos.com/category/hentai",
    "https://www.cartoonpornvideos.com/category/manga",
    "https://www.cartoonpornvideos.com/category/animation",
    "https://www.cartoonpornvideos.com/category/anime",
    "https://www.cartoonpornvideos.com/category/toon",
    "https://www.cartoonpornvideos.com/category/cartoon",
    "https://www.cartoonpornvideos.com/category/big-tits",
    "https://www.cartoonpornvideos.com/category/small-tits",
    "https://www.cartoonpornvideos.com/category/big-ass",
    "https://www.cartoonpornvideos.com/category/small-ass",
    "https://www.cartoonpornvideos.com/category/blowjob",
    "https://www.cartoonpornvideos.com/category/anal",
    "https://www.cartoonpornvideos.com/category/creampie",
    "https://www.cartoonpornvideos.com/category/lesbian",
    "https://www.cartoonpornvideos.com/category/gangbang",
    "https://www.cartoonpornvideos.com/category/bdsm",
    "https://www.cartoonpornvideos.com/category/pov",
    "https://www.cartoonpornvideos.com/category/teen",
    "https://www.cartoonpornvideos.com/category/milf",
    "https://www.cartoonpornvideos.com/category/mom",
    "https://www.cartoonpornvideos.com/category/step-mom",
    "https://www.cartoonpornvideos.com/category/step-sister",
    "https://www.cartoonpornvideos.com/category/school",
    "https://www.cartoonpornvideos.com/category/office",
    "https://www.cartoonpornvideos.com/category/public",
    "https://www.cartoonpornvideos.com/category/outdoor",
    "https://www.cartoonpornvideos.com/category/beach",
    "https://www.cartoonpornvideos.com/category/bath",
    "https://www.cartoonpornvideos.com/category/shower",
    "https://www.cartoonpornvideos.com/category/bedroom",
    "https://www.cartoonpornvideos.com/category/kitchen",
    "https://www.cartoonpornvideos.com/category/car",
    "https://www.cartoonpornvideos.com/category/doctor",
    "https://www.cartoonpornvideos.com/category/nurse",
    "https://www.cartoonpornvideos.com/category/teacher",
    "https://www.cartoonpornvideos.com/category/student",
    "https://www.cartoonpornvideos.com/category/maid",
    "https://www.cartoonpornvideos.com/category/police",
    "https://www.cartoonpornvideos.com/category/military",
    "https://www.cartoonpornvideos.com/category/uniform",
    "https://www.cartoonpornvideos.com/category/costume",
    "https://www.cartoonpornvideos.com/category/fantasy",
    "https://www.cartoonpornvideos.com/category/supernatural",
    "https://www.cartoonpornvideos.com/category/sci-fi",
    "https://www.cartoonpornvideos.com/category/futuristic",
    "https://www.cartoonpornvideos.com/category/robot",
    "https://www.cartoonpornvideos.com/category/alien",
    "https://www.cartoonpornvideos.com/category/monster",
    "https://www.cartoonpornvideos.com/category/demon",
    "https://www.cartoonpornvideos.com/category/angel",
    "https://www.cartoonpornvideos.com/category/vampire",
    "https://www.cartoonpornvideos.com/category/zombie",
    "https://www.cartoonpornvideos.com/category/parody",
    "https://www.cartoonpornvideos.com/category/comedy",
    "https://www.cartoonpornvideos.com/category/romance",
    "https://www.cartoonpornvideos.com/category/action",
    "https://www.cartoonpornvideos.com/category/adventure",
    "https://www.cartoonpornvideos.com/category/horror",
    "https://www.cartoonpornvideos.com/category/thriller",
    "https://www.cartoonpornvideos.com/category/drama",
    "https://www.cartoonpornvideos.com/category/musical",
    "https://www.cartoonpornvideos.com/category/superhero",
    "https://www.cartoonpornvideos.com/category/sports",
    "https://www.cartoonpornvideos.com/category/fitness",
    "https://www.cartoonpornvideos.com/category/yoga",
    "https://www.cartoonpornvideos.com/category/dance",
    "https://www.cartoonpornvideos.com/category/music",
    "https://www.cartoonpornvideos.com/category/concert",
    "https://www.cartoonpornvideos.com/category/party",
    "https://www.cartoonpornvideos.com/category/club",
    "https://www.cartoonpornvideos.com/category/bar",
    "https://www.cartoonpornvideos.com/category/restaurant",
    "https://www.cartoonpornvideos.com/category/hotel",
    "https://www.cartoonpornvideos.com/category/cruise",
    "https://www.cartoonpornvideos.com/category/vacation",
    "https://www.cartoonpornvideos.com/category/travel",
    # Additional categories for even more videos
    "https://www.cartoonpornvideos.com/category/incest",
    "https://www.cartoonpornvideos.com/category/family",
    "https://www.cartoonpornvideos.com/category/brother",
    "https://www.cartoonpornvideos.com/category/sister",
    "https://www.cartoonpornvideos.com/category/father",
    "https://www.cartoonpornvideos.com/category/daughter",
    "https://www.cartoonpornvideos.com/category/aunt",
    "https://www.cartoonpornvideos.com/category/uncle",
    "https://www.cartoonpornvideos.com/category/cousin",
    "https://www.cartoonpornvideos.com/category/friend",
    "https://www.cartoonpornvideos.com/category/neighbor",
    "https://www.cartoonpornvideos.com/category/boss",
    "https://www.cartoonpornvideos.com/category/colleague",
    "https://www.cartoonpornvideos.com/category/teacher-student",
    "https://www.cartoonpornvideos.com/category/nurse-doctor",
    "https://www.cartoonpornvideos.com/category/police-officer",
    "https://www.cartoonpornvideos.com/category/military-soldier",
    "https://www.cartoonpornvideos.com/category/maid-servant",
    "https://www.cartoonpornvideos.com/category/secretary",
    "https://www.cartoonpornvideos.com/category/waitress",
    "https://www.cartoonpornvideos.com/category/shopkeeper",
    "https://www.cartoonpornvideos.com/category/customer",
    "https://www.cartoonpornvideos.com/category/celebrity",
    "https://www.cartoonpornvideos.com/category/superheroine",
    "https://www.cartoonpornvideos.com/category/villain",
    "https://www.cartoonpornvideos.com/category/villainess",
    "https://www.cartoonpornvideos.com/category/princess",
    "https://www.cartoonpornvideos.com/category/queen",
    "https://www.cartoonpornvideos.com/category/knight",
    "https://www.cartoonpornvideos.com/category/wizard",
    "https://www.cartoonpornvideos.com/category/witch",
    "https://www.cartoonpornvideos.com/category/fairy",
    "https://www.cartoonpornvideos.com/category/elf",
    "https://www.cartoonpornvideos.com/category/orc",
    "https://www.cartoonpornvideos.com/category/goblin",
    "https://www.cartoonpornvideos.com/category/dragon",
    "https://www.cartoonpornvideos.com/category/mermaid",
    "https://www.cartoonpornvideos.com/category/centaur",
    "https://www.cartoonpornvideos.com/category/furry",
    "https://www.cartoonpornvideos.com/category/animal",
    "https://www.cartoonpornvideos.com/category/dog",
    "https://www.cartoonpornvideos.com/category/cat",
    "https://www.cartoonpornvideos.com/category/horse",
    "https://www.cartoonpornvideos.com/category/cow",
    "https://www.cartoonpornvideos.com/category/pig",
    "https://www.cartoonpornvideos.com/category/fox",
    "https://www.cartoonpornvideos.com/category/wolf",
    "https://www.cartoonpornvideos.com/category/bear",
    "https://www.cartoonpornvideos.com/category/lion",
    "https://www.cartoonpornvideos.com/category/tiger",
    "https://www.cartoonpornvideos.com/category/leopard",
    "https://www.cartoonpornvideos.com/category/cheetah",
    "https://www.cartoonpornvideos.com/category/panther",
    "https://www.cartoonpornvideos.com/category/jaguar",
    "https://www.cartoonpornvideos.com/category/elephant",
    "https://www.cartoonpornvideos.com/category/giraffe",
    "https://www.cartoonpornvideos.com/category/monkey",
    "https://www.cartoonpornvideos.com/category/gorilla",
    "https://www.cartoonpornvideos.com/category/chimpanzee",
    "https://www.cartoonpornvideos.com/category/bird",
    "https://www.cartoonpornvideos.com/category/eagle",
    "https://www.cartoonpornvideos.com/category/owl",
    "https://www.cartoonpornvideos.com/category/penguin",
    "https://www.cartoonpornvideos.com/category/duck",
    "https://www.cartoonpornvideos.com/category/chicken",
    "https://www.cartoonpornvideos.com/category/fish",
    "https://www.cartoonpornvideos.com/category/shark",
    "https://www.cartoonpornvideos.com/category/dolphin",
    "https://www.cartoonpornvideos.com/category/whale",
    "https://www.cartoonpornvideos.com/category/octopus",
    "https://www.cartoonpornvideos.com/category/squid",
    "https://www.cartoonpornvideos.com/category/alien-abduction",
    "https://www.cartoonpornvideos.com/category/spaceship",
    "https://www.cartoonpornvideos.com/category/time-travel",
    "https://www.cartoonpornvideos.com/category/portal"
]

# Increase maximum number of pages to scrape per category for more videos
MAX_PAGES_PER_CATEGORY = 30

# Headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

def get_video_data_from_page(url):
    """Extract video data from a page"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        videos = []
        
        # Find all video items
        video_items = []
        try:
            video_items = soup.find_all('div', class_='card sub group')
        except Exception:
            pass
        
        for item in video_items:
            # Extract title
            title = "Untitled"
            try:
                find_method = getattr(item, 'find', None)
                if find_method:
                    title_elem = find_method('a', {'class': 'item-title item-link rate-link font-medium'})
                    if title_elem:
                        get_text_method = getattr(title_elem, 'get_text', None)
                        if get_text_method:
                            title = get_text_method(strip=True)
            except Exception:
                pass
            
            # Extract thumbnail
            thumbnail = ""
            try:
                find_method = getattr(item, 'find', None)
                if find_method:
                    thumb_elem = find_method('img', {'class': 'item-image'})
                    if thumb_elem:
                        get_method = getattr(thumb_elem, 'get', None)
                        if get_method:
                            src = get_method('src')
                            if src:
                                thumbnail = src
            except Exception:
                pass
            
            # Extract detail URL
            detail_url = ""
            try:
                find_method = getattr(item, 'find', None)
                if find_method:
                    link_elem = find_method('a', {'class': 'item-title item-link rate-link font-medium'})
                    if link_elem:
                        get_method = getattr(link_elem, 'get', None)
                        if get_method:
                            href = get_method('href')
                            if href:
                                detail_url = href
            except Exception:
                pass
            
            # Extract categories (if available)
            categories = []
            try:
                find_all_method = getattr(item, 'find_all', None)
                if find_all_method:
                    cat_elems = find_all_method('a', {'class': 'item-source block text-xsm'})
                    for cat in cat_elems:
                        get_text_method = getattr(cat, 'get_text', None)
                        if get_text_method:
                            cat_text = get_text_method(strip=True)
                            if cat_text and cat_text not in categories:
                                categories.append(cat_text)
            except Exception:
                pass
            
            # Only add videos with essential data
            if title and thumbnail and detail_url:
                videos.append({
                    "title": title,
                    "thumbnail": thumbnail,
                    "detail_url": detail_url,
                    "external_url": "",  # Will be populated later if needed
                    "categories": categories
                })
                    
        return videos
        
    except Exception as e:
        print(f"Error fetching page {url}: {e}")
        return []

def scrape_category(url, max_pages=MAX_PAGES_PER_CATEGORY):
    """Scrape all pages of a category"""
    all_videos = []
    
    for page in range(1, max_pages + 1):
        page_url = f"{url}?page={page}" if page > 1 else url
        print(f"Scraping page {page} of {url}")
        
        videos = get_video_data_from_page(page_url)
        if not videos:
            print(f"No more videos found on page {page}, stopping")
            break
            
        all_videos.extend(videos)
        print(f"Found {len(videos)} videos on page {page}")
        
        # Be respectful to the server - increase delay to handle rate limiting
        time.sleep(random.uniform(3, 6))
    
    return all_videos

def load_existing_videos(filepath="videos.json"):
    """Load existing videos from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error loading existing videos: {e}")
        return []

def save_videos(videos, filepath="videos.json"):
    """Save videos to JSON file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(videos, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(videos)} videos to {filepath}")
    except Exception as e:
        print(f"Error saving videos: {e}")

def remove_duplicates(videos):
    """Remove duplicate videos based on title, thumbnail, detail_url, and external_url"""
    seen = set()
    unique_videos = []
    
    for video in videos:
        # Create a unique key based on title, thumbnail, detail_url, and external_url
        detail_url = video.get('detail_url', '') or ''
        external_url = video.get('external_url', '') or ''
        key = f"{video['title']}|{video['thumbnail']}|{detail_url}|{external_url}"
        if key not in seen:
            seen.add(key)
            unique_videos.append(video)
    
    return unique_videos

def remove_title_duplicates(videos):
    """Remove videos with duplicate titles (more aggressive deduplication)"""
    seen_titles = set()
    unique_videos = []
    
    for video in videos:
        title = video.get('title', '').strip().lower()
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_videos.append(video)
    
    return unique_videos

def main():
    """Main function to run the mega scraper"""
    print("Starting WHentai Mega Scraper")
    print(f"Will scrape from {len(ADDITIONAL_SOURCES)} categories")
    print(f"Will scrape up to {MAX_PAGES_PER_CATEGORY} pages per category")
    
    # Load existing videos
    existing_videos = load_existing_videos()
    print(f"Loaded {len(existing_videos)} existing videos")
    
    # Create a set of existing video keys for duplicate checking
    existing_keys = set()
    for video in existing_videos:
        detail_url = video.get('detail_url', '') or ''
        external_url = video.get('external_url', '') or ''
        key = f"{video['title']}|{video['thumbnail']}|{detail_url}|{external_url}"
        existing_keys.add(key)
    
    # Scrape from all sources
    all_new_videos = []
    
    # Use ThreadPoolExecutor for concurrent scraping - reduce workers to avoid rate limiting
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit all scraping tasks
        future_to_url = {
            executor.submit(scrape_category, url): url 
            for url in ADDITIONAL_SOURCES
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                videos = future.result()
                print(f"Completed scraping {url}: {len(videos)} videos")
                all_new_videos.extend(videos)
            except Exception as e:
                print(f"Error scraping {url}: {e}")
    
    # Remove duplicates from new videos
    unique_new_videos = remove_duplicates(all_new_videos)
    print(f"Found {len(unique_new_videos)} unique new videos (first deduplication)")
    
    # Apply more aggressive deduplication by title
    title_unique_videos = remove_title_duplicates(unique_new_videos)
    print(f"Found {len(title_unique_videos)} unique new videos (title deduplication)")
    
    # Filter out videos that already exist
    truly_new_videos = []
    for video in title_unique_videos:
        detail_url = video.get('detail_url', '') or ''
        external_url = video.get('external_url', '') or ''
        key = f"{video['title']}|{video['thumbnail']}|{detail_url}|{external_url}"
        if key not in existing_keys:
            truly_new_videos.append(video)
            existing_keys.add(key)  # Add to set to prevent internal duplicates
    
    print(f"Found {len(truly_new_videos)} truly new videos")
    
    # Combine existing and new videos
    all_videos = existing_videos + truly_new_videos
    
    # Remove any remaining duplicates with both methods
    final_videos = remove_duplicates(all_videos)
    final_videos = remove_title_duplicates(final_videos)
    print(f"Final video count: {len(final_videos)} (was {len(all_videos)} before deduplication)")
    
    # Save to file
    save_videos(final_videos)
    
    print("Mega scraping completed!")
    print(f"Added {len(truly_new_videos)} new videos")
    print(f"Total videos: {len(final_videos)}")

if __name__ == "__main__":
    main()