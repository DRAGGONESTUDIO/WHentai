#!/usr/bin/env python3
"""
Script to fix videos with duplicate thumbnails
"""

import json
import re
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

def extract_thumbnail_id(thumbnail_url):
    """Extract thumbnail ID from URL"""
    if not thumbnail_url or not isinstance(thumbnail_url, str):
        return ""
    
    # Extract ID from thumbnail URL
    match = re.search(r'/thumbnail/([^/]+)/', thumbnail_url)
    if match:
        return match.group(1).strip()
    return ""

def find_videos_with_duplicate_thumbnails(videos):
    """Find videos that share the same thumbnail"""
    thumbnail_groups = defaultdict(list)
    
    # Group videos by thumbnail ID
    for i, video in enumerate(videos):
        thumbnail = video.get('thumbnail', '')
        if thumbnail:
            thumb_id = extract_thumbnail_id(thumbnail)
            if thumb_id:
                thumbnail_groups[thumb_id].append(i)
    
    # Filter to only groups with more than one video
    duplicate_groups = {
        thumb_id: indices 
        for thumb_id, indices in thumbnail_groups.items() 
        if len(indices) > 1
    }
    
    return duplicate_groups

def remove_duplicate_thumbnail_videos(videos):
    """Remove videos with duplicate thumbnails, keeping only the first occurrence"""
    duplicate_groups = find_videos_with_duplicate_thumbnails(videos)
    
    if not duplicate_groups:
        print("No videos with duplicate thumbnails found!")
        return videos, 0
    
    print(f"Found {len(duplicate_groups)} groups of videos with duplicate thumbnails")
    
    # Calculate total duplicates
    total_duplicates = sum(len(indices) - 1 for indices in duplicate_groups.values())
    print(f"Total duplicate videos to remove: {total_duplicates}")
    
    # Create a set of indices to remove (all but the first in each group)
    indices_to_remove = set()
    for thumb_id, indices in duplicate_groups.items():
        # Keep the first video, remove the rest
        indices_to_remove.update(indices[1:])
    
    # Create new list without duplicates
    unique_videos = []
    for i, video in enumerate(videos):
        if i not in indices_to_remove:
            unique_videos.append(video)
    
    removed_count = len(indices_to_remove)
    print(f"Removed {removed_count} videos with duplicate thumbnails")
    print(f"Original count: {len(videos)}")
    print(f"New count: {len(unique_videos)}")
    
    return unique_videos, removed_count

def main():
    """Main function to fix duplicate thumbnail videos"""
    print("=== WHentai Duplicate Thumbnail Fix ===\n")
    
    # File paths
    videos_file = "D:\\Website Project\\WHentai\\WHentai\\videos.json"
    backup_file = "D:\\Website Project\\WHentai\\WHentai\\videos_thumbnail_backup.json"
    
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
    
    # Remove videos with duplicate thumbnails
    print("Removing videos with duplicate thumbnails...")
    unique_videos, removed_count = remove_duplicate_thumbnail_videos(videos)
    
    # Save the unique videos
    print("Saving unique videos...")
    if save_videos(unique_videos, videos_file):
        print("Successfully saved unique videos!")
    else:
        print("Error saving unique videos!")
    
    # Show final statistics
    print(f"\n=== Summary ===")
    print(f"Original video count: {len(videos):,}")
    print(f"Final video count: {len(unique_videos):,}")
    print(f"Videos removed: {removed_count:,}")
    print(f"Reduction: {((len(videos) - len(unique_videos)) / len(videos) * 100):.1f}%")
    
    if removed_count > 0:
        print(f"\nBackup saved as: {backup_file}")
        print("You can restore the original database from this backup if needed.")
    else:
        print("\nNo duplicate thumbnail videos were found or removed.")

if __name__ == "__main__":
    main()