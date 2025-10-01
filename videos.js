// Load videos from JSON file
let allVideos = [];
let currentCategory = '';
let currentPage = 1;
const videosPerPage = 20;

// Enhanced thumbnail validation function with comprehensive placeholder detection
function isValidThumbnail(thumbnailUrl) {
    // Check if thumbnail exists and is not empty
    if (!thumbnailUrl || typeof thumbnailUrl !== 'string' || thumbnailUrl.trim() === '') {
        return false;
    }
    
    // Trim whitespace
    const trimmedUrl = thumbnailUrl.trim();
    
    // Check if it's a valid URL format
    try {
        new URL(trimmedUrl);
    } catch (e) {
        return false;
    }
    
    // Convert to lowercase for case-insensitive matching
    const thumbnailLower = trimmedUrl.toLowerCase();
    
    // Check for common placeholder URL patterns
    if (thumbnailLower.startsWith('data:image') || 
        thumbnailLower.startsWith('blob:') || 
        thumbnailLower.startsWith('javascript:')) {
        return false;
    }
    
    // Comprehensive placeholder detection
    const placeholderPatterns = [
        'placehold.co',
        'placeholder',
        'no thumbnail',
        'no image',
        'image not found',
        'thumbnail not available',
        'not available',
        'default',
        'missing',
        'error',
        'undefined',
        'null',
        'blank',
        'empty'
    ];
    
    // Check URL and decoded URL parameters for placeholder text
    try {
        // Check the URL itself
        for (const pattern of placeholderPatterns) {
            if (thumbnailLower.includes(pattern)) {
                return false;
            }
        }
        
        // Decode URL parameters and check for placeholder text
        const urlObj = new URL(trimmedUrl);
        const searchParams = urlObj.searchParams;
        
        // Check all URL parameters for placeholder text
        for (const [key, value] of searchParams) {
            const paramValueLower = value.toLowerCase();
            for (const pattern of placeholderPatterns) {
                if (paramValueLower.includes(pattern)) {
                    return false;
                }
            }
        }
        
        // Also check the full search string
        const searchString = urlObj.search.toLowerCase();
        for (const pattern of placeholderPatterns) {
            if (searchString.includes(pattern)) {
                return false;
            }
        }
    } catch (e) {
        // If URL parsing fails, just check the string
        for (const pattern of placeholderPatterns) {
            if (thumbnailLower.includes(pattern)) {
                return false;
            }
        }
    }
    
    return true;
}

// Enhanced video filtering function
function filterVideosWithValidThumbnails(videos) {
    if (!Array.isArray(videos)) {
        console.error('Invalid videos array provided to filter function');
        return [];
    }
    
    return videos.filter(video => {
        // Video must have a title
        if (!video.title || typeof video.title !== 'string' || video.title.trim() === '') {
            return false;
        }
        
        // Video must have a valid thumbnail
        if (!isValidThumbnail(video.thumbnail)) {
            return false;
        }
        
        return true;
    });
}

// Enhanced video card creation function with robust error handling
function createVideoCard(video, index = 0) {
    // Validate input
    if (!video) {
        console.error('Invalid video object provided to createVideoCard');
        return '';
    }
    
    // Default values for missing properties
    const title = (video.title && typeof video.title === 'string') ? video.title.trim() : 'Untitled Video';
    const thumbnail = (video.thumbnail && typeof video.thumbnail === 'string') ? video.thumbnail.trim() : '';
    const detailUrl = (video.detail_url && typeof video.detail_url === 'string') ? video.detail_url.trim() : '#';
    
    // Always prioritize external_url over detail_url
    // Only use detail_url as a fallback when external_url is empty or invalid
    let externalUrl = detailUrl;
    if (video.external_url && 
        typeof video.external_url === 'string' && 
        video.external_url.trim() !== '' && 
        video.external_url !== '#') {
        externalUrl = video.external_url.trim();
    }
    
    // Handle thumbnail with robust error handling
    let thumbnailHTML = '';
    if (isValidThumbnail(thumbnail)) {
        // Valid thumbnail - use it with error handling
        thumbnailHTML = `
            <img src="${thumbnail}" alt="${title}" 
                 loading="lazy"
                 onerror="this.src='https://placehold.co/300x200/1a1a1a/ff6b6b?text=Thumbnail+Error'; this.onerror=null;"
                 onload="this.style.opacity='1'; this.style.visibility='visible';">
        `;
    } else {
        // No valid thumbnail - this shouldn't happen since we filtered videos, but just in case
        thumbnailHTML = `
            <img src="https://placehold.co/300x200/1a1a1a/ff6b6b?text=No+Thumbnail" alt="${title}" 
                 loading="lazy"
                 style="opacity:1; visibility:visible;">
        `;
    }
    
    // Create the complete video card HTML
    return `
        <div class="video-card" data-video-index="${index}">
            <a href="${externalUrl}" target="_blank" rel="noopener noreferrer">
                <div class="video-thumbnail">
                    ${thumbnailHTML}
                </div>
                <div class="video-info">
                    <div class="video-title">${title}</div>
                </div>
            </a>
        </div>
    `;
}

// Fetch videos from JSON file
fetch('videos.json')
    .then(response => response.json())
    .then(data => {
        // Filter out videos without valid thumbnails
        allVideos = filterVideosWithValidThumbnails(data);
        
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
    document.getElementById('video-count').textContent = allVideos.length;
    document.getElementById('total-pages').textContent = Math.ceil(allVideos.length / videosPerPage);
    
    displayVideos();
}

// Display videos for current page
function displayVideos() {
    const startIndex = (currentPage - 1) * videosPerPage;
    const endIndex = startIndex + videosPerPage;
    const videosToDisplay = allVideos.slice(startIndex, endIndex);
    
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
    
    // Generate HTML for video cards, passing index for consistent duration assignment
    const videoHTML = videosToDisplay.map((video, index) => createVideoCard(video, index)).join('');
    videoGrid.innerHTML = videoHTML;
    
    // Update pagination
    document.getElementById('current-page').textContent = currentPage;
}

// Pagination functions
document.getElementById('prev-page').addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        displayVideos();
    }
});

document.getElementById('next-page').addEventListener('click', () => {
    const totalPages = Math.ceil(allVideos.length / videosPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        displayVideos();
    }
});

// Filter functions
document.getElementById('sort-by').addEventListener('change', (e) => {
    // In a real implementation, this would sort the videos
    alert(`Sorting by: ${e.target.value}`);
});

document.getElementById('video-quality').addEventListener('change', (e) => {
    // In a real implementation, this would filter by quality
    alert(`Filtering by quality: ${e.target.value}`);
});

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Set up search functionality
    const searchInput = document.querySelector('.search-bar input');
    const searchButton = document.querySelector('.search-bar button');
    
    if (searchButton && searchInput) {
        searchButton.addEventListener('click', () => {
            const query = searchInput.value.trim();
            if (query) {
                alert(`Searching for: ${query}`);
                // In a real app, you would redirect to search results page
                // window.location.href = `search.html?q=${encodeURIComponent(query)}`;
            }
        });
        
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchButton.click();
            }
        });
    }
});