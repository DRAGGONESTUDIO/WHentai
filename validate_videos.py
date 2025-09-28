import json

def validate_videos():
    try:
        # Read the videos.json file
        with open('videos.json', 'r', encoding='utf-8') as f:
            videos = json.load(f)
        
        print(f"Total videos: {len(videos)}")
        
        # Validation counters
        valid_videos = 0
        invalid_videos = 0
        videos_with_external_url = 0
        videos_with_detail_url = 0
        videos_with_both_urls = 0
        videos_with_no_urls = 0
        
        # Validate each video
        valid_videos_array = []
        
        for video in videos:
            has_external_url = 'external_url' in video and video['external_url'] and video['external_url'].strip() != ''
            has_detail_url = 'detail_url' in video and video['detail_url'] and video['detail_url'].strip() != '' and video['detail_url'] != '#'
            
            # Count URL statistics
            if has_external_url:
                videos_with_external_url += 1
            if has_detail_url:
                videos_with_detail_url += 1
            if has_external_url and has_detail_url:
                videos_with_both_urls += 1
            if not has_external_url and not has_detail_url:
                videos_with_no_urls += 1
                continue  # Skip videos with no URLs
            
            # Check for required fields
            if 'title' not in video or not video['title'] or video['title'].strip() == '':
                invalid_videos += 1
                continue
            
            if 'thumbnail' not in video or not video['thumbnail'] or video['thumbnail'].strip() == '':
                invalid_videos += 1
                continue
            
            valid_videos += 1
            valid_videos_array.append(video)
        
        # Statistics
        print(f"\nValidation Results:")
        print(f"Valid videos: {valid_videos}")
        print(f"Invalid videos: {invalid_videos}")
        print(f"Videos with external_url: {videos_with_external_url}")
        print(f"Videos with detail_url: {videos_with_detail_url}")
        print(f"Videos with both URLs: {videos_with_both_urls}")
        print(f"Videos with no URLs: {videos_with_no_urls}")
        print(f"Videos after filtering: {len(valid_videos_array)}")
        
        # Save cleaned data to a new file
        with open('videos_cleaned.json', 'w', encoding='utf-8') as f:
            json.dump(valid_videos_array, f, indent=2, ensure_ascii=False)
        
        print('\nCleaned video data saved to videos_cleaned.json')
        
        # Sample some videos to check quality
        print('\nSample of valid videos:')
        for i, video in enumerate(valid_videos_array[:5]):
            print(f"\n{i + 1}. Title: {video['title']}")
            print(f"   Thumbnail: {video['thumbnail']}")
            print(f"   Detail URL: {video['detail_url'] if 'detail_url' in video and video['detail_url'] else 'None'}")
            print(f"   External URL: {video['external_url'] if 'external_url' in video and video['external_url'] else 'None'}")
            
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    validate_videos()