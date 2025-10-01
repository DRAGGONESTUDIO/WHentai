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

def analyze_thumbnail_patterns(videos, sample_size=1000):
    """Analyze thumbnail URL patterns to identify issues"""
    print(f"Analyzing thumbnail patterns for {min(sample_size, len(videos))} videos...")
    
    # Sample videos for testing
    sample_videos = videos[:sample_size] if len(videos) > sample_size else videos
    
    # Pattern analysis
    patterns = {}
    domains = {}
    extensions = {}
    issues = {
        'missing': 0,
        'invalid': 0,
        'placeholder': 0,
        'thumber_php': 0,
        'other': 0
    }
    
    for video in sample_videos:
        thumbnail = video.get('thumbnail', '')
        
        # Categorize thumbnails
        if not thumbnail or thumbnail.strip() == '':
            issues['missing'] += 1
            category = 'missing'
        elif 'placehold.co' in thumbnail:
            issues['placeholder'] += 1
            category = 'placeholder'
        elif thumbnail.endswith('/thumber.php'):
            issues['thumber_php'] += 1
            category = 'thumber_php'
        elif not thumbnail.startswith('http'):
            issues['invalid'] += 1
            category = 'invalid'
        else:
            issues['other'] += 1
            category = 'valid'
        
        # Track patterns
        if category not in patterns:
            patterns[category] = 0
        patterns[category] += 1
        
        # Track domains
        if thumbnail and thumbnail.startswith('http'):
            try:
                domain = urlparse(thumbnail).netloc
                if domain not in domains:
                    domains[domain] = 0
                domains[domain] += 1
            except:
                pass
        
        # Track extensions
        if thumbnail:
            match = re.search(r'\.([a-zA-Z0-9]+)(?:\?.*)?$', thumbnail)
            if match:
                ext = match.group(1).lower()
                if ext not in extensions:
                    extensions[ext] = 0
                extensions[ext] += 1
    
    return patterns, domains, extensions, issues

def find_broken_thumbnail_patterns(videos, sample_size=1000):
    """Find specific patterns of broken thumbnails"""
    print(f"Finding broken thumbnail patterns for {min(sample_size, len(videos))} videos...")
    
    # Sample videos for testing
    sample_videos = videos[:sample_size] if len(videos) > sample_size else videos
    
    broken_patterns = {}
    
    for video in sample_videos:
        thumbnail = video.get('thumbnail', '')
        
        # Skip valid thumbnails
        if thumbnail and thumbnail.startswith('http') and 'placehold.co' not in thumbnail:
            continue
            
        # Categorize broken thumbnails
        if not thumbnail or thumbnail.strip() == '':
            pattern = 'MISSING'
        elif 'placehold.co' in thumbnail:
            pattern = 'PLACEHOLDER'
        elif thumbnail.endswith('/thumber.php'):
            pattern = 'THUMBER_PHP'
        elif not thumbnail.startswith('http'):
            pattern = 'INVALID_URL'
        else:
            pattern = 'OTHER_BROKEN'
            
        if pattern not in broken_patterns:
            broken_patterns[pattern] = []
            
        if len(broken_patterns[pattern]) < 5:  # Limit examples
            broken_patterns[pattern].append({
                'title': video.get('title', 'Unknown'),
                'thumbnail': thumbnail
            })
    
    return broken_patterns

def main():
    """Main function to analyze thumbnail issues"""
    print("=== WHentai Thumbnail Analysis ===\n")
    
    # Load videos
    print("Loading videos from database...")
    videos = load_videos("videos.json")
    
    if not videos:
        print("No videos found or error loading videos!")
        return
        
    print(f"Loaded {len(videos)} videos from database")
    
    # Analyze thumbnail patterns
    patterns, domains, extensions, issues = analyze_thumbnail_patterns(videos)
    
    print(f"\n=== Thumbnail Pattern Analysis ===")
    for pattern, count in patterns.items():
        print(f"{pattern}: {count}")
    
    print(f"\n=== Domain Analysis ===")
    sorted_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)
    for domain, count in sorted_domains[:10]:  # Top 10 domains
        print(f"{domain}: {count}")
    
    print(f"\n=== Extension Analysis ===")
    sorted_extensions = sorted(extensions.items(), key=lambda x: x[1], reverse=True)
    for ext, count in sorted_extensions:
        print(f"{ext}: {count}")
    
    print(f"\n=== Issue Summary ===")
    total = len(videos)
    for issue, count in issues.items():
        percentage = (count / total) * 100 if total > 0 else 0
        print(f"{issue}: {count} ({percentage:.1f}%)")
    
    # Find broken patterns
    broken_patterns = find_broken_thumbnail_patterns(videos)
    
    print(f"\n=== Broken Thumbnail Patterns ===")
    for pattern, examples in broken_patterns.items():
        print(f"\n{pattern}:")
        for example in examples:
            print(f"  - Title: {example['title']}")
            print(f"    Thumbnail: {example['thumbnail']}")
    
    # Detailed statistics
    valid_thumbnails = patterns.get('valid', 0)
    total_videos = len(videos)
    valid_percentage = (valid_thumbnails / total_videos) * 100 if total_videos > 0 else 0
    
    print(f"\n=== Detailed Statistics ===")
    print(f"Total videos: {total_videos:,}")
    print(f"Valid thumbnails: {valid_thumbnails:,} ({valid_percentage:.1f}%)")
    print(f"Broken thumbnails: {total_videos - valid_thumbnails:,} ({100 - valid_percentage:.1f}%)")

if __name__ == "__main__":
    main()