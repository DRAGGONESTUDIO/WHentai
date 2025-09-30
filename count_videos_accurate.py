#!/usr/bin/env python3
"""
Accurate video counter for WHentai
This script counts the number of video objects in the videos.json file
"""

import json
import os

def count_videos_accurate(file_path):
    """Count videos in JSON file accurately"""
    content = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        # Fix any issues with the JSON format
        if content.endswith(','):
            content = content[:-1] + ']'
            
        # Parse the JSON
        data = json.loads(content)
        
        # Count the video objects
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            # If it's a dict, look for a videos key or count all items
            if 'videos' in data:
                return len(data['videos'])
            else:
                return len(data)
        else:
            return 0
            
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        # Try to count manually by looking for object separators
        try:
            # Count the number of '},' patterns and add 1 for the last object
            object_count = content.count('},')
            if content.strip().endswith('}'):
                object_count += 1
            return object_count
        except:
            return 0
    except Exception as e:
        print(f"Error counting videos: {e}")
        return 0

def main():
    """Main function"""
    file_path = "D:\\Website Project\\WHentai\\WHentai\\videos.json"
    
    if os.path.exists(file_path):
        count = count_videos_accurate(file_path)
        print(f"Total videos in {file_path}: {count:,}")
    else:
        print(f"File not found: {file_path}")
        
    # Also check other video files
    other_files = [
        "D:\\Website Project\\WHentai\\WHentai\\videos_sample.json",
        "D:\\Website Project\\WHentai\\WHentai\\videos_cleaned.json",
        "D:\\Website Project\\WHentai\\WHentai\\videos_expanded.json"
    ]
    
    for other_file in other_files:
        if os.path.exists(other_file):
            count = count_videos_accurate(other_file)
            print(f"Total videos in {other_file}: {count:,}")

if __name__ == "__main__":
    main()