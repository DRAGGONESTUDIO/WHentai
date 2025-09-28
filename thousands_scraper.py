#!/usr/bin/env python3
"""
Thousands Videos Scraper for WHentai - Aggressively adds thousands of videos
"""

import json
import subprocess
import sys
import time
from datetime import datetime

def run_enhanced_scraper_pass(pass_number):
    """
    Run the enhanced scraper with increased limits for one pass
    """
    print(f"\n=== Running Enhanced Scraper Pass #{pass_number} ===")
    try:
        # Modify the enhanced scraper temporarily to increase limits
        with open('enhanced_scraper.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Increase limits for this pass
        content = content.replace(
            'MAX_ITEMS_PER_SOURCE = 3000',
            'MAX_ITEMS_PER_SOURCE = 5000'
        )
        content = content.replace(
            'MAX_PAGES_PER_SOURCE = 30',
            'MAX_PAGES_PER_SOURCE = 50'
        )
        
        with open('enhanced_scraper_temp.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Run the modified scraper
        result = subprocess.run([
            sys.executable, 
            'enhanced_scraper_temp.py'
        ], capture_output=True, text=True, timeout=600)  # 10 minute timeout
        
        # Restore original file
        with open('enhanced_scraper.py', 'w', encoding='utf-8') as f:
            f.write(content.replace(
                'MAX_ITEMS_PER_SOURCE = 5000',
                'MAX_ITEMS_PER_SOURCE = 3000'
            ).replace(
                'MAX_PAGES_PER_SOURCE = 50',
                'MAX_PAGES_PER_SOURCE = 30'
            ))
        
        # Clean up temp file
        import os
        if os.path.exists('enhanced_scraper_temp.py'):
            os.remove('enhanced_scraper_temp.py')
        
        if result.returncode == 0:
            print(f"✓ Enhanced Scraper Pass #{pass_number} completed successfully")
            # Extract number of videos added from output
            lines = result.stdout.split('\n')
            for line in lines:
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
            print(f"✗ Enhanced Scraper Pass #{pass_number} failed:")
            print(result.stderr[-500:])  # Last 500 chars of error
            return 0
    except subprocess.TimeoutExpired:
        print(f"✗ Enhanced Scraper Pass #{pass_number} timed out")
        return 0
    except Exception as e:
        print(f"✗ Error running Enhanced Scraper Pass #{pass_number}: {e}")
        return 0

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

def main():
    """
    Main function to add thousands of videos
    """
    print(f"=== WHentai Thousands Videos Scraper - {datetime.now().isoformat()} ===")
    
    # Get initial video count
    initial_count = get_video_count()
    print(f"Initial video count: {initial_count}")
    
    # Run multiple passes to add thousands of videos
    total_added = 0
    passes = 5  # Run 5 passes to add thousands of videos
    
    for i in range(passes):
        # Add a delay between passes to be respectful to the server
        if i > 0:
            print(f"\nWaiting 30 seconds before next pass...")
            time.sleep(30)
        
        # Run one pass
        videos_added = run_enhanced_scraper_pass(i + 1)
        total_added += videos_added
        print(f"Pass #{i+1} added {videos_added} videos")
        
        # Show current progress
        current_count = get_video_count()
        print(f"Current total: {current_count} videos")
        
        # If no videos were added, we might be done
        if videos_added == 0:
            print("No new videos added in this pass. May have reached the limit.")
            # Try one more pass to be sure
            if i < passes - 1:  # If not the last pass
                print("Continuing to next pass...")
                continue
            else:
                break
    
    # Final count
    final_count = get_video_count()
    actual_added = final_count - initial_count
    
    # Report results
    print("\n=== Thousands Videos Scraping Summary ===")
    print(f"Initial video count: {initial_count}")
    print(f"Final video count: {final_count}")
    print(f"Actual videos added: {actual_added}")
    print(f"Target passes: {passes}")
    
    # Save summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "initial_count": initial_count,
        "final_count": final_count,
        "videos_added": actual_added,
        "passes_completed": passes,
        "status": "completed"
    }
    
    with open('thousands_scraping_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nScraping completed! Added {actual_added} new videos.")
    print("Check thousands_scraping_summary.json for detailed results.")
    
    return actual_added > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)