import json
import re

def extract_categories_from_title(title):
    """Extract potential categories from video title"""
    # Common category keywords
    categories = [
        # Content types
        '3D', 'Animation', 'Anime', 'Cartoon', 'Manga', 'Toon', 'Hentai', 'Porn',
        
        # Body types and characteristics
        'Big Tits', 'Small Tits', 'Large Boobs', 'Huge Boobs', 'Big Boobs',
        'Big Ass', 'Small Ass', 'BBW', 'Petite', 'Curvy', 'Skinny',
        'Blonde', 'Brunette', 'Redhead', 'Black Hair', 'Brown Hair',
        'Asian', 'Japanese', 'Ebony', 'Black', 'Latina', 'White',
        'MILF', 'Mom', 'Mother', 'Teen', '18', 'Young', 'Older', 'Mature',
        'Granny', 'Grandma', 'Girl', 'Woman', 'Man', 'Boy', 'Guy',
        
        # Sexual acts and positions
        'Blowjob', 'BJ', 'Deepthroat', 'Facial', 'Cumshot', 'Creampie',
        'Anal', 'DP', 'Double Penetration', 'Gangbang', 'Orgy', 'Threesome',
        'Foursome', '69', 'Missionary', 'Doggy Style', 'Cowgirl',
        'Reverse Cowgirl', 'Standing', 'Sitting', 'Kneeling',
        
        # Kinks and fetishes
        'BDSM', 'Bondage', 'Rope', 'Cuffs', 'Blindfold', 'Gag',
        'Femdom', 'Domination', 'Submission', 'S&M', 'Masochism',
        'Fisting', 'Squirt', 'Squirting', 'Cum', 'Orgasm',
        'Cuckold', 'Cuckquean', 'Swinger', 'Swinging',
        'Fetish', 'Foot Fetish', 'Feet', 'Handjob', 'Titjob',
        'Cunnilingus', 'Rimming', 'Ass Licking', 'Pussy Licking',
        
        # Scenarios and themes
        'School', 'Teacher', 'Student', 'Nurse', 'Doctor', 'Office',
        'Boss', 'Secretary', 'Step Mom', 'Step Sister', 'Step Brother',
        'Family', 'Incest', 'Taboo', 'Forbidden', 'Affair', 'Cheating',
        'Public', 'Outdoor', 'Beach', 'Pool', 'Hotel', 'Car',
        'Bathroom', 'Shower', 'Toilet', 'Bedroom', 'Home',
        'Parody', 'Spoof', 'Comedy', 'Funny', 'Humor',
        'Romance', 'Romantic', 'Love', 'Relationship',
        'Action', 'Adventure', 'Fantasy', 'Supernatural', 'Magic',
        'Sci-Fi', 'Science Fiction', 'Future', 'Space', 'Alien',
        'Historical', 'Medieval', 'Knight', 'Princess', 'Royal',
        'Military', 'Army', 'Soldier', 'Police', 'Cop',
        'Prison', 'Captive', 'Kidnapped', 'Hostage',
        
        # Nationalities and ethnicities
        'American', 'British', 'UK', 'English', 'French', 'German',
        'Italian', 'Spanish', 'Mexican', 'Brazilian', 'Argentinian',
        'Colombian', 'Venezuelan', 'Peruvian', 'Chilean', 'Argentine',
        'Russian', 'Chinese', 'Korean', 'Indian', 'Arab', 'Middle Eastern',
        'African', 'Australian', 'Canadian',
        
        # Special categories
        'Amateur', 'Homemade', 'Professional', 'Pornstar',
        'Compilation', 'Collection', 'Best Of', 'Greatest Hits',
        'Uncensored', 'Raw', 'Unfiltered', 'Hardcore',
        'Softcore', 'Erotic', 'Sensual', 'Romantic',
        'VR', 'Virtual Reality', 'Interactive',
        'Solo', 'Masturbation', 'Self Pleasure',
        'Lesbian', 'Gay', 'Bisexual', 'Transgender', ' Shemale',
        'Yaoi', 'Yuri', 'Boy Love', 'Girl Love',
        
        # Toys and accessories
        'Dildo', 'Vibrator', 'Buttplug', 'Anal Beads',
        'Sex Toys', 'Pleasure Toys', 'Adult Toys',
        
        # Special scenarios
        'First Time', 'Virgin', 'Defloration',
        'Seduction', 'Temptation', 'Teasing',
        'Surprise', 'Caught', 'Peeping', 'Voyeur',
        'Role Play', 'Costume', 'Disguise', 'Uniform',
        'Fantasy', 'Dream', 'Nightmare'
    ]
    
    found_categories = []
    title_lower = title.lower()
    
    # Check for each category keyword
    for category in categories:
        if category.lower() in title_lower:
            found_categories.append(category)
    
    return found_categories

def add_category_tags_to_videos():
    """Add category tags to all videos in videos.json"""
    try:
        # Read the videos file
        with open('videos.json', 'r', encoding='utf-8') as f:
            videos = json.load(f)
        
        print(f"Processing {len(videos)} videos...")
        
        # Process each video
        for i, video in enumerate(videos):
            # Extract categories from title
            categories = extract_categories_from_title(video.get('title', ''))
            
            # Add categories to video data
            video['categories'] = categories
            
            # Show progress
            if (i + 1) % 5000 == 0:
                print(f"Processed {i + 1} videos...")
        
        # Save updated videos back to file
        with open('videos.json', 'w', encoding='utf-8') as f:
            json.dump(videos, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully updated {len(videos)} videos with category tags!")
        
        # Show some statistics
        category_count = {}
        for video in videos:
            for category in video.get('categories', []):
                category_count[category] = category_count.get(category, 0) + 1
        
        # Show top 20 categories
        sorted_categories = sorted(category_count.items(), key=lambda x: x[1], reverse=True)
        print("\nTop 20 categories:")
        for category, count in sorted_categories[:20]:
            print(f"  {category}: {count} videos")
            
    except Exception as e:
        print(f"Error processing videos: {e}")

if __name__ == "__main__":
    add_category_tags_to_videos()