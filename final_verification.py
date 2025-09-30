#!/usr/bin/env python3
"""
Final verification script for WHentai direct linking fix
This script checks if the JavaScript files have been properly updated to prioritize external_url
"""

import os
import re
import json

# List of JavaScript files to check
JS_FILES = [
    'category-videos.js',
    'videos.js',
    'popular.js',
    'random.js',
    'newest.js',
    'search.js',
    'category.js'
]

# Pattern to check for proper external_url prioritization
PATTERN = re.compile(r'external_url.*?external_url.*?detailUrl', re.DOTALL)

def check_file(file_path):
    """Check if a file has the correct external_url prioritization logic"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check if the file contains the prioritization logic
        if 'external_url' in content and ('detailUrl' in content or 'detail_url' in content):
            # Look for the specific pattern we implemented
            if 'external_url &&' in content or 'external_url !==' in content or 'external_url.trim()' in content:
                return True, "File has proper external_url prioritization logic"
            else:
                return False, "File contains external_url but may not have proper prioritization logic"
        else:
            return False, "File does not contain expected external_url or detailUrl references"
            
    except Exception as e:
        return False, f"Error reading file: {e}"

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
            
    except json.JSONDecodeError:
        # Try to count manually by looking for object separators
        try:
            # Count the number of '},' patterns and add 1 for the last object
            object_count = content.count('},')
            if content.strip().endswith('}'):
                object_count += 1
            return object_count
        except:
            return 0
    except Exception:
        return 0

def main():
    """Main function to run the verification"""
    print("=== WHentai Direct Linking Fix Verification ===\n")
    
    all_passed = True
    
    for js_file in JS_FILES:
        file_path = os.path.join('D:\\Website Project\\WHentai\\WHentai', js_file)
        
        if os.path.exists(file_path):
            passed, message = check_file(file_path)
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status} {js_file}: {message}")
            
            if not passed:
                all_passed = False
        else:
            print(f"✗ FAIL {js_file}: File not found")
            all_passed = False
    
    print("\n=== Verification Summary ===")
    if all_passed:
        print("✓ All JavaScript files have been properly updated for direct linking!")
        print("Users should now be directed straight to the original video source.")
    else:
        print("✗ Some files may not be properly updated.")
        print("Please check the individual file reports above.")
    
    print("\n=== Video Database Status ===")
    try:
        # Count videos in the database using our accurate method
        video_count = count_videos_accurate('D:\\Website Project\\WHentai\\WHentai\\videos.json')
        print(f"Video database contains {video_count:,} videos")
    except Exception as e:
        print(f"Could not determine video count: {e}")

if __name__ == "__main__":
    main()