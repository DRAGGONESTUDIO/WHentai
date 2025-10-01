#!/usr/bin/env python3
"""
Script to analyze thumbnail issues in detail
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

def analyze_thumbnail_issues(videos, sample_size=1000):
    """Analyze thumbnail issues in detail"""
    print(f"Analyzing thumbnail issues for {min(sample_size, len(videos))} videos...")
    
    # Sample videos for testing
    sample_videos = videos[:sample_size] if len(videos) > sample_size else videos
    
    # Issue categories
    issues = {
        'valid': 0,
        'empty': 0,
        'whitespace_only': 0,
        'undefined_string': 0,
        'null_string': 0,
        'no_http': 0,
        'data_url': 0,
        'blob_url': 0,
        'javascript_url': 0,
        'no_thumbnail_keyword': 0,
        'other': 0
    }
    
    # Collect examples for each issue
    examples = {key: [] for key in issues.keys()}
    
    for video in sample_videos:
        thumbnail = video.get('thumbnail', '')
        
        # Categorize the thumbnail
        category = categorize_thumbnail(thumbnail)
        issues[category] += 1
        
        # Collect examples (max 3 per category)
        if len(examples[category]) < 3:
            examples[category].append({
                'title': video.get('title', 'Unknown'),
                'thumbnail': thumbnail
            })
    
    return issues, examples

def categorize_thumbnail(thumbnail):
    """Categorize a thumbnail URL"""
    if not thumbnail:
        return 'empty'
    
    if isinstance(thumbnail, str):
        # Check for whitespace-only strings
        if thumbnail.strip() == '':
            return 'whitespace_only'
        
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
        
        # Check if it contains "thumbnail" keyword
        if 'thumbnail' not in thumbnail.lower() and 'thumber.php' not in thumbnail.lower():
            return 'no_thumbnail_keyword'
        
        return 'valid'
    
    return 'other'

def main():
    """Main function to analyze thumbnail issues"""
    print("=== WHentai Thumbnail Issue Analysis ===\n")
    
    # Load videos
    print("Loading videos from database...")
    videos = load_videos("videos.json")
    
    if not videos:
        print("No videos found or error loading videos!")
        return
        
    print(f"Loaded {len(videos)} videos from database")
    
    # Analyze thumbnail issues
    issues, examples = analyze_thumbnail_issues(videos)
    
    print(f"\n=== Thumbnail Issue Analysis ===")
    total = sum(issues.values())
    for issue, count in issues.items():
        percentage = (count / total) * 100 if total > 0 else 0
        print(f"{issue}: {count} ({percentage:.1f}%)")
    
    print(f"\n=== Examples of Each Issue ===")
    for issue, example_list in examples.items():
        if example_list:
            print(f"\n{issue}:")
            for example in example_list:
                print(f"  - Title: {example['title']}")
                print(f"    Thumbnail: {example['thumbnail']}")

if __name__ == "__main__":
    main()