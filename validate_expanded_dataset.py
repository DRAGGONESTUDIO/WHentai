import json

def validate_expanded_dataset():
    """Validate that all videos in the expanded dataset have proper metadata"""
    
    # Load the expanded dataset
    with open('videos.json', 'r', encoding='utf-8') as f:
        videos = json.load(f)
    
    print(f"Validating {len(videos)} videos...")
    
    # Validation counters
    valid_videos = 0
    invalid_videos = 0
    videos_with_external_url = 0
    videos_with_detail_url = 0
    videos_with_both_urls = 0
    videos_with_no_urls = 0
    
    # Check each video for proper structure
    for i, video in enumerate(videos):
        # Check if video has required fields
        has_title = 'title' in video and isinstance(video['title'], str) and len(video['title'].strip()) > 0
        has_thumbnail = 'thumbnail' in video and isinstance(video['thumbnail'], str) and len(video['thumbnail'].strip()) > 0
        has_detail_url = 'detail_url' in video and isinstance(video['detail_url'], str)
        has_external_url = 'external_url' in video and isinstance(video['external_url'], str)
        
        # Validate URLs
        detail_url_valid = has_detail_url and len(video['detail_url'].strip()) > 0
        external_url_valid = has_external_url and len(video['external_url'].strip()) > 0
        
        # Count URL statistics
        if detail_url_valid:
            videos_with_detail_url += 1
        if external_url_valid:
            videos_with_external_url += 1
        if detail_url_valid and external_url_valid:
            videos_with_both_urls += 1
        if not detail_url_valid and not external_url_valid:
            videos_with_no_urls += 1
        
        # Check if video is valid (must have title, thumbnail, and at least one URL)
        if has_title and has_thumbnail and (detail_url_valid or external_url_valid):
            valid_videos += 1
        else:
            invalid_videos += 1
            if invalid_videos <= 10:  # Show first 10 invalid videos
                print(f"Invalid video at index {i}:")
                print(f"  Title: {video.get('title', 'MISSING')}")
                print(f"  Thumbnail: {video.get('thumbnail', 'MISSING')}")
                print(f"  Detail URL: {video.get('detail_url', 'MISSING')}")
                print(f"  External URL: {video.get('external_url', 'MISSING')}")
                print()
    
    # Print validation results
    print("\nValidation Results:")
    print(f"Valid videos: {valid_videos}")
    print(f"Invalid videos: {invalid_videos}")
    print(f"Videos with external_url: {videos_with_external_url}")
    print(f"Videos with detail_url: {videos_with_detail_url}")
    print(f"Videos with both URLs: {videos_with_both_urls}")
    print(f"Videos with no URLs: {videos_with_no_urls}")
    
    # Show some sample valid videos
    print("\nSample of valid videos:")
    sample_count = 0
    for video in videos:
        if sample_count >= 5:
            break
            
        has_title = 'title' in video and isinstance(video['title'], str) and len(video['title'].strip()) > 0
        has_thumbnail = 'thumbnail' in video and isinstance(video['thumbnail'], str) and len(video['thumbnail'].strip()) > 0
        has_detail_url = 'detail_url' in video and isinstance(video['detail_url'], str) and len(video['detail_url'].strip()) > 0
        has_external_url = 'external_url' in video and isinstance(video['external_url'], str)
        
        if has_title and has_thumbnail and (has_detail_url or has_external_url):
            print(f"\n{sample_count + 1}. Title: {video['title'][:100]}{'...' if len(video['title']) > 100 else ''}")
            print(f"   Thumbnail: {video['thumbnail']}")
            if has_detail_url:
                print(f"   Detail URL: {video['detail_url'][:100]}{'...' if len(video['detail_url']) > 100 else ''}")
            if has_external_url and video['external_url']:
                print(f"   External URL: {video['external_url']}")
            sample_count += 1
    
    # Check if all videos are valid
    if invalid_videos == 0:
        print("\n✅ All videos have proper metadata!")
        return True
    else:
        print(f"\n❌ Found {invalid_videos} videos with missing or invalid metadata")
        return False

if __name__ == "__main__":
    validate_expanded_dataset()