// Load videos from JSON file
let allVideos = [];
let filteredVideos = [];
let currentCategory = '';
let currentPage = 1;
const videosPerPage = 30;

// Function to remove duplicate videos based on title and thumbnail
function removeDuplicateVideos(videos) {
    const seen = new Set();
    return videos.filter(video => {
        // Create a more comprehensive unique key based on title, thumbnail, and URLs
        const key = `${video.title}|${video.thumbnail}|${video.detail_url}|${video.external_url}`;
        if (seen.has(key)) {
            return false; // Duplicate found
        }
        seen.add(key);
        return true; // Unique video
    });
}

// Fetch videos from JSON file
fetch('videos.json')
    .then(response => response.json())
    .then(data => {
        // Remove duplicate videos
        const uniqueVideos = removeDuplicateVideos(data);
        
        allVideos = uniqueVideos;
        // Remove the first few non-video entries if they exist
        if (allVideos.length > 0 && !allVideos[0].title.includes("Hentai") && !allVideos[0].title.includes("Cartoon")) {
            allVideos.shift();
        }
        loadCategoryVideos();
    })
    .catch(error => {
        console.error('Error loading videos:', error);
        document.getElementById('video-grid').innerHTML = `
            <div class="error-message">
                <h3>Error Loading Videos</h3>
                <p>Unable to load video data. Please try again later.</p>
            </div>
        `;
    });

// Get category from URL parameter
function getCategoryFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('category') || 'All Videos';
}

// Load videos for the current category
function loadCategoryVideos() {
    currentCategory = getCategoryFromURL();
    document.getElementById('category-title').textContent = currentCategory;
    document.getElementById('category-name').textContent = currentCategory;
    
    // Filter videos by category
    if (currentCategory === 'All Videos') {
        filteredVideos = allVideos;
    } else {
        // Filter videos based on actual category tags with improved matching
        filteredVideos = allVideos.filter(video => {
            // Check if video has categories array
            if (video.categories && Array.isArray(video.categories)) {
                // Check if any of the video's categories match the current category (case-insensitive)
                return video.categories.some(category => 
                    category.toLowerCase() === currentCategory.toLowerCase()
                );
            }
            // Fallback to keyword matching in title if no categories
            const title = video.title.toLowerCase();
            return title.includes(currentCategory.toLowerCase());
        });
    }
    
    document.getElementById('category-description').textContent = `Browse ${filteredVideos.length} videos in the ${currentCategory} category.`;
    
    // Reset to first page when loading new category
    currentPage = 1;
    displayVideos();
}

// Display videos for current page
function displayVideos() {
    const startIndex = (currentPage - 1) * videosPerPage;
    const endIndex = startIndex + videosPerPage;
    const videosToDisplay = filteredVideos.slice(startIndex, endIndex);
    
    const videoGrid = document.getElementById('video-grid');
    
    if (videosToDisplay.length === 0) {
        videoGrid.innerHTML = `
            <div class="no-results">
                <h3>No Videos Found</h3>
                <p>There are no videos available in this category.</p>
            </div>
        `;
        return;
    }
    
    // Generate HTML for video cards
    const videoHTML = videosToDisplay.map(video => createVideoCard(video)).join('');
    
    // If this is the first page, replace content, otherwise append
    if (currentPage === 1) {
        videoGrid.innerHTML = videoHTML;
    } else {
        videoGrid.innerHTML += videoHTML;
    }
}

// Function to load more videos
function loadMoreVideos() {
    currentPage++;
    displayVideos();
}

// Function to handle search
function handleSearch(query) {
    if (query) {
        // Redirect to search page with query
        window.location.href = `search.html?q=${encodeURIComponent(query)}`;
    }
}

// Function to create video card HTML with proper metadata display
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

// Set up search functionality
function initSearch() {
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
    
    // Set up load more button
    const loadMoreButton = document.getElementById('load-more');
    if (loadMoreButton) {
        loadMoreButton.addEventListener('click', () => {
            loadMoreVideos();
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initSearch();
});