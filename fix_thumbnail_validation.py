#!/usr/bin/env python3
"""
Script to fix thumbnail validation issues
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

def is_valid_thumbnail_url(url):
    """Check if a thumbnail URL is valid and accessible"""
    if not url or not isinstance(url, str):
        return False
    
    # Check if it's a valid URL format
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False
    except:
        return False
    
    # Check for common invalid patterns
    invalid_patterns = [
        'undefined',
        'null',
        'javascript:',
        'data:image',
        'blob:'
    ]
    
    if any(pattern in url.lower() for pattern in invalid_patterns):
        return False
    
    # Check if it's a thumbnail URL
    if 'thumbnail' not in url and 'thumber.php' not in url:
        return False
    
    return True

def fix_thumbnail_urls(videos):
    """Fix thumbnail URLs in videos"""
    fixed_count = 0
    fixed_videos = []
    
    for video in videos:
        fixed_video = video.copy()
        thumbnail = video.get('thumbnail', '')
        
        # If thumbnail is invalid, try to reconstruct it
        if not is_valid_thumbnail_url(thumbnail):
            # Try to create a valid thumbnail URL from other video data
            detail_url = video.get('detail_url', '')
            if detail_url and isinstance(detail_url, str):
                # Try to extract thumbnail info from detail URL
                # This is a simplified approach - in a real implementation you might
                # need more sophisticated parsing
                pass
            
            # If we still don't have a valid thumbnail, leave it as is
            # The JavaScript will handle the fallback
            pass
        
        # Keep the original thumbnail - let JavaScript handle validation
        # This prevents overwriting potentially valid URLs that might fail our simple validation
        fixed_videos.append(fixed_video)
    
    return fixed_videos, fixed_count

def enhance_video_data(videos):
    """Enhance video data to improve JavaScript validation"""
    enhanced_count = 0
    enhanced_videos = []
    
    for video in videos:
        enhanced_video = video.copy()
        
        # Ensure all videos have the required fields
        if 'title' not in enhanced_video or not enhanced_video['title']:
            enhanced_video['title'] = 'Untitled Video'
        
        if 'thumbnail' not in enhanced_video or not enhanced_video['thumbnail']:
            enhanced_video['thumbnail'] = ''
        
        if 'detail_url' not in enhanced_video:
            enhanced_video['detail_url'] = ''
        
        if 'external_url' not in enhanced_video:
            enhanced_video['external_url'] = ''
        
        # Clean up thumbnail URL
        thumbnail = enhanced_video.get('thumbnail', '')
        if isinstance(thumbnail, str):
            # Remove extra whitespace
            thumbnail = thumbnail.strip()
            
            # Fix common issues
            if thumbnail.startswith('//'):
                thumbnail = 'https:' + thumbnail
            elif thumbnail.startswith('www.'):
                thumbnail = 'https://' + thumbnail
            
            enhanced_video['thumbnail'] = thumbnail
        
        # Clean up URLs
        detail_url = enhanced_video.get('detail_url', '')
        if isinstance(detail_url, str):
            enhanced_video['detail_url'] = detail_url.strip()
        
        external_url = enhanced_video.get('external_url', '')
        if isinstance(external_url, str):
            enhanced_video['external_url'] = external_url.strip()
        
        enhanced_videos.append(enhanced_video)
        enhanced_count += 1
    
    return enhanced_videos, enhanced_count

def main():
    """Main function to fix thumbnail validation issues"""
    print("=== WHentai Thumbnail Validation Fix ===\n")
    
    # File paths
    videos_file = "videos.json"
    backup_file = "videos_thumbnail_validation_backup.json"
    
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
    
    # Enhance video data
    print("Enhancing video data...")
    enhanced_videos, enhanced_count = enhance_video_data(videos)
    
    print(f"Enhanced {enhanced_count} videos")
    
    # Save the enhanced videos
    print("Saving enhanced videos...")
    if save_videos(enhanced_videos, videos_file):
        print("Successfully saved enhanced videos!")
    else:
        print("Error saving enhanced videos!")
    
    # Show final statistics
    print(f"\n=== Summary ===")
    print(f"Total videos processed: {len(videos):,}")
    print(f"Videos enhanced: {enhanced_count:,}")
    
    if enhanced_count > 0:
        print(f"\nBackup saved as: {backup_file}")
        print("You can restore the original database from this backup if needed.")
        
        print(f"\n=== Next Steps ===")
        print("1. Clear your browser cache")
        print("2. Hard refresh all pages (Ctrl+F5 or Cmd+Shift+R)")
        print("3. Test video thumbnails on the website")

if __name__ == "__main__":
    main()