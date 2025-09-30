#!/usr/bin/env python3
"""
Script to fix thumbnail URL issues in the video database
"""

import json
import re
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

def fix_thumbnail_url(thumbnail):
    """Fix common thumbnail URL issues"""
    if not thumbnail or not isinstance(thumbnail, str):
        return ""
    
    # Remove extra whitespace
    thumbnail = thumbnail.strip()
    
    # If already a valid URL, return as is
    if is_valid_url(thumbnail):
        return thumbnail
    
    # Fix common issues
    # Protocol-relative URLs
    if thumbnail.startswith("//"):
        return "https:" + thumbnail
    
    # Missing protocol
    if thumbnail.startswith("www."):
        return "https://" + thumbnail
    
    # Common domain fixes
    if "ttcache" in thumbnail and "http" not in thumbnail:
        if not thumbnail.startswith("/"):
            return "https://" + thumbnail
        else:
            return "https://c1.ttcache.com" + thumbnail
    
    # Try to fix relative paths
    if thumbnail.startswith("/thumbnail/"):
        return "https://c1.ttcache.com" + thumbnail
    
    # If we can't fix it, return the original
    return thumbnail

def validate_and_fix_thumbnails(videos):
    """Validate and fix thumbnail URLs in videos"""
    fixed_count = 0
    issue_count = 0
    fixed_videos = []
    
    for video in videos:
        fixed_video = video.copy()
        thumbnail = video.get('thumbnail', '')
        
        # Check if thumbnail has issues
        if thumbnail and isinstance(thumbnail, str):
            # Check if it's a valid URL
            if not is_valid_url(thumbnail):
                issue_count += 1
                # Try to fix it
                fixed_thumbnail = fix_thumbnail_url(thumbnail)
                if fixed_thumbnail != thumbnail:
                    fixed_video['thumbnail'] = fixed_thumbnail
                    fixed_count += 1
                    print(f"Fixed thumbnail: {thumbnail} -> {fixed_thumbnail}")
        
        fixed_videos.append(fixed_video)
    
    return fixed_videos, fixed_count, issue_count

def main():
    """Main function to fix thumbnail URLs"""
    print("=== WHentai Thumbnail URL Fix ===\n")
    
    # File paths
    videos_file = "D:\\Website Project\\WHentai\\WHentai\\videos.json"
    backup_file = "D:\\Website Project\\WHentai\\WHentai\\videos_thumbnail_url_backup.json"
    
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
    
    # Validate and fix thumbnails
    print("Validating and fixing thumbnail URLs...")
    fixed_videos, fixed_count, issue_count = validate_and_fix_thumbnails(videos)
    
    print(f"Thumbnail issues found: {issue_count}")
    print(f"Thumbnail URLs fixed: {fixed_count}")
    
    # Save the fixed videos
    print("Saving fixed videos...")
    if save_videos(fixed_videos, videos_file):
        print("Successfully saved fixed videos!")
    else:
        print("Error saving fixed videos!")
    
    # Show final statistics
    print(f"\n=== Summary ===")
    print(f"Total videos processed: {len(videos):,}")
    print(f"Thumbnail issues found: {issue_count:,}")
    print(f"Thumbnail URLs fixed: {fixed_count:,}")
    
    if fixed_count > 0:
        print(f"\nBackup saved as: {backup_file}")
        print("You can restore the original database from this backup if needed.")
    else:
        print("\nNo thumbnail URL issues were found or fixed.")

if __name__ == "__main__":
    main()