#!/usr/bin/env python3
"""
Comprehensive Scraper for WHentai
This scraper attempts to gather videos from multiple sources to maximize the video count.
"""

import json
import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

# List of categories to scrape
CATEGORIES = [
    'hentai', '3d', 'anime', 'cartoon', 'toon', 'manga', 'animation',
    'porn', 'sex', 'fuck', 'boobs', 'tits', 'ass', 'pussy', 'cock',
    'dick', 'cum', 'orgy', 'gangbang', 'fetish', 'bdsm', 'bondage',
    'schoolgirl', 'teacher', 'milf', 'housewife', 'office', 'public',
    'outdoor', 'beach', 'pool', 'bath', 'shower', 'bathroom', 'bedroom',
    'kitchen', 'living-room', 'hotel', 'hospital', 'doctor', 'nurse',
    'police', 'uniform', 'cosplay', 'maid', 'secretary', 'student',
    'lesbian', 'gay', 'bisexual', 'transgender', 'shemale', 'lgbt',
    'interracial', 'black', 'asian', 'japanese', 'chinese', 'korean',
    'american', 'european', 'latina', 'ebony', 'white', 'redhead',
    'blonde', 'brunette', 'big-tits', 'small-tits', 'huge-tits',
    'big-ass', 'small-ass', 'huge-ass', 'big-cock', 'small-cock',
    'huge-cock', 'fat', 'thin', 'slim', 'curvy', 'pregnant',
    'mature', 'old', 'young', 'teen', 'college', 'university',
    'high-school', 'middle-school', 'elementary', 'kindergarten'
]

# Base URL for scraping
BASE_URL = "https://www.cartoonpornvideos.com"

# Headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

def load_existing_videos():
    """Load existing videos from videos.json"""
    try:
        with open('videos.json', 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content.endswith(','):
                content = content[:-1] + ']'
            data = json.loads(content)
            return {video.get('id'): video for video in data}
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print(f"Error loading videos.json: {e}")
        return {}

def save_videos(videos):
    """Save videos to videos.json"""
    try:
        with open('videos.json', 'w', encoding='utf-8') as f:
            json.dump(list(videos.values()), f, indent=2, ensure_ascii=False)
        print(f"Saved {len(videos)} videos to videos.json")
    except Exception as e:
        print(f"Error saving videos: {e}")

def get_page(url, retries=3):
    """Fetch a page with retry logic"""
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Error fetching {url} (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return None

def extract_video_info(video_element, base_url):
    """Extract video information from a video element"""
    try:
        # Extract title
        title_element = video_element.find('h3') or video_element.find('h2') or video_element.find('a')
        title = title_element.get_text(strip=True) if title_element else "Unknown Title"
        
        # Extract URL
        link_element = video_element.find('a')
        if link_element and link_element.get('href'):
            url = urljoin(base_url, link_element['href'])
        else:
            url = "#"
        
        # Extract thumbnail
        thumb_element = video_element.find('img')
        thumbnail = thumb_element.get('src') or thumb_element.get('data-src') if thumb_element else ""
        if thumbnail:
            thumbnail = urljoin(base_url, thumbnail)
        
        # Extract duration if available
        duration = ""
        duration_element = video_element.find('span', class_='duration') or video_element.find('div', class_='duration')
        if duration_element:
            duration = duration_element.get_text(strip=True)
        
        # Extract views if available
        views = ""
        views_element = video_element.find('span', class_='views') or video_element.find('div', class_='views')
        if views_element:
            views = views_element.get_text(strip=True)
        
        # Create a unique ID based on URL or title
        video_id = url.split('/')[-1] if url != "#" and url else title.replace(' ', '-').lower()
        
        return {
            'id': video_id,
            'title': title,
            'url': url,
            'thumbnail': thumbnail,
            'duration': duration,
            'views': views,
            'detail_url': url,
            'external_url': url
        }
    except Exception as e:
        print(f"Error extracting video info: {e}")
        return None

def scrape_category(category, existing_videos, max_pages=5):
    """Scrape a specific category"""
    print(f"Scraping category: {category}")
    new_videos = {}
    
    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}/category/{category}?page={page}"
        print(f"Fetching page {page}: {url}")
        
        response = get_page(url)
        if not response:
            print(f"Failed to fetch page {page} for category {category}")
            continue
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find video elements (adjust selectors based on actual site structure)
        video_elements = soup.find_all('div', class_='video-item') or \
                         soup.find_all('div', class_='item') or \
                         soup.find_all('div', class_='thumb') or \
                         soup.find_all('li', class_='video') or \
                         soup.find_all('article')
        
        if not video_elements:
            # Try alternative selectors
            video_elements = soup.find_all('a', href=lambda x: x and '/video/' in x)
        
        if not video_elements:
            print(f"No video elements found on page {page}")
            break
            
        print(f"Found {len(video_elements)} video elements on page {page}")
        
        for video_element in video_elements:
            video_info = extract_video_info(video_element, BASE_URL)
            if video_info and video_info['id'] and video_info['id'] not in existing_videos and video_info['id'] not in new_videos:
                # Only add if it's not already in existing videos or new videos
                new_videos[video_info['id']] = video_info
                print(f"Added new video: {video_info['title']}")
        
        # Add a delay to be respectful to the server
        time.sleep(random.uniform(1, 3))
    
    return new_videos

def scrape_popular(existing_videos, max_pages=5):
    """Scrape popular videos"""
    print("Scraping popular videos")
    new_videos = {}
    
    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}/popular?page={page}" if page > 1 else f"{BASE_URL}/popular"
        print(f"Fetching popular page {page}: {url}")
        
        response = get_page(url)
        if not response:
            print(f"Failed to fetch popular page {page}")
            continue
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find video elements
        video_elements = soup.find_all('div', class_='video-item') or \
                         soup.find_all('div', class_='item') or \
                         soup.find_all('div', class_='thumb') or \
                         soup.find_all('li', class_='video') or \
                         soup.find_all('article')
        
        if not video_elements:
            video_elements = soup.find_all('a', href=lambda x: x and '/video/' in x)
        
        if not video_elements:
            print(f"No video elements found on popular page {page}")
            break
            
        print(f"Found {len(video_elements)} video elements on popular page {page}")
        
        for video_element in video_elements:
            video_info = extract_video_info(video_element, BASE_URL)
            if video_info and video_info['id'] and video_info['id'] not in existing_videos and video_info['id'] not in new_videos:
                new_videos[video_info['id']] = video_info
                print(f"Added new popular video: {video_info['title']}")
        
        time.sleep(random.uniform(1, 3))
    
    return new_videos

def main():
    """Main function to run the comprehensive scraper"""
    print("=== WHentai Comprehensive Scraper ===")
    
    # Load existing videos
    existing_videos = load_existing_videos()
    print(f"Loaded {len(existing_videos)} existing videos")
    
    # Dictionary to store all new videos
    all_new_videos = {}
    
    # Scrape popular videos
    popular_videos = scrape_popular(existing_videos, max_pages=3)
    all_new_videos.update(popular_videos)
    print(f"Found {len(popular_videos)} new popular videos")
    
    # Scrape categories
    for category in CATEGORIES[:10]:  # Limit to first 10 categories to avoid overwhelming
        category_videos = scrape_category(category, existing_videos, max_pages=2)
        all_new_videos.update(category_videos)
        print(f"Found {len(category_videos)} new videos in category {category}")
        time.sleep(random.uniform(2, 5))  # Longer delay between categories
    
    # Combine existing and new videos
    combined_videos = existing_videos.copy()
    combined_videos.update(all_new_videos)
    
    # Save all videos
    save_videos(combined_videos)
    
    print(f"\n=== Scraping Summary ===")
    print(f"Existing videos: {len(existing_videos)}")
    print(f"New videos found: {len(all_new_videos)}")
    print(f"Total videos: {len(combined_videos)}")
    print("Comprehensive scraping completed!")

if __name__ == "__main__":
    main()