import json

# Load the videos data
with open('videos.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Count videos with external URLs
total_videos = len(data)
videos_with_external = sum(1 for item in data if item.get('external_url'))

# Calculate percentage
percentage = (videos_with_external / total_videos) * 100 if total_videos > 0 else 0

print(f"Total videos: {total_videos}")
print(f"Videos with external_url: {videos_with_external}")
print(f"Percentage: {percentage:.1f}%")

# Show some examples
print("\nFirst 10 videos with external URLs:")
count = 0
for item in data:
    if item.get('external_url') and count < 10:
        print(f"- {item['title'][:50]}... -> {item['external_url']}")
        count += 1