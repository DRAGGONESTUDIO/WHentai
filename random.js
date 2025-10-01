// Add pagination variables at the top of the file
let currentPage = 1;
const videosPerPage = 36;
let allVideos = [];
let videosCache = null; // Cache for video data
let isLoading = false; // Flag to prevent multiple simultaneous requests
// No video numbering needed

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

// Function to create video card HTML with numbering
function createVideoCard(video, index = 0) {
    // Default values for missing properties
    const title = video.title || 'Untitled Video';
    let thumbnail = video.thumbnail || 'https://placehold.co/300x200/1a1a1a/ff6b6b?text=No+Thumbnail';
    const detailUrl = video.detail_url || '#';
    
    // Check if thumbnail is valid
    if (!isValidThumbnail(thumbnail)) {
        thumbnail = 'https://placehold.co/300x200/1a1a1a/ff6b6b?text=No+Thumbnail';
    }
    
    // Additional check for broken image URLs
    const brokenImagePatterns = ['data:image', 'blob:', 'javascript:'];
    if (brokenImagePatterns.some(pattern => thumbnail.startsWith(pattern))) {
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
    const durationSeed = title.length + (video.detail_url ? video.detail_url.length : 0) + index;
    const durationIndex = durationSeed % durations.length;
    const randomDuration = durations[durationIndex];
    const randomViews = views[Math.floor(Math.random() * views.length)];
    const randomDate = dates[Math.floor(Math.random() * dates.length)];
    
    return `
        <div class="video-card">
            <a href="${externalUrl}" target="_blank" rel="noopener noreferrer">
                <div class="video-thumbnail">
                    <img src="${thumbnail}" alt="${title}" onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\'no-thumbnail\'>No Thumbnail</div>';" onload="this.style.opacity='1';" style="opacity:0; transition: opacity 0.3s;">
                    <div class="video-duration">${randomDuration}</div>
                </div>
                <div class="video-info">
                    <div class="video-title">${title}</div>
                </div>
            </a>
        </div>
    `;
}

// Function to remove duplicate videos based on title, thumbnail, and URL
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

// Function to get random videos from videos_cleaned.json with caching
async function loadRandomVideos() {
    // Prevent multiple simultaneous requests
    if (isLoading) return;
    
    isLoading = true;
    
    try {
        // Check if we have cached data
        if (videosCache) {
            processVideos(videosCache);
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
        
        // Cache the data
        videosCache = videos;
        
        processVideos(videos);
    } catch (error) {
        console.error('Error loading random videos:', error);
        // Show error message to user
        const randomContainer = document.getElementById('random-videos');
        if (randomContainer) {
            randomContainer.innerHTML = '<p class="error-message">Failed to load videos. Please try again later.</p>';
        }
    } finally {
        isLoading = false;
    }
}

// Function to process videos after loading
function processVideos(videos) {
    try {
        // Filter out videos without any URLs
        const validVideos = videos.filter(video => 
            (video.external_url && video.external_url.trim() !== '') || 
            (video.detail_url && video.detail_url.trim() !== '' && video.detail_url !== '#')
        );
        
        // Filter out videos without valid thumbnails
        const videosWithValidThumbnails = filterVideosWithValidThumbnails(validVideos);
        
        // Remove duplicate videos
        const uniqueVideos = removeDuplicateVideos(videosWithValidThumbnails);
        
        // Shuffle the videos array using Fisher-Yates algorithm
        const shuffledVideos = [...uniqueVideos];
        for (let i = shuffledVideos.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffledVideos[i], shuffledVideos[j]] = [shuffledVideos[j], shuffledVideos[i]];
        }
        
        // Take a larger sample and reshuffle for better distribution
        allVideos = shuffledVideos.slice(0, 3000); // Load more videos for pagination
        
        // No video numbering needed
        
        // Display first page of videos
        displayVideos();
    } catch (error) {
        console.error('Error processing random videos:', error);
        // Show error message to user
        const randomContainer = document.getElementById('random-videos');
        if (randomContainer) {
            randomContainer.innerHTML = '<p class="error-message">Error processing videos. Please try again later.</p>';
        }
    }
}

// Function to display videos for current page
function displayVideos() {
    const startIndex = (currentPage - 1) * videosPerPage;
    const endIndex = startIndex + videosPerPage;
    const videosToDisplay = allVideos.slice(startIndex, endIndex);
    
    const randomContainer = document.getElementById('random-videos');
    if (randomContainer) {
        // Replace content with video cards, passing index for consistent duration assignment
        randomContainer.innerHTML = videosToDisplay.map((video, index) => createVideoCard(video, index)).join('');
        
        // If no videos to display, show a message
        if (videosToDisplay.length === 0 && currentPage === 1) {
            randomContainer.innerHTML = '<p class="no-videos-message">No videos found.</p>';
        }
    }
    
    // Update pagination controls
    updatePagination();
}

// Function to go to a specific page
function goToPage(pageNumber) {
    if (pageNumber >= 1 && pageNumber <= Math.ceil(allVideos.length / videosPerPage)) {
        currentPage = pageNumber;
        // No video numbering needed
        displayVideos();
        updatePagination();
        
        // Scroll to top of video grid
        const videoGrid = document.getElementById('random-videos');
        if (videoGrid) {
            videoGrid.scrollIntoView({ behavior: 'smooth' });
        }
    }
}

// Function to update pagination controls with numbered buttons
function updatePagination() {
    const totalPages = Math.ceil(allVideos.length / videosPerPage);
    const paginationContainer = document.getElementById('pagination-controls');
    
    if (paginationContainer && totalPages > 1) {
        let paginationHTML = '';
        
        // Previous button
        if (currentPage > 1) {
            paginationHTML += `<button class="btn btn-secondary" onclick="goToPage(${currentPage - 1})">Previous</button>`;
        }
        
        // Numbered page buttons
        const maxVisiblePages = 10;
        let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
        
        // Adjust start page if we're near the end
        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        // First page button (if not already shown)
        if (startPage > 1) {
            paginationHTML += `<button class="btn btn-secondary" onclick="goToPage(1)">1</button>`;
            if (startPage > 2) {
                paginationHTML += `<span class="pagination-ellipsis">...</span>`;
            }
        }
        
        // Page number buttons
        for (let i = startPage; i <= endPage; i++) {
            if (i === currentPage) {
                paginationHTML += `<button class="btn btn-primary active" disabled>${i}</button>`;
            } else {
                paginationHTML += `<button class="btn btn-secondary" onclick="goToPage(${i})">${i}</button>`;
            }
        }
        
        // Last page button (if not already shown)
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHTML += `<span class="pagination-ellipsis">...</span>`;
            }
            paginationHTML += `<button class="btn btn-secondary" onclick="goToPage(${totalPages})">${totalPages}</button>`;
        }
        
        // Next button
        if (currentPage < totalPages) {
            paginationHTML += `<button class="btn btn-secondary" onclick="goToPage(${currentPage + 1})">Next</button>`;
        }
        
        paginationContainer.innerHTML = paginationHTML;
    } else if (paginationContainer) {
        // Hide pagination if there's only one page
        paginationContainer.innerHTML = '';
    }
}

// Function to handle search
function handleSearch(query) {
    if (query) {
        // Redirect to search page with query
        window.location.href = `search.html?q=${encodeURIComponent(query)}`;
    }
}

// Function to initialize the page
function init() {
    // Load random videos
    loadRandomVideos();
    
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
    
    // Set up refresh button
    const refreshButton = document.getElementById('refresh-videos');
    if (refreshButton) {
        refreshButton.addEventListener('click', () => {
            // Reset to first page and reload (this will reshuffle the videos)
            currentPage = 1;
            loadRandomVideos();
        });
    }
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    // DOM is already loaded
    init();
}