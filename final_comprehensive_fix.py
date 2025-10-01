#!/usr/bin/env python3
"""
Final comprehensive fix for thumbnail issues
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

def fix_thumbnail_formatting(videos):
    """Fix thumbnail formatting issues"""
    fixed_count = 0
    fixed_videos = []
    
    for video in videos:
        fixed_video = video.copy()
        thumbnail = video.get('thumbnail', '')
        
        # Ensure thumbnail is properly formatted
        if thumbnail and isinstance(thumbnail, str):
            # Remove any extra whitespace
            thumbnail = thumbnail.strip()
            
            # Fix common URL encoding issues
            thumbnail = thumbnail.replace(' ', '%20')
            
            # Ensure it's a complete URL
            if thumbnail and not thumbnail.startswith('http'):
                # If it looks like it should be a ttcache URL, fix it
                if 'thumbnail' in thumbnail or 'thumber.php' in thumbnail:
                    if not thumbnail.startswith('/'):
                        thumbnail = 'https://c1.ttcache.com/' + thumbnail
                    else:
                        thumbnail = 'https://c1.ttcache.com' + thumbnail
            
            # Update the thumbnail if it changed
            if thumbnail != video.get('thumbnail', ''):
                fixed_video['thumbnail'] = thumbnail
                fixed_count += 1
        
        fixed_videos.append(fixed_video)
    
    return fixed_videos, fixed_count

def main():
    """Main function to apply final comprehensive fix"""
    print("=== WHentai Final Comprehensive Thumbnail Fix ===\n")
    
    # File paths
    videos_file = "videos.json"
    backup_file = "videos_final_fix_backup.json"
    
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
    
    # Fix thumbnail formatting
    print("Fixing thumbnail formatting issues...")
    fixed_videos, fixed_count = fix_thumbnail_formatting(videos)
    
    print(f"Fixed formatting for {fixed_count} videos")
    
    # Save the fixed videos
    print("Saving fixed videos...")
    if save_videos(fixed_videos, videos_file):
        print("Successfully saved fixed videos!")
    else:
        print("Error saving fixed videos!")
    
    # Show final statistics
    print(f"\n=== Summary ===")
    print(f"Total videos processed: {len(videos):,}")
    print(f"Videos with formatting fixes: {fixed_count:,}")
    
    if fixed_count > 0:
        print(f"\nBackup saved as: {backup_file}")
        print("You can restore the original database from this backup if needed.")
        
        print(f"\n=== Next Steps ===")
        print("1. Clear your browser cache completely")
        print("2. Hard refresh all pages (Ctrl+F5 or Cmd+Shift+R)")
        print("3. Test thumbnail display on the website")
        print("4. If issues persist, check browser developer tools for errors")

if __name__ == "__main__":
    main()