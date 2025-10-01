#!/usr/bin/env python3
import json

# Load videos from JSON file
with open('videos.json', 'r', encoding='utf-8') as f:
    videos = json.load(f)

print(f"Total videos: {len(videos)}")

# Categorize thumbnails
missing = 0
empty = 0
valid = 0
placeholders = 0
invalid_format = 0
other = 0

sample_valid = []
sample_placeholders = []

for video in videos:
    thumbnail = video.get('thumbnail', '')
    
    if not thumbnail:
        missing += 1
    elif thumbnail.strip() == '':
        empty += 1
    elif thumbnail.startswith('http') and 'placehold.co' not in thumbnail:
        valid += 1
        if len(sample_valid) < 5:
            sample_valid.append(thumbnail)
    elif 'placehold.co' in thumbnail:
        placeholders += 1
        if len(sample_placeholders) < 5:
            sample_placeholders.append(thumbnail)
    elif thumbnail.startswith('http'):
        # Has http but is a placeholder
        placeholders += 1
    else:
        invalid_format += 1

print(f"\nThumbnail Analysis:")
print(f"Missing: {missing}")
print(f"Empty: {empty}")
print(f"Valid: {valid}")
print(f"Placeholders: {placeholders}")
print(f"Invalid format: {invalid_format}")
print(f"Other: {other}")

print(f"\nSample Valid Thumbnails:")
for i, thumb in enumerate(sample_valid, 1):
    print(f"{i}. {thumb}")

print(f"\nSample Placeholder Thumbnails:")
for i, thumb in enumerate(sample_placeholders, 1):
    print(f"{i}. {thumb}")

# Check if there's an issue with the valid thumbnails
print(f"\nTesting first 5 valid thumbnails for issues...")
for i, thumbnail in enumerate(sample_valid[:5]):
    print(f"{i+1}. {thumbnail}")