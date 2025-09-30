#!/usr/bin/env python3
"""
Detailed analysis script to find more subtle duplicates and thumbnail issues
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

def extract_video_id(video):
    """Extract a unique identifier for a video"""
    # Try multiple fields to create a unique ID
    video_id = video.get('id')
    if video_id:
        return str(video_id).strip()
    
    # Try URL-based ID
    urls = [video.get('url'), video.get('external_url'), video.get('detail_url')]
    for url in urls:
        if url and isinstance(url, str):
            # Extract ID from URL if possible
            match = re.search(r'/([^/]+)$', url)
            if match:
                return match.group(1).strip()
    
    # Use title as last resort
    title = video.get('title', '')
    if title:
        return str(title).strip()
    
    # Generate a hash-based ID if nothing else works
    return str(hash(str(video)))

def extract_thumbnail_id(thumbnail_url):
    """Extract thumbnail ID from URL"""
    if not thumbnail_url or not isinstance(thumbnail_url, str):
        return ""
    
    # Extract ID from thumbnail URL
    match = re.search(r'/thumbnail/([^/]+)/', thumbnail_url)
    if match:
        return match.group(1).strip()
    return ""

def find_similar_videos(videos, threshold=0.8):
    """Find potentially similar videos based on title similarity"""
    similar_groups = []
    processed = set()
    
    for i, video1 in enumerate(videos):
        if i in processed:
            continue
            
        group = [i]
        title1 = video1.get('title', '').lower().strip()
        
        if not title1:
            continue
            
        for j, video2 in enumerate(videos[i+1:], i+1):
            if j in processed:
                continue
                
            title2 = video2.get('title', '').lower().strip()
            
            if not title2:
                continue
                
            # Simple similarity check (this is a basic implementation)
            # In a real-world scenario, you might want to use a library like difflib
            words1 = set(title1.split())
            words2 = set(title2.split())
            
            if words1 and words2:
                similarity = len(words1.intersection(words2)) / len(words1.union(words2))
                
                if similarity >= threshold:
                    group.append(j)
                    processed.add(j)
        
        if len(group) > 1:
            similar_groups.append(group)
        processed.add(i)
    
    return similar_groups

def detect_thumbnail_issues(videos):
    """Detect various thumbnail issues"""
    issues = {
        'missing': [],
        'broken_urls': [],
        'suspicious_patterns': [],
        'duplicate_thumbnails': defaultdict(list)
    }
    
    # Check each video for thumbnail issues
    for i, video in enumerate(videos):
        thumbnail = video.get('thumbnail', '')
        
        # Check for missing thumbnails
        if not thumbnail or thumbnail.strip() == "":
            issues['missing'].append(i)
            continue
            
        # Check for broken URLs
        if not is_valid_url(thumbnail):
            issues['broken_urls'].append((i, thumbnail))
            continue
            
        # Check for suspicious patterns
        if 'thumbnail' in thumbnail and 'ttcache.com' not in thumbnail:
            issues['suspicious_patterns'].append((i, thumbnail))
            
        # Group by thumbnail ID to find duplicates
        thumb_id = extract_thumbnail_id(thumbnail)
        if thumb_id:
            issues['duplicate_thumbnails'][thumb_id].append(i)
    
    # Filter out thumbnail IDs that only appear once (not duplicates)
    issues['duplicate_thumbnails'] = {
        thumb_id: indices 
        for thumb_id, indices in issues['duplicate_thumbnails'].items() 
        if len(indices) > 1
    }
    
    return issues

def fix_thumbnails(videos):
    """Fix thumbnail issues in videos"""
    fixed_count = 0
    fixed_videos = []
    
    for video in videos:
        fixed_video = video.copy()
        thumbnail = video.get('thumbnail', '')
        
        # Fix common issues
        if thumbnail:
            # Remove extra whitespace
            thumbnail = thumbnail.strip()
            
            # Fix protocol-relative URLs
            if thumbnail.startswith("//"):
                thumbnail = "https:" + thumbnail
                fixed_video['thumbnail'] = thumbnail
                fixed_count += 1
            # Fix missing protocol
            elif thumbnail.startswith("www."):
                thumbnail = "https://" + thumbnail
                fixed_video['thumbnail'] = thumbnail
                fixed_count += 1
            # Fix common domain issues
            elif "ttcache" in thumbnail and "http" not in thumbnail:
                thumbnail = "https://" + thumbnail
                fixed_video['thumbnail'] = thumbnail
                fixed_count += 1
        
        fixed_videos.append(fixed_video)
    
    return fixed_videos, fixed_count

def advanced_duplicate_detection(videos):
    """Advanced duplicate detection using multiple criteria"""
    duplicates = []
    seen = {}
    
    for i, video in enumerate(videos):
        # Create a comprehensive signature
        title = video.get('title', '').strip().lower()
        url = (video.get('url') or video.get('external_url') or video.get('detail_url') or '').strip()
        thumbnail = video.get('thumbnail', '').strip()
        
        # Create signature based on multiple factors
        signature = f"{title}|{url}|{thumbnail}"
        
        if signature in seen:
            duplicates.append((i, seen[signature], signature))
        else:
            seen[signature] = i
    
    return duplicates

def main():
    """Main function to perform detailed analysis"""
    print("=== WHentai Detailed Video Analysis ===\n")
    
    # File paths
    videos_file = "D:\\Website Project\\WHentai\\WHentai\\videos.json"
    backup_file = "D:\\Website Project\\WHentai\\WHentai\\videos_detailed_backup.json"
    
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
    
    # Detect thumbnail issues
    print("Detecting thumbnail issues...")
    thumbnail_issues = detect_thumbnail_issues(videos)
    
    print(f"Thumbnail issues detected:")
    print(f"  - Missing thumbnails: {len(thumbnail_issues['missing'])}")
    print(f"  - Broken URLs: {len(thumbnail_issues['broken_urls'])}")
    print(f"  - Suspicious patterns: {len(thumbnail_issues['suspicious_patterns'])}")
    print(f"  - Duplicate thumbnails: {len(thumbnail_issues['duplicate_thumbnails'])} groups")
    
    # Fix thumbnails
    print("Fixing thumbnail issues...")
    fixed_videos, fixed_count = fix_thumbnails(videos)
    print(f"Fixed {fixed_count} thumbnail issues")
    
    # Advanced duplicate detection
    print("Performing advanced duplicate detection...")
    duplicates = advanced_duplicate_detection(fixed_videos)
    print(f"Found {len(duplicates)} duplicates")
    
    # Remove duplicates
    if duplicates:
        indices_to_remove = set([dup[0] for dup in duplicates])
        final_videos = []
        for i, video in enumerate(fixed_videos):
            if i not in indices_to_remove:
                final_videos.append(video)
        
        removed_count = len(duplicates)
        print(f"Removed {removed_count} duplicates")
    else:
        final_videos = fixed_videos
        removed_count = 0
    
    # Save the final videos
    print("Saving final videos...")
    if save_videos(final_videos, videos_file):
        print("Successfully saved final videos!")
    else:
        print("Error saving final videos!")
    
    # Show final statistics
    print(f"\n=== Detailed Summary ===")
    print(f"Original video count: {len(videos):,}")
    print(f"Final video count: {len(final_videos):,}")
    print(f"Thumbnail issues fixed: {fixed_count:,}")
    print(f"Duplicates removed: {removed_count:,}")
    print(f"Net change: {len(final_videos) - len(videos):+,}")
    
    # Show some examples of issues found
    if thumbnail_issues['broken_urls']:
        print(f"\nSample broken URLs:")
        for i, (idx, url) in enumerate(thumbnail_issues['broken_urls'][:5]):
            print(f"  {idx}: {url}")
    
    if duplicates:
        print(f"\nSample duplicates:")
        for i, (dup_idx, orig_idx, signature) in enumerate(duplicates[:5]):
            print(f"  Duplicate {dup_idx} matches original {orig_idx}")
            if len(signature) > 50:
                print(f"    Signature: {signature[:50]}...")
            else:
                print(f"    Signature: {signature}")

if __name__ == "__main__":
    main()