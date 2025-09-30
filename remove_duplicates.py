#!/usr/bin/env python3
"""
Script to remove duplicate videos from the WHentai database
"""

import json
import os
from collections import defaultdict

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

def identify_duplicates(videos):
    """Identify duplicate videos based on URL or ID"""
    seen_urls = {}
    seen_ids = {}
    duplicates = []
    
    for i, video in enumerate(videos):
        # Get video identifier
        video_id = video.get('id') or video.get('url') or video.get('title', '')
        video_url = video.get('url') or video.get('external_url') or video.get('detail_url') or ''
        
        # Check for duplicate ID
        is_duplicate = False
        if video_id and video_id in seen_ids:
            duplicates.append((i, seen_ids[video_id], 'id'))
            is_duplicate = True
            
        # Check for duplicate URL
        elif video_url and video_url in seen_urls:
            duplicates.append((i, seen_urls[video_url], 'url'))
            is_duplicate = True
            
        # Record this video if not a duplicate
        if not is_duplicate:
            if video_id:
                seen_ids[video_id] = i
            if video_url:
                seen_urls[video_url] = i
                
    return duplicates

def remove_duplicates(videos):
    """Remove duplicate videos from the list"""
    # Identify duplicates first
    duplicates = identify_duplicates(videos)
    
    if not duplicates:
        print("No duplicates found!")
        return videos
        
    print(f"Found {len(duplicates)} duplicate videos")
    
    # Create a set of indices to remove
    indices_to_remove = set([dup[0] for dup in duplicates])
    
    # Create new list without duplicates (keeping the first occurrence)
    unique_videos = []
    for i, video in enumerate(videos):
        if i not in indices_to_remove:
            unique_videos.append(video)
            
    print(f"Removed {len(duplicates)} duplicate videos")
    print(f"Original count: {len(videos)}")
    print(f"New count: {len(unique_videos)}")
    
    return unique_videos

def main():
    """Main function to remove duplicates from the video database"""
    print("=== WHentai Duplicate Video Remover ===\n")
    
    # File paths
    videos_file = "D:\\Website Project\\WHentai\\WHentai\\videos.json"
    backup_file = "D:\\Website Project\\WHentai\\WHentai\\videos_backup_before_dedup.json"
    
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
        
    # Remove duplicates
    print("Removing duplicates...")
    unique_videos = remove_duplicates(videos)
    
    # Save the deduplicated videos
    print("Saving deduplicated videos...")
    if save_videos(unique_videos, videos_file):
        print("Successfully saved deduplicated videos!")
    else:
        print("Error saving deduplicated videos!")
        
    # Show final statistics
    duplicates_removed = len(videos) - len(unique_videos)
    print(f"\n=== Summary ===")
    print(f"Original video count: {len(videos):,}")
    print(f"Videos after deduplication: {len(unique_videos):,}")
    print(f"Duplicates removed: {duplicates_removed:,}")
    
    if duplicates_removed > 0:
        print("\nBackup of original database saved as:")
        print(backup_file)
    else:
        print("\nNo duplicates were found or removed.")
        # Remove backup if no duplicates were found
        try:
            os.remove(backup_file)
            print("Backup file removed (no duplicates found)")
        except:
            pass

if __name__ == "__main__":
    main()