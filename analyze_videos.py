#!/usr/bin/env python3
"""
Script to analyze videos for duplicates and thumbnail issues
"""

import json
import re
import os
from collections import defaultdict
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
    
    # Remove any whitespace
    thumbnail = thumbnail.strip()
    
    # Fix common URL encoding issues
    thumbnail = thumbnail.replace(" ", "%20")
    
    # Check if it's a valid URL
    if is_valid_url(thumbnail):
        return thumbnail
    
    # If it's a relative path, try to fix it
    if thumbnail.startswith("//"):
        return "https:" + thumbnail
    elif thumbnail.startswith("/"):
        return "https://c1.ttcache.com" + thumbnail
    
    return thumbnail

def analyze_thumbnails(videos):
    """Analyze thumbnail issues"""
    issues = {
        'missing': 0,
        'invalid': 0,
        'fixed': 0,
        'total': len(videos)
    }
    
    fixed_videos = []
    
    for video in videos:
        # Make a copy of the video
        fixed_video = video.copy()
        
        # Get thumbnail
        thumbnail = video.get('thumbnail', '')
        
        # Check if thumbnail is missing
        if not thumbnail or thumbnail == "":
            issues['missing'] += 1
            # Try to extract from detail_url if possible
            detail_url = video.get('detail_url', '')
            if detail_url and 'ttcache.com' in detail_url:
                # Try to extract thumbnail ID from URL
                match = re.search(r'/thumbnail/([^/]+)/', detail_url)
                if match:
                    thumbnail_id = match.group(1)
                    fixed_video['thumbnail'] = f"https://c1.ttcache.com/thumbnail/{thumbnail_id}/288x162/thumbnail.jpg"
                    issues['fixed'] += 1
        # Check if thumbnail URL is invalid
        elif not is_valid_url(thumbnail):
            issues['invalid'] += 1
            # Try to fix it
            fixed_thumbnail = fix_thumbnail_url(thumbnail)
            if fixed_thumbnail != thumbnail and is_valid_url(fixed_thumbnail):
                fixed_video['thumbnail'] = fixed_thumbnail
                issues['fixed'] += 1
            elif fixed_thumbnail != thumbnail:
                fixed_video['thumbnail'] = fixed_thumbnail
        
        fixed_videos.append(fixed_video)
    
    return fixed_videos, issues

def identify_duplicates(videos):
    """Identify duplicate videos based on multiple criteria"""
    seen = {}
    duplicates = []
    
    for i, video in enumerate(videos):
        # Create a composite key for better duplicate detection
        video_id = video.get('id', '')
        video_url = video.get('url', '') or video.get('external_url', '') or video.get('detail_url', '')
        video_title = video.get('title', '')
        
        # Create a more comprehensive key
        composite_key = f"{video_id}|{video_url}|{video_title}"
        
        # Normalize the key (remove extra whitespace, convert to lowercase)
        composite_key = composite_key.strip().lower()
        
        # Check for duplicates
        if composite_key in seen:
            duplicates.append((i, seen[composite_key], composite_key))
        else:
            seen[composite_key] = i
                
    return duplicates

def remove_duplicates(videos):
    """Remove duplicate videos from the list"""
    # Identify duplicates first
    duplicates = identify_duplicates(videos)
    
    if not duplicates:
        print("No duplicates found!")
        return videos, 0
        
    print(f"Found {len(duplicates)} duplicate videos")
    
    # Create a set of indices to remove
    indices_to_remove = set([dup[0] for dup in duplicates])
    
    # Create new list without duplicates (keeping the first occurrence)
    unique_videos = []
    for i, video in enumerate(videos):
        if i not in indices_to_remove:
            unique_videos.append(video)
            
    duplicates_removed = len(duplicates)
    print(f"Removed {duplicates_removed} duplicate videos")
    print(f"Original count: {len(videos)}")
    print(f"New count: {len(unique_videos)}")
    
    return unique_videos, duplicates_removed

def main():
    """Main function to analyze and fix videos"""
    print("=== WHentai Video Analysis and Fix Tool ===\n")
    
    # File paths
    videos_file = "D:\\Website Project\\WHentai\\WHentai\\videos.json"
    backup_file = "D:\\Website Project\\WHentai\\WHentai\\videos_backup_before_fix.json"
    
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
        
    # Analyze and fix thumbnails
    print("Analyzing and fixing thumbnails...")
    fixed_videos, thumbnail_issues = analyze_thumbnails(videos)
    
    print(f"Thumbnail issues found:")
    print(f"  - Missing thumbnails: {thumbnail_issues['missing']}")
    print(f"  - Invalid thumbnails: {thumbnail_issues['invalid']}")
    print(f"  - Fixed thumbnails: {thumbnail_issues['fixed']}")
    print(f"  - Total videos analyzed: {thumbnail_issues['total']}")
    
    # Remove duplicates
    print("\nRemoving duplicates...")
    unique_videos, duplicates_removed = remove_duplicates(fixed_videos)
    
    # Save the fixed videos
    print("Saving fixed videos...")
    if save_videos(unique_videos, videos_file):
        print("Successfully saved fixed videos!")
    else:
        print("Error saving fixed videos!")
        
    # Show final statistics
    print(f"\n=== Summary ===")
    print(f"Original video count: {len(videos):,}")
    print(f"Videos after fixes: {len(unique_videos):,}")
    print(f"Duplicates removed: {duplicates_removed:,}")
    print(f"Thumbnail issues fixed: {thumbnail_issues['fixed']:,}")
    
    if duplicates_removed > 0 or thumbnail_issues['fixed'] > 0:
        print(f"\nBackup of original database saved as:")
        print(backup_file)
    else:
        print(f"\nNo issues were found or fixed.")
        # Remove backup if no issues were found
        try:
            os.remove(backup_file)
            print("Backup file removed (no issues found)")
        except:
            pass

if __name__ == "__main__":
    main()