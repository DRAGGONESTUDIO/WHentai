#!/usr/bin/env python3
"""
Automated Scraper for WHentai - Runs periodically to add recent videos
This script is designed to be run by GitHub Actions or other CI/CD systems
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta

def load_existing_videos():
    """Load existing videos from videos.json"""
    if os.path.exists('videos.json'):
        try:
            with open('videos.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading existing videos: {e}")
            return []
    return []

def get_recent_videos(videos, hours=24):
    """Get videos scraped in the last N hours"""
    if not videos:
        return []
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    recent_videos = []
    
    for video in videos:
        scraped_at = video.get('scraped_at')
        if scraped_at:
            try:
                scraped_time = datetime.fromisoformat(scraped_at.replace('Z', '+00:00'))
                if scraped_time > cutoff_time:
                    recent_videos.append(video)
            except ValueError:
                # If we can't parse the date, skip this video
                continue
    
    return recent_videos

def run_enhanced_scraper():
    """Run the enhanced scraper to get more videos"""
    try:
        print("Running enhanced scraper...")
        result = subprocess.run([
            sys.executable, 
            'enhanced_scraper.py'
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            print("Enhanced scraper completed successfully")
            print(result.stdout)
            return True
        else:
            print("Enhanced scraper failed:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("Enhanced scraper timed out")
        return False
    except Exception as e:
        print(f"Error running enhanced scraper: {e}")
        return False

def run_max_videos_scraper():
    """Run the maximum videos scraper to get even more videos"""
    try:
        print("Running maximum videos scraper...")
        result = subprocess.run([
            sys.executable, 
            'max_videos_scraper.py'
        ], capture_output=True, text=True, timeout=600)  # 10 minute timeout
        
        if result.returncode == 0:
            print("Maximum videos scraper completed successfully")
            print(result.stdout)
            return True
        else:
            print("Maximum videos scraper failed:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("Maximum videos scraper timed out")
        return False
    except Exception as e:
        print(f"Error running maximum videos scraper: {e}")
        return False

def update_categories():
    """Run the category tagging script to ensure all videos have categories"""
    try:
        print("Updating video categories...")
        result = subprocess.run([
            sys.executable, 
            'add_category_tags.py'
        ], capture_output=True, text=True, timeout=120)  # 2 minute timeout
        
        if result.returncode == 0:
            print("Category update completed successfully")
            print(result.stdout)
            return True
        else:
            print("Category update failed:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("Category update timed out")
        return False
    except Exception as e:
        print(f"Error updating categories: {e}")
        return False

def main():
    """Main function to run the automated scraping process"""
    print(f"=== WHentai Automated Scraper - {datetime.now().isoformat()} ===")
    
    # Load existing videos
    existing_videos = load_existing_videos()
    print(f"Found {len(existing_videos)} existing videos")
    
    # Get recent videos before scraping
    recent_before = get_recent_videos(existing_videos, 24)
    print(f"Found {len(recent_before)} recent videos (last 24 hours)")
    
    # Try to run the maximum videos scraper first (it includes the enhanced scraper)
    # If it doesn't exist or fails, fall back to the enhanced scraper
    success = False
    if os.path.exists('max_videos_scraper.py'):
        success = run_max_videos_scraper()
    
    if not success and os.path.exists('enhanced_scraper.py'):
        success = run_enhanced_scraper()
    
    # If neither scraper worked, try the basic scraper
    if not success and os.path.exists('cartoon_scraper.py'):
        try:
            print("Running basic cartoon scraper...")
            result = subprocess.run([
                sys.executable, 
                'cartoon_scraper.py'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("Basic scraper completed successfully")
                success = True
            else:
                print("Basic scraper failed:")
                print(result.stderr)
        except Exception as e:
            print(f"Error running basic scraper: {e}")
    
    if success:
        # Load updated videos
        updated_videos = load_existing_videos()
        print(f"Updated to {len(updated_videos)} total videos")
        
        # Get recent videos after scraping
        recent_after = get_recent_videos(updated_videos, 24)
        new_recent_videos = len(recent_after) - len(recent_before)
        print(f"Added {new_recent_videos} new recent videos")
        
        # Update categories for new videos
        if update_categories():
            print("Categories updated successfully")
        else:
            print("Failed to update categories")
        
        # Report results
        print("\n=== Scraping Summary ===")
        print(f"Total videos: {len(updated_videos)}")
        print(f"New videos added: {len(updated_videos) - len(existing_videos)}")
        print(f"Recent videos (24h): {len(recent_after)}")
        
        # Save summary to a file for GitHub Actions
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_videos": len(updated_videos),
            "new_videos": len(updated_videos) - len(existing_videos),
            "recent_videos": len(recent_after),
            "status": "success"
        }
        
        with open('scraping_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        return True
    else:
        print("All scraping attempts failed!")
        
        # Save error summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_videos": len(existing_videos),
            "new_videos": 0,
            "recent_videos": len(recent_before),
            "status": "failed"
        }
        
        with open('scraping_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)