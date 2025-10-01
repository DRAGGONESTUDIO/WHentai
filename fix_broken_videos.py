#!/usr/bin/env python3
"""
Script to fix broken video links and thumbnails
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

def get_preferred_url(video):
    """Get the preferred URL for a video (same logic as in JavaScript files)"""
    # Always prioritize external_url over detail_url
    # Only use detail_url as a fallback when external_url is empty or invalid
    has_valid_external_url = 'external_url' in video and \
                           video['external_url'] and \
                           video['external_url'].strip() != '' and \
                           video['external_url'] != '#'
    
    if has_valid_external_url:
        return video['external_url']
    
    # Fallback to detail_url
    return video.get('detail_url', '#')

def fix_broken_videos(videos):
    """Fix broken videos by updating URLs and handling missing links"""
    fixed_count = 0
    thumbnail_fixes = 0
    url_improvements = 0
    fixed_videos = []
    
    for video in videos:
        fixed_video = video.copy()
        changed = False
        
        # Fix thumbnail URLs
        if 'thumbnail' in video and video['thumbnail']:
            original_thumbnail = video['thumbnail']
            fixed_thumbnail = fix_thumbnail_url(original_thumbnail)
            if fixed_thumbnail != original_thumbnail:
                fixed_video['thumbnail'] = fixed_thumbnail
                thumbnail_fixes += 1
                changed = True
        
        # Improve URL handling
        # If external_url is missing but detail_url exists, try to extract a better URL
        has_external_url = 'external_url' in video and video['external_url'] and video['external_url'].strip() != ''
        has_detail_url = 'detail_url' in video and video['detail_url'] and video['detail_url'].strip() != '' and video['detail_url'] != '#'
        
        if not has_external_url and has_detail_url:
            # Try to extract a direct URL from the detail_url if it's a redirector
            detail_url = video['detail_url']
            if 'cartoonpornvideos.com/out/?l=' in detail_url:
                # Try to decode the redirect URL
                try:
                    # Extract the encoded part
                    import urllib.parse
                    parsed_url = urllib.parse.urlparse(detail_url)
                    params = urllib.parse.parse_qs(parsed_url.query)
                    if 'l' in params:
                        encoded_part = params['l'][0]
                        # Try to decode base64 part (simplified approach)
                        # In a real implementation, you'd need proper base64 decoding
                        # For now, we'll just make sure the URL is valid
                        if is_valid_url(detail_url):
                            # Keep the detail_url as external_url if it's valid
                            fixed_video['external_url'] = detail_url
                            url_improvements += 1
                            changed = True
                except Exception as e:
                    # If we can't decode it, keep the detail_url as is
                    pass
        
        # Handle completely missing URLs
        if not has_external_url and not has_detail_url:
            # Create a placeholder or try to reconstruct if possible
            # For now, we'll just ensure there's at least a detail_url
            if 'title' in video and video['title']:
                # Create a basic detail_url from the title
                safe_title = re.sub(r'[^a-zA-Z0-9\-_]', '-', video['title'])[:50]
                fixed_video['detail_url'] = f"https://www.cartoonpornvideos.com/video/{safe_title}"
                url_improvements += 1
                changed = True
        
        if changed:
            fixed_count += 1
            
        fixed_videos.append(fixed_video)
    
    return fixed_videos, fixed_count, thumbnail_fixes, url_improvements

def create_fallback_thumbnails(videos):
    """Create fallback thumbnails for videos with broken thumbnails"""
    fixed_count = 0
    fixed_videos = []
    
    # Common fallback thumbnail patterns
    fallback_domains = [
        "https://placehold.co/300x200/1a1a1a/ff6b6b?text=Thumbnail+Not+Available",
        "https://placehold.co/300x200/2c3e50/ecf0f1?text=No+Image",
        "https://placehold.co/300x200/34495e/bdc3c7?text=Image+Missing"
    ]
    
    for i, video in enumerate(videos):
        fixed_video = video.copy()
        
        # Check if thumbnail is missing or invalid
        if 'thumbnail' not in video or not video['thumbnail'] or video['thumbnail'].strip() == '':
            # Assign a fallback thumbnail
            fallback_index = i % len(fallback_domains)
            fixed_video['thumbnail'] = fallback_domains[fallback_index]
            fixed_count += 1
        elif video['thumbnail'].endswith('/thumber.php'):
            # Replace generic thumber.php with a more descriptive placeholder
            fallback_index = i % len(fallback_domains)
            fixed_video['thumbnail'] = fallback_domains[fallback_index]
            fixed_count += 1
            
        fixed_videos.append(fixed_video)
    
    return fixed_videos, fixed_count

def main():
    """Main function to fix broken videos"""
    print("=== WHentai Broken Video Fixer ===\n")
    
    # File paths
    videos_file = "videos.json"
    backup_file = "videos_backup_before_fix.json"
    
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
    
    # Fix broken videos
    print("Fixing broken videos...")
    fixed_videos, fixed_count, thumbnail_fixes, url_improvements = fix_broken_videos(videos)
    
    print(f"Fixed {fixed_count} videos")
    print(f"Thumbnail fixes: {thumbnail_fixes}")
    print(f"URL improvements: {url_improvements}")
    
    # Create fallback thumbnails for remaining issues
    print("Creating fallback thumbnails...")
    final_videos, fallback_count = create_fallback_thumbnails(fixed_videos)
    
    print(f"Created fallback thumbnails for {fallback_count} videos")
    
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
    print(f"Thumbnail fixes: {thumbnail_fixes:,}")
    print(f"URL improvements: {url_improvements:,}")
    print(f"Fallback thumbnails created: {fallback_count:,}")
    
    if fixed_count > 0:
        print(f"\nBackup saved as: {backup_file}")
        print("You can restore the original database from this backup if needed.")

if __name__ == "__main__":
    main()