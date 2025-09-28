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
        
        // Use the smaller videos_cleaned.json file instead of the large videos.json
        const response = await fetch('videos_cleaned.json', { signal: controller.signal });
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const videos = await response.json();
        
        // Cache the data
        videosCache = videos;
        
        processCategories(videos);
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
        
        videos.forEach(video => {
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

// Display categories dynamically
function displayCategories() {
    const categoryGrid = document.getElementById('category-grid');
    if (categoryGrid) {
        categoryGrid.innerHTML = categoryData.map(([name, count]) => `
            <div class="category-card" data-category="${name}">
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
                // Redirect to category videos page
                window.location.href = `category-videos.html?category=${encodeURIComponent(categoryName)}`;
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

// Function to display static categories as fallback
function displayStaticCategories() {
    const categoryGrid = document.getElementById('category-grid');
    if (categoryGrid) {
        categoryGrid.innerHTML = staticCategories.map(([name, count]) => `
            <div class="category-card" data-category="${name}">
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
                // Redirect to category videos page
                window.location.href = `category-videos.html?category=${encodeURIComponent(categoryName)}`;
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
    
    // Improved link handling - prioritize direct video links over redirect links
    let externalUrl = detailUrl; // Default to detail_url
    
    // Check if we have a valid external URL
    if (video.external_url && video.external_url.trim() !== '') {
        // List of known redirect URLs that don't lead to actual videos
        const invalidRedirects = [
            'sortporn.com',
            'bit.ly',
            'lustyheroes.com',
            'youfetishbitch.com',
            'bemyhole.com',
            'tsyndicate.com',
            'theporndude.com',
            'rpwmct.com',
            '60fpsanimation.com',
            'hentaismile.com',
            'lesbian8.com',
            'freeporn8.com',
            'welcomix.com',
            'fapality.com',
            'mylust.com',
            'eporner.com',
            'xxxfree.watch',
            'zlink7.com',
            'adtng.com',
            'ylmcash.com',
            'aberatii.com',
            'kimsaliese.com',
            'whitehardcorp.com',
            'brazzersnetwork.com'
        ];
        
        // Check if the external URL is a valid direct link
        const isInvalidRedirect = invalidRedirects.some(domain => video.external_url.includes(domain));
        
        // Use external URL if it's not a known redirect, or if detail_url is not available
        if (!isInvalidRedirect || detailUrl === '#' || detailUrl === '') {
            externalUrl = video.external_url;
        }
        // Otherwise, fall back to detail_url if it's available
        else if (detailUrl && detailUrl !== '#' && detailUrl.trim() !== '') {
            externalUrl = detailUrl;
        }
    }
    // If no external URL, ensure we have a valid detail URL
    else if (detailUrl && detailUrl !== '#' && detailUrl.trim() !== '') {
        externalUrl = detailUrl;
    }
    
    // Additional validation for the final URL
    // If the URL is still invalid, use a fallback
    if (!externalUrl || externalUrl === '#' || externalUrl.trim() === '' || 
        !externalUrl.startsWith('http')) {
        externalUrl = 'https://www.cartoonpornvideos.com/';
    }
    
    // For demo purposes, we'll generate random durations, views, and dates
    const durations = ["15:30", "18:42", "22:15", "24:10", "28:05", "32:40", "35:15", "40:20"];
    const views = ["1.2M", "980K", "2.1M", "3.5M", "1.8M", "1.5M", "2.7M", "1.3M"];
    const dates = ["2 days ago", "1 week ago", "3 days ago", "2 weeks ago", "5 days ago", "4 days ago", "1 day ago", "3 days ago"];
    
    const randomDuration = durations[Math.floor(Math.random() * durations.length)];
    const randomViews = views[Math.floor(Math.random() * views.length)];
    const randomDate = dates[Math.floor(Math.random() * dates.length)];
    
    return `
        <div class="video-card">
            <a href="${externalUrl}" target="_blank" rel="noopener noreferrer">
                <div class="video-thumbnail">
                    <img src="${thumbnail}" alt="${title}" onerror="this.src='https://placehold.co/300x200/1a1a1a/ff6b6b?text=No+Thumbnail';">
                    <div class="video-duration">${randomDuration}</div>
                </div>
                <div class="video-info">
                    <div class="video-title">${title}</div>
                    <div class="video-meta">
                        <div class="video-views">
                            <i class="fas fa-eye"></i>
                            ${randomViews}
                        </div>
                        <div class="video-date">
                            <i class="far fa-clock"></i>
                            ${randomDate}
                        </div>
                    </div>
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
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', init);