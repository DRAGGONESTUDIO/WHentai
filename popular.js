// Add pagination variables at the top of the file
let currentPage = 1;
const videosPerPage = 36;
let allVideos = [];
let currentSortBy = 'views'; // Default sorting for popular page
let currentDurationFilter = 'any'; // Default duration filter
let videosCache = null; // Cache for video data
let isLoading = false; // Flag to prevent multiple simultaneous requests

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

// Function to create video card HTML without numbering
function createVideoCard(video) {
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
                    <img src="${thumbnail}" alt="${title}" loading="lazy" onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\'no-thumbnail\'>No Thumbnail</div>';" onload="this.style.opacity='1';" style="opacity:0; transition: opacity 0.3s;">
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
    const uniqueVideos = [];
    
    for (const video of videos) {
        // Create a more comprehensive unique key based on title, thumbnail, and URLs
        const detailUrl = video.detail_url || '';
        const externalUrl = video.external_url || '';
        const key = `${video.title}|${video.thumbnail}|${detailUrl}|${externalUrl}`;
        
        if (!seen.has(key)) {
            seen.add(key);
            uniqueVideos.push(video);
        }
    }
    
    return uniqueVideos;
}

// Function to sort videos based on selected criteria
function sortVideos(videos, sortBy) {
    // Create a copy of the array to avoid modifying the original
    const sortedVideos = [...videos];
    
    switch (sortBy) {
        case 'views':
            return sortedVideos.sort((a, b) => {
                // Simple view comparison (in a real app, you'd have actual view counts)
                return Math.random() - 0.5;
            });
        case 'date':
            return sortedVideos.sort((a, b) => {
                // For date sorting
                return Math.random() - 0.5;
            });
        case 'duration':
            return sortedVideos.sort((a, b) => {
                // Simple duration comparison (in a real app, you'd have actual durations)
                return Math.random() - 0.5;
            });
        default:
            return sortedVideos.sort(() => Math.random() - 0.5);
    }
}

// Function to filter videos by duration
function filterVideosByDuration(videos, durationFilter) {
    if (durationFilter === 'any') {
        return videos;
    }
    
    // Simulate filtering by returning a subset based on the filter
    const filteredVideos = [...videos];
    switch (durationFilter) {
        case 'short':
            return filteredVideos.sort(() => Math.random() - 0.5);
        case 'medium':
            return filteredVideos.sort(() => Math.random() - 0.5);
        case 'long':
            return filteredVideos.sort(() => Math.random() - 0.5);
        default:
            return videos;
    }
}

// Function to load popular videos from videos_cleaned.json with caching
async function loadPopularVideos() {
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
        console.error('Error loading popular videos:', error);
        // Show error message to user
        const popularContainer = document.getElementById('popular-videos');
        if (popularContainer) {
            popularContainer.innerHTML = '<p class="error-message">Failed to load videos. Please try again later.</p>';
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
        
        // Apply duration filter first
        const durationFilteredVideos = filterVideosByDuration(uniqueVideos, currentDurationFilter);
        
        // Sort videos based on current sort setting
        const sortedVideos = sortVideos(durationFilteredVideos, currentSortBy);
        
        // Store videos to maintain consistency across pagination (without reshuffling)
        allVideos = sortedVideos.slice(0, 3000); // Load more videos for pagination
        
        // Display first page of videos
        displayVideos();
    } catch (error) {
        console.error('Error processing popular videos:', error);
        // Show error message to user
        const popularContainer = document.getElementById('popular-videos');
        if (popularContainer) {
            popularContainer.innerHTML = '<p class="error-message">Error processing videos. Please try again later.</p>';
        }
    }
}

// Function to display videos for current page
function displayVideos() {
    const startIndex = (currentPage - 1) * videosPerPage;
    const endIndex = startIndex + videosPerPage;
    const videosToDisplay = allVideos.slice(startIndex, endIndex);
    
    const popularContainer = document.getElementById('popular-videos');
    if (popularContainer) {
        // Create video cards for videos
        const videoCards = [];
        for (const video of videosToDisplay) {
            videoCards.push(createVideoCard(video));
        }
        
        // Replace content with video cards
        popularContainer.innerHTML = videoCards.join('');
        
        // If no videos to display, show a message
        if (videoCards.length === 0 && currentPage === 1) {
            popularContainer.innerHTML = '<p class="no-videos-message">No videos found.</p>';
        }
    }
    
    // Update pagination controls
    updatePagination();
}

// Function to go to a specific page
function goToPage(pageNumber) {
    if (pageNumber >= 1 && pageNumber <= Math.ceil(allVideos.length / videosPerPage)) {
        currentPage = pageNumber;
        displayVideos();
        updatePagination();
        
        // Scroll to top of video grid
        const videoGrid = document.getElementById('popular-videos');
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

// Function to handle sort filter changes - FIXED to use cached data
function handleSortChange() {
    const sortFilter = document.getElementById('sort-filter');
    if (sortFilter) {
        currentSortBy = sortFilter.value;
        // Reset to first page when sorting
        currentPage = 1;
        // Re-process cached videos with new sort order instead of reloading
        if (videosCache) {
            processVideos(videosCache);
        }
    }
}

// Function to handle duration filter changes - FIXED to use cached data
function handleDurationChange() {
    const durationFilter = document.getElementById('duration-filter');
    if (durationFilter) {
        currentDurationFilter = durationFilter.value;
        // Reset to first page when filtering
        currentPage = 1;
        // Re-process cached videos with new duration filter instead of reloading
        if (videosCache) {
            processVideos(videosCache);
        }
    }
}

// Function to initialize the page
function init() {
    // Load popular videos
    loadPopularVideos();
    
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
    
    // Set up sort filter
    const sortFilter = document.getElementById('sort-filter');
    if (sortFilter) {
        sortFilter.addEventListener('change', handleSortChange);
    }
    
    // Set up duration filter
    const durationFilter = document.getElementById('duration-filter');
    if (durationFilter) {
        durationFilter.addEventListener('change', handleDurationChange);
    }
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    // DOM is already loaded
    init();
}