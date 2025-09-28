# Generate HTML for ALL categories
# This script reads categories from categories.txt and generates HTML

def generate_category_html(name, video_count):
    """Generate HTML for a single category card"""
    # Simple icon mapping based on common category keywords
    icon_mapping = {
        "3D": "fas fa-cube",
        "4K": "fas fa-video",
        "69": "fas fa-bed",
        "18": "fas fa-birthday-cake",
        "Amateur": "fas fa-user",
        "Anal": "fas fa-backward",
        "Anime": "fas fa-dragon",
        "Arab": "fas fa-globe-africa",
        "Asian": "fas fa-globe-asia",
        "Ass": "fas fa-moon",
        "Babe": "fas fa-heart",
        "BBC": "fas fa-mars",
        "BBW": "fas fa-circle",
        "BDSM": "fas fa-handcuffs",
        "Big Ass": "fas fa-moon",
        "Big Cock": "fas fa-mars",
        "Big Tits": "fas fa-venus",
        "Blonde": "fas fa-user",
        "Blowjob": "fas fa-kiss",
        "Bondage": "fas fa-handcuffs",
        "Boobs": "fas fa-venus",
        "Brazilian": "fas fa-globe-americas",
        "Bukkake": "fas fa-shower",
        "Cartoon": "fas fa-paint-brush",
        "Casting": "fas fa-audition",
        "Cheating": "fas fa-user-secret",
        "Chinese": "fas fa-globe-asia",
        "Chubby": "fas fa-circle",
        "Classic": "fas fa-clock",
        "College": "fas fa-graduation-cap",
        "Comic": "fas fa-book",
        "Compilation": "fas fa-list",
        "Cosplay": "fas fa-mask",
        "Creampie": "fas fa-seedling",
        "Cum": "fas fa-tint",
        "Cumshot": "fas fa-tint",
        "Cunnilingus": "fas fa-kiss",
        "Cute": "fas fa-heart",
        "Czech": "fas fa-globe-europe",
        "Deepthroat": "fas fa-kiss",
        "Desi": "fas fa-globe-asia",
        "Doctor": "fas fa-user-md",
        "Doggystyle": "fas fa-dog",
        "Double Penetration": "fas fa-arrows-alt-h",
        "DP": "fas fa-arrows-alt-h",
        "Ebony": "fas fa-user",
        "Exotic": "fas fa-globe",
        "Facial": "fas fa-smile",
        "Fantasy": "fas fa-hat-wizard",
        "Feet": "fas fa-footprints",
        "Femdom": "fas fa-venus",
        "Fingering": "fas fa-hand-point-up",
        "First Time": "fas fa-star",
        "Fisting": "fas fa-hand-rock",
        "Fitness": "fas fa-dumbbell",
        "Footjob": "fas fa-footprints",
        "French": "fas fa-globe-europe",
        "Funny": "fas fa-laugh",
        "Gangbang": "fas fa-users",
        "Gay": "fas fa-mars-double",
        "German": "fas fa-globe-europe",
        "GILF": "fas fa-venus",
        "Girlfriend": "fas fa-heart",
        "Glasses": "fas fa-glasses",
        "Gloryhole": "fas fa-circle",
        "Goth": "fas fa-moon",
        "Grandpa": "fas fa-mars",
        "Granny": "fas fa-venus",
        "Group Sex": "fas fa-users",
        "Hairy": "fas fa-leaf",
        "Handjob": "fas fa-hand-paper",
        "Hardcore": "fas fa-fire",
        "HD": "fas fa-video",
        "Hentai": "fas fa-dragon",
        "Horny": "fas fa-fire",
        "Hospital": "fas fa-hospital",
        "Hot": "fas fa-fire",
        "Indian": "fas fa-globe-asia",
        "Interracial": "fas fa-globe",
        "Italian": "fas fa-globe-europe",
        "Japanese": "fas fa-globe-asia",
        "JAV": "fas fa-video",
        "Kissing": "fas fa-kiss",
        "Korean": "fas fa-globe-asia",
        "Latex": "fas fa-paint-roller",
        "Latina": "fas fa-globe-americas",
        "Lesbian": "fas fa-venus-double",
        "Lingerie": "fas fa-tshirt",
        "Machine": "fas fa-cogs",
        "Maid": "fas fa-broom",
        "Massage": "fas fa-spa",
        "Masturbating": "fas fa-hand-paper",
        "Mature": "fas fa-venus",
        "Medical": "fas fa-user-md",
        "Mexican": "fas fa-globe-americas",
        "MILF": "fas fa-venus",
        "Mom": "fas fa-venus",
        "Monster": "fas fa-paw",
        "Nurse": "fas fa-user-md",
        "Office": "fas fa-briefcase",
        "Old": "fas fa-venus",
        "Orgasm": "fas fa-bolt",
        "Outdoor": "fas fa-tree",
        "Pakistani": "fas fa-globe-asia",
        "Parody": "fas fa-copy",
        "Party": "fas fa-glass-cheers",
        "POV": "fas fa-eye",
        "Pregnant": "fas fa-baby",
        "Public": "fas fa-users",
        "Pussy": "fas fa-venus",
        "Russian": "fas fa-globe-europe",
        "School": "fas fa-school",
        "Secretary": "fas fa-briefcase",
        "Seduce": "fas fa-heart",
        "Shaved": "fas fa-cut",
        "Shower": "fas fa-shower",
        "Skinny": "fas fa-arrows-alt-h",
        "Slave": "fas fa-chain",
        "Sleep": "fas fa-bed",
        "Small Tits": "fas fa-venus",
        "Solo": "fas fa-user",
        "Spanish": "fas fa-globe-europe",
        "Squirt": "fas fa-tint",
        "Stockings": "fas fa-socks",
        "Story": "fas fa-book",
        "Strap-On": "fas fa-plug",
        "Stripper": "fas fa-gem",
        "Student": "fas fa-graduation-cap",
        "Swallow": "fas fa-kiss",
        "Swinger": "fas fa-users",
        "Teacher": "fas fa-chalkboard-teacher",
        "Teen": "fas fa-child",
        "Threesome": "fas fa-users",
        "Toys": "fas fa-plug",
        "Uniform": "fas fa-tshirt",
        "Vintage": "fas fa-clock",
        "Virgin": "fas fa-star",
        "Webcam": "fas fa-camera",
        "Wife": "fas fa-heart",
        "Yoga": "fas fa-spa",
        "Young": "fas fa-child"
    }
    
    # Find the best matching icon
    icon_class = "fas fa-tag"  # default icon
    name_lower = name.lower()
    for key, icon in icon_mapping.items():
        if key.lower() in name_lower:
            icon_class = icon
            break
    
    # Generate the HTML
    html = f'''                <div class="category-card">
                    <div class="category-icon">
                        <i class="{icon_class}"></i>
                    </div>
                    <h3>{name}</h3>
                    <span>{video_count} videos</span>
                </div>'''
    return html

def read_categories_from_file():
    """Read categories from the text file"""
    categories = []
    try:
        with open("categories.txt", "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            # Process pairs of lines (name and count)
            for i in range(0, len(lines), 2):
                if i + 1 < len(lines):
                    name = lines[i]
                    count = lines[i + 1]
                    # Skip single letters used as headers
                    if len(name) > 1 and name.isalpha() and len(name) < 50:
                        categories.append((name, count))
                    # Also handle cases where the name might be on the count line
                    elif len(name) <= 1 and i + 2 < len(lines):
                        # This is likely a header, so skip it and the next line
                        continue
    except FileNotFoundError:
        print("categories.txt file not found")
        return []
    return categories

def main():
    # Read categories from file
    categories = read_categories_from_file()
    
    # Generate HTML for all categories
    html_output = ""
    for name, video_count in categories:
        # Only process if name is not a single letter
        if len(name) > 1 and not (len(name) == 1 and name.isalpha()):
            html_output += generate_category_html(name, video_count) + "\n"
    
    # Write to output file
    with open("generated_categories.html", "w", encoding="utf-8") as f:
        f.write(html_output)
    
    print(f"Generated HTML for {len(categories)} categories")

if __name__ == "__main__":
    main()