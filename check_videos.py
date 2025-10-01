#!/usr/bin/env python3
import json

# Load videos from JSON file
with open('videos.json', 'r', encoding='utf-8') as f:
    videos = json.load(f)

print(f"Total videos: {len(videos)}")

# Check first 5 videos
print("\nFirst 5 videos:")
for i, video in enumerate(videos[:5]):
    title = video.get('title', 'No title')
    thumbnail = video.get('thumbnail', 'No thumbnail')
    print(f"{i+1}. {title[:50]}...")
    print(f"   Thumbnail: {thumbnail[:100]}")
    print()