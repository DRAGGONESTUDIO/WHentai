#!/usr/bin/env python3
import json
import requests
import time

def test_thumbnail_accessibility():
    """Test if thumbnail URLs are accessible"""
    print("=== Testing Thumbnail Accessibility ===\n")
    
    # Load videos
    try:
        with open('videos.json', 'r', encoding='utf-8') as f:
            videos = json.load(f)
        print(f"Loaded {len(videos)} videos")
    except Exception as e:
        print(f"Error loading videos: {e}")
        return
    
    # Get sample of valid thumbnails
    valid_thumbnails = []
    for video in videos:
        thumbnail = video.get('thumbnail', '')
        if thumbnail.startswith('http') and 'placehold.co' not in thumbnail:
            valid_thumbnails.append((video.get('title', 'Unknown')[:50], thumbnail))
            if len(valid_thumbnails) >= 10:
                break
    
    print(f"\nTesting {len(valid_thumbnails)} valid thumbnails:")
    
    accessible = 0
    inaccessible = 0
    
    for i, (title, thumbnail) in enumerate(valid_thumbnails, 1):
        try:
            # Test with a HEAD request first
            response = requests.head(thumbnail, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                print(f"{i}. ✓ Accessible - {title}...")
                accessible += 1
            elif response.status_code == 404:
                print(f"{i}. ✗ Not Found - {title}...")
                inaccessible += 1
            else:
                # Try with GET request if HEAD fails
                response = requests.get(thumbnail, timeout=5, allow_redirects=True, stream=True)
                response.close()
                if response.status_code == 200:
                    print(f"{i}. ✓ Accessible (GET) - {title}...")
                    accessible += 1
                else:
                    print(f"{i}. ✗ Status {response.status_code} - {title}...")
                    inaccessible += 1
        except requests.exceptions.RequestException as e:
            print(f"{i}. ✗ Error - {title}... ({str(e)[:50]})")
            inaccessible += 1
        except Exception as e:
            print(f"{i}. ✗ Unexpected Error - {title}... ({str(e)[:50]})")
            inaccessible += 1
    
    print(f"\n=== Results ===")
    print(f"Accessible: {accessible}")
    print(f"Inaccessible: {inaccessible}")
    print(f"Success Rate: {accessible/(accessible+inaccessible)*100:.1f}%")

if __name__ == "__main__":
    test_thumbnail_accessibility()