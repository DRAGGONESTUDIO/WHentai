#!/usr/bin/env python3
"""
Test script for the WHentai scrapers
"""

import subprocess
import sys
import json

def test_basic_scraper():
    """Test the basic cartoon scraper"""
    print("Testing basic cartoon scraper...")
    try:
        result = subprocess.run([
            sys.executable, 
            'cartoon_scraper.py'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✓ Basic scraper test passed")
            return True
        else:
            print("✗ Basic scraper test failed:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("✗ Basic scraper test timed out")
        return False
    except Exception as e:
        print(f"✗ Basic scraper test error: {e}")
        return False

def test_enhanced_scraper():
    """Test the enhanced scraper"""
    print("Testing enhanced scraper...")
    try:
        result = subprocess.run([
            sys.executable, 
            'enhanced_scraper.py'
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✓ Enhanced scraper test passed")
            return True
        else:
            print("✗ Enhanced scraper test failed:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("✗ Enhanced scraper test timed out")
        return False
    except Exception as e:
        print(f"✗ Enhanced scraper test error: {e}")
        return False

def test_automated_scraper():
    """Test the automated scraper"""
    print("Testing automated scraper...")
    try:
        result = subprocess.run([
            sys.executable, 
            'automated_scraper.py'
        ], capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0:
            print("✓ Automated scraper test passed")
            return True
        else:
            print("✗ Automated scraper test failed:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("✗ Automated scraper test timed out")
        return False
    except Exception as e:
        print(f"✗ Automated scraper test error: {e}")
        return False

def check_videos_file():
    """Check if videos.json file exists and is valid"""
    print("Checking videos.json file...")
    try:
        with open('videos.json', 'r', encoding='utf-8') as f:
            videos = json.load(f)
        
        print(f"✓ Found {len(videos)} videos in videos.json")
        
        # Check first video structure
        if videos:
            first_video = videos[0]
            required_fields = ['title', 'thumbnail', 'detail_url']
            missing_fields = [field for field in required_fields if field not in first_video]
            
            if not missing_fields:
                print("✓ Video structure is valid")
                return True
            else:
                print(f"✗ Missing fields in video structure: {missing_fields}")
                return False
        else:
            print("⚠ No videos found in file")
            return True
    except FileNotFoundError:
        print("✗ videos.json file not found")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in videos.json: {e}")
        return False
    except Exception as e:
        print(f"✗ Error checking videos.json: {e}")
        return False

def main():
    """Run all tests"""
    print("=== WHentai Scraper Test Suite ===\n")
    
    tests = [
        check_videos_file,
        test_basic_scraper,
        test_enhanced_scraper,
        test_automated_scraper
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print(f"=== Test Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)