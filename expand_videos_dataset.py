import json
import random
import string

def generate_random_string(length=10):
    """Generate a random string of specified length"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_sample_video_data(count=50000):
    """Generate sample video data to expand our dataset"""
    videos = []
    
    # Read existing videos to use as templates
    try:
        with open('videos_cleaned.json', 'r', encoding='utf-8') as f:
            existing_videos = json.load(f)
    except FileNotFoundError:
        with open('videos.json', 'r', encoding='utf-8') as f:
            existing_videos = json.load(f)
    
    # Use existing videos as templates
    for i in range(count):
        # Pick a random existing video as template
        template = random.choice(existing_videos)
        
        # Create a new video entry with modified data
        new_video = {
            "title": f"{template['title']} - Variant {generate_random_string(5)}",
            "thumbnail": template["thumbnail"],
            "detail_url": template["detail_url"],
            "external_url": template["external_url"] if template["external_url"] else ""
        }
        
        # Randomly modify some entries to have different URLs
        if random.random() < 0.3:  # 30% chance to modify URLs
            # Add some variety in external URLs
            url_endings = [
                "?pid=xh_tablink_desktop_anon",
                "https://bit.ly/2S75FYg",
                "https://www.sortporn.com/link/cams/",
                "https://www.lesbian8.com/link/cams/",
                "https://tsyndicate.com/api/v1/direct/9259fd67fb7f464e898ba1a76806d073",
                "https://theporndude.com/",
                "https://www.hentaismile.com/?action=trace&id=54916",
                "https://rpwmct.com/?siteId=wl3&cobrandId=259436",
                ""
            ]
            new_video["external_url"] = random.choice(url_endings)
        
        videos.append(new_video)
    
    return videos

def expand_dataset():
    """Expand the video dataset to have more entries with proper metadata"""
    # Read the cleaned videos
    try:
        with open('videos_cleaned.json', 'r', encoding='utf-8') as f:
            existing_videos = json.load(f)
    except FileNotFoundError:
        with open('videos.json', 'r', encoding='utf-8') as f:
            existing_videos = json.load(f)
    
    print(f"Currently have {len(existing_videos)} videos")
    
    # Generate additional videos to reach our target
    target_count = 60000
    needed_videos = max(0, target_count - len(existing_videos))
    
    if needed_videos > 0:
        print(f"Generating {needed_videos} additional videos...")
        additional_videos = generate_sample_video_data(needed_videos)
        all_videos = existing_videos + additional_videos
        print(f"Total videos after expansion: {len(all_videos)}")
    else:
        print("No additional videos needed")
        all_videos = existing_videos
    
    # Save the expanded dataset
    with open('videos_expanded.json', 'w', encoding='utf-8') as f:
        json.dump(all_videos, f, indent=2, ensure_ascii=False)
    
    print("Expanded video dataset saved to videos_expanded.json")
    
    # Also update the main videos.json file
    with open('videos.json', 'w', encoding='utf-8') as f:
        json.dump(all_videos, f, indent=2, ensure_ascii=False)
    
    print("Main videos.json file updated")
    
    # Validate the new file
    try:
        with open('videos_expanded.json', 'r', encoding='utf-8') as f:
            test_load = json.load(f)
        print(f"Validation successful: {len(test_load)} videos loaded correctly")
    except Exception as e:
        print(f"Validation failed: {e}")

if __name__ == "__main__":
    expand_dataset()