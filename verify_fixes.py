#!/usr/bin/env python3
"""
Script to verify that our fixes have resolved the video issues
"""

import json

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

def verify_fixes():
    """Verify that our fixes have resolved the issues"""
    print("=== WHentai Fix Verification ===\n")
    
    # Load videos
    print("Loading videos from database...")
    videos = load_videos("videos.json")
    
    if not videos:
        print("No videos found or error loading videos!")
        return
    
    print(f"Loaded {len(videos)} videos from database")
    
    # Check for videos with missing thumbnails
    missing_thumbnails = 0
    generic_thumbnails = 0
    valid_thumbnails = 0
    
    # Check for videos with URLs
    videos_with_external_url = 0
    videos_with_detail_url = 0
    videos_with_both = 0
    videos_with_neither = 0
    
    for video in videos:
        # Check thumbnails
        if 'thumbnail' not in video or not video['thumbnail'] or video['thumbnail'].strip() == '':
            missing_thumbnails += 1
        elif 'placehold.co' in video['thumbnail']:
            generic_thumbnails += 1
        else:
            valid_thumbnails += 1
        
        # Check URLs
        has_external = 'external_url' in video and video['external_url'] and video['external_url'].strip() != ''
        has_detail = 'detail_url' in video and video['detail_url'] and video['detail_url'].strip() != '' and video['detail_url'] != '#'
        
        if has_external:
            videos_with_external_url += 1
        if has_detail:
            videos_with_detail_url += 1
        if has_external and has_detail:
            videos_with_both += 1
        if not has_external and not has_detail:
            videos_with_neither += 1
    
    # Show results
    print(f"\n=== Thumbnail Analysis ===")
    print(f"Videos with valid thumbnails: {valid_thumbnails:,}")
    print(f"Videos with generic placeholders: {generic_thumbnails:,}")
    print(f"Videos with missing thumbnails: {missing_thumbnails:,}")
    print(f"Total videos: {len(videos):,}")
    
    print(f"\n=== URL Analysis ===")
    print(f"Videos with external_url: {videos_with_external_url:,}")
    print(f"Videos with detail_url: {videos_with_detail_url:,}")
    print(f"Videos with both URLs: {videos_with_both:,}")
    print(f"Videos with neither URL: {videos_with_neither:,}")
    print(f"Total videos: {len(videos):,}")
    
    # Calculate percentages
    if len(videos) > 0:
        valid_thumb_pct = (valid_thumbnails / len(videos)) * 100
        generic_thumb_pct = (generic_thumbnails / len(videos)) * 100
        missing_thumb_pct = (missing_thumbnails / len(videos)) * 100
        
        external_url_pct = (videos_with_external_url / len(videos)) * 100
        detail_url_pct = (videos_with_detail_url / len(videos)) * 100
        neither_url_pct = (videos_with_neither / len(videos)) * 100
        
        print(f"\n=== Percentages ===")
        print(f"Valid thumbnails: {valid_thumb_pct:.1f}%")
        print(f"Generic placeholders: {generic_thumb_pct:.1f}%")
        print(f"Missing thumbnails: {missing_thumb_pct:.1f}%")
        
        print(f"Videos with external_url: {external_url_pct:.1f}%")
        print(f"Videos with detail_url: {detail_url_pct:.1f}%")
        print(f"Videos with neither URL: {neither_url_pct:.1f}%")
    
    # Show some examples
    print(f"\n=== Sample Videos ===")
    for i, video in enumerate(videos[:3]):
        print(f"\n{i+1}. Title: {video.get('title', 'Unknown')}")
        print(f"   Thumbnail: {video.get('thumbnail', 'None')}")
        print(f"   External URL: {video.get('external_url', 'None')}")
        print(f"   Detail URL: {video.get('detail_url', 'None')}")

if __name__ == "__main__":
    verify_fixes()