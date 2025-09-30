// Category data with names and video counts - we'll populate this dynamically
let categoryData = [];
let videosCache = null; // Cache for video data
let isLoading = false; // Flag to prevent multiple simultaneous requests

// Function to load categories from videos data
async function loadCategoriesFromVideos() {
    // Prevent multiple simultaneous requests
    if (isLoading) return;
    
    isLoading = true;
    
    try {
        // Check if we have cached data
        if (videosCache) {
            processCategories(videosCache);
            isLoading = false;
            return;
        }
        
        // Fetch videos with a timeout to prevent hanging
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
        
        // Use the videos.json file
        const response = await fetch('videos.json', { signal: controller.signal });
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const videos = await response.json();
        
        // Limit to first 5000 videos for performance
        const limitedVideos = videos.slice(0, 5000);
        
        // Cache the data
        videosCache = videos;
        
        processCategories(limitedVideos);
        processTags(limitedVideos); // Process tags as well
    } catch (error) {
        console.error('Error loading categories:', error);
        // Fallback to static categories
        displayStaticCategories();
    } finally {
        isLoading = false;
    }
}

// Function to process categories after loading videos
function processCategories(videos) {
    try {
        // Count categories from video data
        const categoryCount = {};
        
        videos.forEach((video, index) => {
            if (video.categories && Array.isArray(video.categories)) {
                video.categories.forEach(category => {
                    // Only count non-empty categories
                    if (category && category.trim() !== '') {
                        categoryCount[category] = (categoryCount[category] || 0) + 1;
                    }
                });
            }
        });
        
        // Convert to array and sort by count (descending)
        categoryData = Object.entries(categoryCount)
            .map(([name, count]) => [name, count.toString()])
            .sort((a, b) => parseInt(b[1]) - parseInt(a[1]));
        
        // Display categories
        displayCategories();
    } catch (error) {
        console.error('Error processing categories:', error);
        // Fallback to static categories
        displayStaticCategories();
    }
}

// Display categories dynamically with enhanced animations
function displayCategories() {
    const categoryGrid = document.getElementById('category-grid');
    if (categoryGrid) {
        categoryGrid.innerHTML = categoryData.map(([name, count], index) => `
            <div class="category-card animated-card" data-category="${name}" style="animation-delay: ${index * 0.1}s">
                <div class="category-icon">
                    <i class="fas fa-tag"></i>
                </div>
                <h3>${name}</h3>
                <span>${count} videos</span>
            </div>
        `).join('');
        
        // Add click event listeners to category cards
        document.querySelectorAll('.category-card').forEach(card => {
            card.addEventListener('click', function() {
                const categoryName = this.getAttribute('data-category');
                // Add animation effect on click
                this.classList.add('card-clicked');
                setTimeout(() => {
                    // Redirect to category videos page
                    window.location.href = `category-videos.html?category=${encodeURIComponent(categoryName)}`;
                }, 300);
            });
        });
    }
}

// Static category data as fallback
const staticCategories = [
    ["Hentai", "8.7K"],
    ["3D", "669K"],
    ["Anime", "845K"],
    ["MILF", "8.6K"],
    ["Teen", "63.4K"],
    ["Big Tits", "449K"],
    ["Anal", "223K"],
    ["Blowjob", "341K"],
    ["Creampie", "10.3K"],
    ["Lesbian", "18.9K"],
    ["BDSM", "130K"],
    ["POV", "35K"],
    ["Gangbang", "14.1K"],
    ["Asian", "210K"],
    ["BBW", "43.2K"],
    ["School", "756"],
    ["Yaoi", "542"],
    ["Yuri", "489"],
    ["Romance", "1.2K"],
    ["Action", "980"],
    ["Supernatural", "632"],
    ["Amateur", "269K"],
    ["Homemade", "93.2K"],
    ["Compilation", "22.6K"],
    ["Uncensored", "154K"]
];

// Function to display static categories as fallback with animations
function displayStaticCategories() {
    const categoryGrid = document.getElementById('category-grid');
    if (categoryGrid) {
        categoryGrid.innerHTML = staticCategories.map(([name, count], index) => `
            <div class="category-card animated-card" data-category="${name}" style="animation-delay: ${index * 0.1}s">
                <div class="category-icon">
                    <i class="fas fa-tag"></i>
                </div>
                <h3>${name}</h3>
                <span>${count} videos</span>
            </div>
        `).join('');
        
        // Add click event listeners to category cards
        document.querySelectorAll('.category-card').forEach(card => {
            card.addEventListener('click', function() {
                const categoryName = this.getAttribute('data-category');
                // Add animation effect on click
                this.classList.add('card-clicked');
                setTimeout(() => {
                    // Redirect to category videos page
                    window.location.href = `category-videos.html?category=${encodeURIComponent(categoryName)}`;
                }, 300);
            });
        });
    }
}

// Function to process tags from video data
function processTags(videos) {
    try {
        // Count tags from video data
        const tagCount = {};
        
        videos.forEach((video, index) => {
            if (video.categories && Array.isArray(video.categories)) {
                video.categories.forEach(category => {
                    // Only count non-empty categories
                    if (category && category.trim() !== '') {
                        tagCount[category] = (tagCount[category] || 0) + 1;
                    }
                });
            }
        });
        
        // Convert to array and sort by count (descending), then take top 20
        const sortedTags = Object.entries(tagCount)
            .map(([name, count]) => ({ name, count }))
            .sort((a, b) => b.count - a.count)
            .slice(0, 20);
        
        // Display tags
        displayTags(sortedTags);
    } catch (error) {
        console.error('Error processing tags:', error);
    }
}

// Function to display tags with animations
function displayTags(tags) {
    const tagsContainer = document.getElementById('tags-container');
    if (tagsContainer) {
        tagsContainer.innerHTML = tags.map((tag, index) => `
            <div class="tag animated-tag" data-tag="${tag.name}" style="animation-delay: ${index * 0.05}s">
                ${tag.name} (${tag.count})
            </div>
        `).join('');
        
        // Add click event listeners to tags
        document.querySelectorAll('.tag').forEach(tag => {
            tag.addEventListener('click', function() {
                const tagName = this.getAttribute('data-tag');
                // Add animation effect on click
                this.classList.add('tag-clicked');
                setTimeout(() => {
                    // Redirect to category videos page
                    window.location.href = `category-videos.html?category=${encodeURIComponent(tagName)}`;
                }, 300);
            });
        });
    }
}

// Function to create video card HTML
function createVideoCard(video) {
    // Default values for missing properties
    const title = video.title || 'Untitled Video';
    let thumbnail = video.thumbnail || 'https://placehold.co/300x200/1a1a1a/ff6b6b?text=No+Thumbnail';
    const detailUrl = video.detail_url || '#';
    
    // Check if thumbnail URL is valid, if not use fallback
    if (!thumbnail || thumbnail.includes('undefined') || thumbnail.includes('null') || 
        !thumbnail.startsWith('http')) {
        thumbnail = 'https://placehold.co/300x200/1a1a1a/ff6b6b?text=No+Thumbnail';
    }
    
    // Always prioritize external_url over detail_url
    // Only use detail_url as a fallback when external_url is empty or invalid
    let externalUrl = video.external_url && video.external_url.trim() !== '' && video.external_url !== '#' 
        ? video.external_url 
        : detailUrl;
    
    // Additional validation for the final URL
    // If the URL is still invalid, use a fallback
    if (!externalUrl || externalUrl === '#' || externalUrl.trim() === '' || 
        !externalUrl.startsWith('http')) {
        externalUrl = 'https://www.cartoonpornvideos.com/';
    }
    
    // For demo purposes, we'll generate consistent durations, views, and dates based on video index
    const durations = ["08:30", "12:15", "15:30", "18:42", "22:15", "24:10", "28:05", "32:40", "35:15", "40:20"];
    const views = ["1.2M", "980K", "2.1M", "3.5M", "1.8M", "1.5M", "2.7M", "1.3M"];
    const dates = ["2 days ago", "1 week ago", "3 days ago", "2 weeks ago", "5 days ago", "4 days ago", "1 day ago", "3 days ago"];
    
    // Assign consistent duration based on video properties for filtering consistency
    const durationIndex = (title.length + (detailUrl ? detailUrl.length : 0)) % durations.length;
    const randomDuration = durations[durationIndex];
    const randomViews = views[Math.floor(Math.random() * views.length)];
    const randomDate = dates[Math.floor(Math.random() * dates.length)];
    
    return `
        <div class="video-card">
            <a href="${externalUrl}" target="_blank" rel="noopener noreferrer">
                <div class="video-thumbnail">
                    <img src="${thumbnail}" alt="${title}" onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\'no-thumbnail\'>No Thumbnail</div>';">
                    <div class="video-duration">${randomDuration}</div>
                </div>
                <div class="video-info">
                    <div class="video-title">${title}</div>
                </div>
            </a>
        </div>
    `;
}

// Function to handle search
function handleSearch(query) {
    if (query) {
        // Redirect to search page with query
        window.location.href = `search.html?q=${encodeURIComponent(query)}`;
    }
}

// Function to initialize the category page
function init() {
    // Display static categories immediately
    displayStaticCategories();
    
    // Add a small delay to ensure DOM is fully loaded
    setTimeout(() => {
        // Load categories dynamically
        loadCategoriesFromVideos();
        
        // Set up search functionality
        const searchInput = document.querySelector('.search-bar input');
        const searchButton = document.querySelector('.search-bar button');
        
        if (searchButton && searchInput) {
            searchButton.addEventListener('click', () => {
                const query = searchInput.value.trim();
                handleSearch(query);
            });
            
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    const query = searchInput.value.trim();
                    handleSearch(query);
                }
            });
        }
    }, 100);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', init);

// Fallback to static categories after 5 seconds if dynamic categories haven't loaded
setTimeout(() => {
    const categoryGrid = document.getElementById('category-grid');
    if (categoryGrid && !categoryGrid.innerHTML) {
        console.log('Falling back to static categories');
        displayStaticCategories();
    }
}, 5000);