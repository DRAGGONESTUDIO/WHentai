#!/usr/bin/env python3
"""
Maximum Videos Scraper for WHentai - Combines multiple scraping strategies
This script runs all available scrapers to maximize the number of videos
"""

import subprocess
import sys
import json
import os
from datetime import datetime

def run_scraper(scraper_name, script_name):
    """
    Run a scraper script and return the result
    """
    print(f"\n=== Running {scraper_name} ===")
    try:
        result = subprocess.run([
            sys.executable, 
            script_name
        ], capture_output=True, text=True, timeout=600)  # 10 minute timeout
        
        if result.returncode == 0:
            print(f"✓ {scraper_name} completed successfully")
            print(result.stdout)
            return True
        else:
            print(f"✗ {scraper_name} failed:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print(f"✗ {scraper_name} timed out")
        return False
    except Exception as e:
        print(f"✗ Error running {scraper_name}: {e}")
        return False

def get_video_count():
    """
    Get the current video count from videos.json
    """
    try:
        if os.path.exists('videos.json'):
            with open('videos.json', 'r', encoding='utf-8') as f:
                videos = json.load(f)
            return len(videos)
        else:
            return 0
    except Exception as e:
        print(f"Error getting video count: {e}")
        return 0

def update_categories():
    """
    Run the category tagging script to ensure all videos have categories
    """
    print("\n=== Updating Video Categories ===")
    try:
        result = subprocess.run([
            sys.executable, 
            'add_category_tags.py'
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            print("✓ Category update completed successfully")
            print(result.stdout)
            return True
        else:
            print("✗ Category update failed:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("✗ Category update timed out")
        return False
    except Exception as e:
        print(f"✗ Error updating categories: {e}")
        return False

def main():
    """
    Main function to run all scrapers and maximize video count
    """
    print(f"=== WHentai Maximum Videos Scraper - {datetime.now().isoformat()} ===")
    
    # Get initial video count
    initial_count = get_video_count()
    print(f"Initial video count: {initial_count}")
    
    # List of scrapers to run
    scrapers = [
        ("Enhanced Scraper", "enhanced_scraper.py"),
        ("Additional Category Scraper", "additional_scraper.py")
    ]
    
    # Run each scraper
    successful_scrapers = []
    failed_scrapers = []
    
    for scraper_name, script_name in scrapers:
        if os.path.exists(script_name):
            if run_scraper(scraper_name, script_name):
                successful_scrapers.append(scraper_name)
            else:
                failed_scrapers.append(scraper_name)
        else:
            print(f"Skipping {scraper_name} - script not found: {script_name}")
            failed_scrapers.append(scraper_name)
    
    # Get final video count
    final_count = get_video_count()
    added_videos = final_count - initial_count
    
    # Update categories for new videos
    if added_videos > 0:
        update_categories()
    
    # Report results
    print("\n=== Scraping Summary ===")
    print(f"Initial video count: {initial_count}")
    print(f"Final video count: {final_count}")
    print(f"Videos added: {added_videos}")
    print(f"Successful scrapers: {', '.join(successful_scrapers) if successful_scrapers else 'None'}")
    print(f"Failed scrapers: {', '.join(failed_scrapers) if failed_scrapers else 'None'}")
    
    # Save summary to a file
    summary = {
        "timestamp": datetime.now().isoformat(),
        "initial_count": initial_count,
        "final_count": final_count,
        "added_videos": added_videos,
        "successful_scrapers": successful_scrapers,
        "failed_scrapers": failed_scrapers,
        "status": "completed" if not failed_scrapers or successful_scrapers else "partial"
    }
    
    with open('max_scraping_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    return len(successful_scrapers) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)