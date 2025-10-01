#!/usr/bin/env python3
"""
Script to check for broken video links and thumbnails
"""

import json
import requests
from urllib.parse import urlparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def load_videos(file_path):
    """Load videos from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        # Fix any issues with the JSON format
        if content.endswith(','):
            content = content[:-1] + ']'
            
        # Parse the JSON
        data = json.loads(content)
        return data
    except Exception as e:
        print(f"Error loading videos from {file_path}: {e}")
        return []

def is_valid_url(url):
    """Check if a URL is valid"""
    if not url or not isinstance(url, str):
        return False
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def check_thumbnail_url(thumbnail_url, timeout=5):
    """Check if a thumbnail URL is accessible"""
    if not is_valid_url(thumbnail_url):
        return False, "Invalid URL"
    
    try:
        # Just check if we can connect, don't download the whole image
        response = requests.head(thumbnail_url, timeout=timeout, allow_redirects=True)
        return response.status_code == 200, f"Status: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def check_video_links(video, timeout=5):
    """Check if video links are accessible"""
    results = {
        'thumbnail_ok': True,
        'thumbnail_error': '',
        'external_url_ok': True,
        'external_url_error': '',
        'detail_url_ok': True,
        'detail_url_error': ''
    }
    
    # Check thumbnail
    if 'thumbnail' in video and video['thumbnail']:
        results['thumbnail_ok'], results['thumbnail_error'] = check_thumbnail_url(video['thumbnail'], timeout)
    
    # Check external URL if present
    if 'external_url' in video and video['external_url'] and video['external_url'].strip() != '':
        try:
            response = requests.head(video['external_url'], timeout=timeout, allow_redirects=True)
            results['external_url_ok'] = response.status_code < 400 or response.status_code == 403  # 403 might be okay
            results['external_url_error'] = f"Status: {response.status_code}"
        except requests.exceptions.RequestException as e:
            results['external_url_ok'] = False
            results['external_url_error'] = str(e)
        except Exception as e:
            results['external_url_ok'] = False
            results['external_url_error'] = str(e)
    
    # Check detail URL if present
    if 'detail_url' in video and video['detail_url'] and video['detail_url'].strip() != '' and video['detail_url'] != '#':
        try:
            response = requests.head(video['detail_url'], timeout=timeout, allow_redirects=True)
            results['detail_url_ok'] = response.status_code < 400 or response.status_code == 403  # 403 might be okay
            results['detail_url_error'] = f"Status: {response.status_code}"
        except requests.exceptions.RequestException as e:
            results['detail_url_ok'] = False
            results['detail_url_error'] = str(e)
        except Exception as e:
            results['detail_url_ok'] = False
            results['detail_url_error'] = str(e)
    
    return results

def analyze_videos(videos, sample_size=100):
    """Analyze videos for broken links"""
    print(f"Analyzing {min(sample_size, len(videos))} videos for broken links...")
    
    # Sample videos for testing (don't check all to avoid rate limiting)
    sample_videos = videos[:sample_size] if len(videos) > sample_size else videos
    
    broken_thumbnails = []
    broken_external_urls = []
    broken_detail_urls = []
    
    # Use threading to check URLs in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all tasks
        future_to_video = {executor.submit(check_video_links, video): video for video in sample_videos}
        
        # Process completed tasks
        for i, future in enumerate(as_completed(future_to_video)):
            video = future_to_video[future]
            try:
                result = future.result()
                
                if not result['thumbnail_ok']:
                    broken_thumbnails.append({
                        'video': video,
                        'error': result['thumbnail_error']
                    })
                
                if not result['external_url_ok']:
                    broken_external_urls.append({
                        'video': video,
                        'error': result['external_url_error']
                    })
                
                if not result['detail_url_ok']:
                    broken_detail_urls.append({
                        'video': video,
                        'error': result['detail_url_error']
                    })
                
                # Print progress
                if (i + 1) % 10 == 0:
                    print(f"Checked {i + 1}/{len(sample_videos)} videos...")
                    
            except Exception as e:
                print(f"Error checking video: {e}")
    
    return broken_thumbnails, broken_external_urls, broken_detail_urls

def main():
    """Main function to check for broken videos"""
    print("=== WHentai Broken Video Link Checker ===\n")
    
    # File paths
    videos_file = "videos.json"
    
    # Load videos
    print("Loading videos from database...")
    videos = load_videos(videos_file)
    
    if not videos:
        print("No videos found or error loading videos!")
        return
        
    print(f"Loaded {len(videos)} videos from database")
    
    # Analyze videos
    broken_thumbnails, broken_external_urls, broken_detail_urls = analyze_videos(videos, sample_size=50)
    
    # Show results
    print(f"\n=== Analysis Results ===")
    print(f"Broken thumbnails: {len(broken_thumbnails)}")
    print(f"Broken external URLs: {len(broken_external_urls)}")
    print(f"Broken detail URLs: {len(broken_detail_urls)}")
    
    # Show some examples
    if broken_thumbnails:
        print(f"\n=== Sample Broken Thumbnails ===")
        for i, item in enumerate(broken_thumbnails[:5]):
            video = item['video']
            print(f"{i+1}. Title: {video.get('title', 'Unknown')}")
            print(f"   Thumbnail: {video.get('thumbnail', 'None')}")
            print(f"   Error: {item['error']}\n")
    
    if broken_external_urls:
        print(f"\n=== Sample Broken External URLs ===")
        for i, item in enumerate(broken_external_urls[:5]):
            video = item['video']
            print(f"{i+1}. Title: {video.get('title', 'Unknown')}")
            print(f"   External URL: {video.get('external_url', 'None')}")
            print(f"   Error: {item['error']}\n")
    
    if broken_detail_urls:
        print(f"\n=== Sample Broken Detail URLs ===")
        for i, item in enumerate(broken_detail_urls[:5]):
            video = item['video']
            print(f"{i+1}. Title: {video.get('title', 'Unknown')}")
            print(f"   Detail URL: {video.get('detail_url', 'None')}")
            print(f"   Error: {item['error']}\n")
    
    # Summary
    print(f"\n=== Summary ===")
    print(f"Total videos analyzed: 50")
    print(f"Videos with broken thumbnails: {len(broken_thumbnails)} ({len(broken_thumbnails)/50*100:.1f}%)")
    print(f"Videos with broken external URLs: {len(broken_external_urls)} ({len(broken_external_urls)/50*100:.1f}%)")
    print(f"Videos with broken detail URLs: {len(broken_detail_urls)} ({len(broken_detail_urls)/50*100:.1f}%)")

if __name__ == "__main__":
    main()