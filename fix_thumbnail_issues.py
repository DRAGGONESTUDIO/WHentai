#!/usr/bin/env python3
"""
Script to fix thumbnail issues by implementing better fallback handling
"""

import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from urllib.parse import urlparse

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

def save_videos(videos, file_path):
    """Save videos to JSON file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(videos, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(videos)} videos to {file_path}")
        return True
    except Exception as e:
        print(f"Error saving videos to {file_path}: {e}")
        return False

def is_valid_url(url):
    """Check if a URL is valid"""
    if not url or not isinstance(url, str):
        return False
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def test_thumbnail_url(thumbnail_url, timeout=3):
    """Test if a thumbnail URL is accessible"""
    if not is_valid_url(thumbnail_url):
        return False, "Invalid URL"
    
    try:
        # Send a HEAD request first to check if the URL exists
        response = requests.head(thumbnail_url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            return True, "Accessible"
        elif response.status_code == 404:
            return False, "Not Found"
        elif response.status_code == 403:
            # Try GET request if HEAD is forbidden
            response = requests.get(thumbnail_url, timeout=timeout, allow_redirects=True, stream=True)
            response.close()
            if response.status_code == 200:
                return True, "Accessible (GET)"
            else:
                return False, f"Access Denied (Status: {response.status_code})"
        else:
            return False, f"Status: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def categorize_thumbnail(thumbnail):
    """Categorize a thumbnail URL"""
    if not thumbnail or not isinstance(thumbnail, str):
        return 'missing'
    
    # Check for whitespace-only strings
    if thumbnail.strip() == '':
        return 'empty'
    
    # Check for "undefined" string
    if thumbnail == 'undefined':
        return 'undefined_string'
    
    # Check for "null" string
    if thumbnail == 'null':
        return 'null_string'
    
    # Check for valid URL format
    if not thumbnail.startswith('http'):
        # Check for specific invalid patterns
        if thumbnail.startswith('data:'):
            return 'data_url'
        elif thumbnail.startswith('blob:'):
            return 'blob_url'
        elif thumbnail.startswith('javascript:'):
            return 'javascript_url'
        else:
            return 'no_http'
    
    # Check if it's already a placeholder
    if 'placehold.co' in thumbnail:
        return 'placeholder'
    
    return 'valid'

def fix_video_thumbnails(videos):
    """Fix thumbnail issues in videos by improving validation"""
    fixed_count = 0
    fixed_videos = []
    
    # Categorize all thumbnails first
    categories = {}
    for video in videos:
        category = categorize_thumbnail(video.get('thumbnail', ''))
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    print(f"Thumbnail categories: {categories}")
    
    # Process videos
    for video in videos:
        fixed_video = video.copy()
        thumbnail = video.get('thumbnail', '')
        category = categorize_thumbnail(thumbnail)
        
        # If it's already valid or a placeholder, keep as is
        if category in ['valid', 'placeholder']:
            fixed_videos.append(fixed_video)
            continue
        
        # For other categories, ensure we have a proper fallback
        if category in ['missing', 'empty', 'undefined_string', 'null_string', 'no_http', 'data_url', 'blob_url', 'javascript_url']:
            # Use a better placeholder
            fixed_video['thumbnail'] = 'https://placehold.co/300x200/1a1a1a/ff6b6b?text=Thumbnail+Not+Available'
            fixed_count += 1
        
        fixed_videos.append(fixed_video)
    
    return fixed_videos, fixed_count

def create_thumbnail_fallbacks(videos, sample_size=100):
    """Create fallback thumbnails for videos with broken URLs"""
    print(f"Creating fallback thumbnails for {min(sample_size, len(videos))} videos...")
    
    # Sample videos for testing
    sample_videos = videos[:sample_size] if len(videos) > sample_size else videos
    
    # Test URLs in parallel
    broken_thumbnails = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(test_thumbnail_url, video.get('thumbnail', '')): i 
            for i, video in enumerate(sample_videos)
        }
        
        # Process completed tasks
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                success, message = future.result()
                if not success and message == "Not Found":
                    broken_thumbnails.append(index)
            except Exception as e:
                pass  # Ignore errors in this test
    
    print(f"Found {len(broken_thumbnails)} broken thumbnails in sample")
    
    # Apply fallbacks to all videos that had broken thumbnails in sample
    fixed_videos = []
    fallback_count = 0
    
    for i, video in enumerate(videos):
        fixed_video = video.copy()
        thumbnail = video.get('thumbnail', '')
        
        # If this video was in our sample and had a broken thumbnail, or if it's already categorized as problematic
        category = categorize_thumbnail(thumbnail)
        if i in broken_thumbnails or category in ['missing', 'empty', 'undefined_string', 'null_string', 'no_http', 'data_url', 'blob_url', 'javascript_url']:
            # Apply a better fallback
            fixed_video['thumbnail'] = 'https://placehold.co/300x200/2c3e50/ecf0f1?text=Image+Not+Found'
            fallback_count += 1
            
        fixed_videos.append(fixed_video)
    
    return fixed_videos, fallback_count

def main():
    """Main function to fix thumbnail issues"""
    print("=== WHentai Thumbnail Issue Fix ===\n")
    
    # File paths
    videos_file = "videos.json"
    backup_file = "videos_thumbnail_fix_backup.json"
    
    # Load videos
    print("Loading videos from database...")
    videos = load_videos(videos_file)
    
    if not videos:
        print("No videos found or error loading videos!")
        return
        
    print(f"Loaded {len(videos)} videos from database")
    
    # Create backup
    print("Creating backup...")
    if not save_videos(videos, backup_file):
        print("Warning: Could not create backup!")
    
    # Fix thumbnail issues
    print("Fixing thumbnail issues...")
    fixed_videos, fixed_count = fix_video_thumbnails(videos)
    
    print(f"Fixed {fixed_count} videos with thumbnail issues")
    
    # Create better fallbacks
    print("Creating improved fallback thumbnails...")
    final_videos, fallback_count = create_thumbnail_fallbacks(fixed_videos)
    
    print(f"Applied fallbacks to {fallback_count} videos")
    
    # Save the fixed videos
    print("Saving fixed videos...")
    if save_videos(final_videos, videos_file):
        print("Successfully saved fixed videos!")
    else:
        print("Error saving fixed videos!")
    
    # Show final statistics
    print(f"\n=== Summary ===")
    print(f"Total videos processed: {len(videos):,}")
    print(f"Videos with fixes applied: {fixed_count:,}")
    print(f"Videos with fallbacks applied: {fallback_count:,}")
    
    if fixed_count > 0 or fallback_count > 0:
        print(f"\nBackup saved as: {backup_file}")
        print("You can restore the original database from this backup if needed.")

if __name__ == "__main__":
    main()