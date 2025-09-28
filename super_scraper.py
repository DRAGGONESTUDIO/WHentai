#!/usr/bin/env python3
"""
Super Scraper for WHentai - Adds thousands of videos by running multiple scraping passes
"""

import json
import subprocess
import sys
import time
from datetime import datetime

def get_video_count():
    """
    Get the current video count from videos.json
    """
    try:
        with open('videos.json', 'r', encoding='utf-8') as f:
            videos = json.load(f)
        return len(videos)
    except Exception as e:
        print(f"Error getting video count: {e}")
        return 0

def run_enhanced_scraper():
    """
    Run the enhanced scraper to add more videos
    """
    print("Running enhanced scraper...")
    try:
        result = subprocess.run([
            sys.executable, 
            'enhanced_scraper.py'
        ], capture_output=True, text=True, timeout=900)  # 15 minute timeout
        
        if result.returncode == 0:
            print("Enhanced scraper completed successfully")
            # Extract the number of videos from the output
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'Saving' in line and 'videos to' in line:
                    # Extract number before "videos to"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'videos':
                            try:
                                count = int(parts[i-1])
                                return count
                            except:
                                pass
            return 0
        else:
            print("Enhanced scraper failed:")
            # Print last 1000 characters of error output
            print(result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)
            return 0
    except subprocess.TimeoutExpired:
        print("Enhanced scraper timed out")
        return 0
    except Exception as e:
        print(f"Error running enhanced scraper: {e}")
        return 0

def update_categories():
    """
    Run the category tagging script to ensure all videos have categories
    """
    print("Updating video categories...")
    try:
        result = subprocess.run([
            sys.executable, 
            'add_category_tags.py'
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            print("Category update completed successfully")
            return True
        else:
            print("Category update failed:")
            print(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("Category update timed out")
        return False
    except Exception as e:
        print(f"Error updating categories: {e}")
        return False

def main():
    """
    Main function to add thousands of videos
    """
    print(f"=== WHentai Super Scraper - {datetime.now().isoformat()} ===")
    
    # Get initial video count
    initial_count = get_video_count()
    print(f"Initial video count: {initial_count}")
    
    # Run multiple passes to add thousands of videos
    total_added = 0
    passes = 10  # Run 10 passes to maximize video addition
    
    for i in range(passes):
        print(f"\n=== Super Scraper Pass #{i+1}/{passes} ===")
        
        # Add a delay between passes to be respectful to the server
        if i > 0:
            print(f"Waiting 60 seconds before next pass...")
            time.sleep(60)
        
        # Run the enhanced scraper
        videos_after_pass = run_enhanced_scraper()
        
        # Check how many videos were added in this pass
        current_count = get_video_count()
        videos_added_this_pass = current_count - (initial_count + total_added)
        total_added += videos_added_this_pass
        
        print(f"Pass #{i+1} added {videos_added_this_pass} videos")
        print(f"Total added so far: {total_added} videos")
        print(f"Current total: {current_count} videos")
        
        # If no videos were added, we might be done
        if videos_added_this_pass == 0:
            print("No new videos added in this pass.")
            # Try one more pass to be sure
            if i < passes - 1:  # If not the last pass
                print("Continuing to next pass...")
                continue
            else:
                print("Ending scraping early as no new videos are being found.")
                break
    
    # Final count
    final_count = get_video_count()
    actual_added = final_count - initial_count
    
    # Update categories for all new videos
    print("\n=== Updating Categories for New Videos ===")
    update_categories()
    
    # Report results
    print("\n=== Super Scraper Summary ===")
    print(f"Initial video count: {initial_count}")
    print(f"Final video count: {final_count}")
    print(f"Total videos added: {actual_added}")
    print(f"Target passes: {passes}")
    print(f"Completed passes: {passes}")
    
    # Save summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "initial_count": initial_count,
        "final_count": final_count,
        "videos_added": actual_added,
        "passes_completed": passes,
        "status": "completed"
    }
    
    with open('super_scraping_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nSuper scraping completed! Added {actual_added} new videos.")
    print("Check super_scraping_summary.json for detailed results.")
    
    return actual_added > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)