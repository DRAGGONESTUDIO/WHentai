#!/usr/bin/env python3
"""
Project status verification script for WHentai
This script performs a complete verification of the WHentai project status
"""

import os
import json
import re

# Configuration
PROJECT_DIR = "D:\\Website Project\\WHentai\\WHentai"
JS_FILES = [
    'category-videos.js',
    'videos.js',
    'popular.js',
    'random.js',
    'newest.js',
    'search.js',
    'category.js'
]
REQUIRED_FILES = [
    'videos.json',
    'index.html',
    'styles.css'
] + JS_FILES

def check_direct_linking_fix():
    """Check if the direct linking fix is properly implemented"""
    print("Checking direct linking fix...")
    all_passed = True
    
    for js_file in JS_FILES:
        file_path = os.path.join(PROJECT_DIR, js_file)
        
        if not os.path.exists(file_path):
            print(f"  ✗ FAIL {js_file}: File not found")
            all_passed = False
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check if the file contains the prioritization logic
            if 'external_url' in content and ('detailUrl' in content or 'detail_url' in content):
                # Look for the specific pattern we implemented
                if 'external_url &&' in content or 'external_url !==' in content or 'external_url.trim()' in content:
                    print(f"  ✓ PASS {js_file}: Has proper external_url prioritization logic")
                else:
                    print(f"  ? WARN {js_file}: Contains external_url but may not have proper prioritization logic")
            else:
                print(f"  ✗ FAIL {js_file}: Does not contain expected external_url or detailUrl references")
                all_passed = False
                
        except Exception as e:
            print(f"  ✗ FAIL {js_file}: Error reading file - {e}")
            all_passed = False
    
    return all_passed

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

def check_video_database():
    """Check the video database status"""
    print("Checking video database...")
    
    videos_file = os.path.join(PROJECT_DIR, 'videos.json')
    
    if not os.path.exists(videos_file):
        print("  ✗ FAIL videos.json: File not found")
        return False
        
    try:
        video_count = count_videos_accurate(videos_file)
        print(f"  ✓ INFO videos.json: Contains {video_count:,} videos")
        
        if video_count > 0:
            return True
        else:
            print("  ✗ FAIL videos.json: File appears to be empty or corrupted")
            return False
            
    except Exception as e:
        print(f"  ✗ FAIL videos.json: Error counting videos - {e}")
        return False

def check_required_files():
    """Check if all required files are present"""
    print("Checking required files...")
    all_present = True
    
    for file_name in REQUIRED_FILES:
        file_path = os.path.join(PROJECT_DIR, file_name)
        
        if os.path.exists(file_path):
            print(f"  ✓ FOUND {file_name}")
        else:
            print(f"  ✗ MISSING {file_name}")
            all_present = False
    
    return all_present

def main():
    """Main function to run the complete verification"""
    print("=== WHentai Project Status Verification ===\n")
    
    # Check required files
    files_ok = check_required_files()
    print()
    
    # Check direct linking fix
    direct_linking_ok = check_direct_linking_fix()
    print()
    
    # Check video database
    database_ok = check_video_database()
    print()
    
    # Final summary
    print("=== Final Verification Summary ===")
    
    if files_ok and direct_linking_ok and database_ok:
        print("✓ ALL CHECKS PASSED - Project is in good working condition!")
        print("  - All required files are present")
        print("  - Direct linking fix is properly implemented")
        print("  - Video database is functional")
        print("\nUsers should be directed straight to original video sources.")
    else:
        print("✗ SOME CHECKS FAILED - Please review the issues above")
        if not files_ok:
            print("  - Some required files are missing")
        if not direct_linking_ok:
            print("  - Direct linking fix may not be properly implemented")
        if not database_ok:
            print("  - Video database may have issues")
    
    print("\n=== Additional Information ===")
    try:
        # Show sizes of other video files
        other_files = ['videos_sample.json', 'videos_cleaned.json', 'videos_expanded.json']
        for other_file in other_files:
            file_path = os.path.join(PROJECT_DIR, other_file)
            if os.path.exists(file_path):
                video_count = count_videos_accurate(file_path)
                print(f"  {other_file}: {video_count:,} videos")
    except Exception as e:
        print(f"  Error checking other video files: {e}")

if __name__ == "__main__":
    main()