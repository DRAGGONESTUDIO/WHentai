#!/usr/bin/env python3
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def test_thumbnail_url(thumbnail_url, timeout=5):
    """Test if a thumbnail URL is accessible"""
    try:
        # Send a HEAD request first to check if the URL exists
        response = requests.head(thumbnail_url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            return True, "Accessible", response.status_code
        elif response.status_code == 404:
            return False, "Not Found", response.status_code
        elif response.status_code == 403:
            # Try GET request if HEAD is forbidden
            response = requests.get(thumbnail_url, timeout=timeout, allow_redirects=True, stream=True)
            response.close()
            if response.status_code == 200:
                return True, "Accessible (GET)", response.status_code
            else:
                return False, f"Access Denied (Status: {response.status_code})", response.status_code
        else:
            return False, f"Status: {response.status_code}", response.status_code
    except requests.exceptions.RequestException as e:
        return False, str(e), 0
    except Exception as e:
        return False, str(e), 0

def test_thumbnails(videos, sample_size=10):
    """Test thumbnail URLs for a sample of videos"""
    print(f"Testing thumbnail URLs for {min(sample_size, len(videos))} videos...")
    
    # Sample videos for testing
    sample_videos = videos[:sample_size] if len(videos) > sample_size else videos
    
    # Test URLs in parallel
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tasks
        future_to_video = {
            executor.submit(test_thumbnail_url, video.get('thumbnail', '')): video 
            for video in sample_videos
        }
        
        # Process completed tasks
        for future in as_completed(future_to_video):
            video = future_to_video[future]
            try:
                success, message, status_code = future.result()
                results.append({
                    'video': video,
                    'success': success,
                    'message': message,
                    'status_code': status_code
                })
            except Exception as e:
                results.append({
                    'video': video,
                    'success': False,
                    'message': str(e),
                    'status_code': 0
                })
    
    return results

def main():
    """Main function to test thumbnail URLs"""
    print("=== WHentai Thumbnail URL Test ===\n")
    
    # Load videos
    print("Loading videos from database...")
    try:
        with open('videos.json', 'r', encoding='utf-8') as f:
            videos = json.load(f)
        print(f"Loaded {len(videos)} videos from database")
    except Exception as e:
        print(f"Error loading videos: {e}")
        return
    
    # Test thumbnail URLs
    results = test_thumbnails(videos, sample_size=20)
    
    # Analyze results
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n=== Test Results ===")
    print(f"Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"Failed: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")
    
    # Show failed examples
    if failed:
        print(f"\n=== Failed Thumbnails ===")
        for i, result in enumerate(failed[:10]):
            video = result['video']
            title = video.get('title', 'Unknown')[:50]
            thumbnail = video.get('thumbnail', 'None')
            print(f"{i+1}. {title}...")
            print(f"   Thumbnail: {thumbnail}")
            print(f"   Error: {result['message']}")
            print()
    
    # Show successful examples
    if successful:
        print(f"\n=== Successful Thumbnails ===")
        for i, result in enumerate(successful[:10]):
            video = result['video']
            title = video.get('title', 'Unknown')[:50]
            thumbnail = video.get('thumbnail', 'None')
            print(f"{i+1}. {title}...")
            print(f"   Thumbnail: {thumbnail}")
            print(f"   Status: {result['message']}")
            print()

if __name__ == "__main__":
    main()