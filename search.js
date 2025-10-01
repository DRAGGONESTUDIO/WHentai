// Add pagination variables
let currentPage = 1;
const videosPerPage = 36; // 36 videos per page
let allFilteredVideos = [];
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

// Get search query from URL parameters
function getSearchQuery() {
    const urlParams = new URLSearchParams(window.location.search);
    const query = urlParams.get('q') || ''; // Return empty string if no query
    console.log('Search query extracted:', query);
    return query;
}

// Function to create video card HTML without numbering
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
    const uniqueVideos = [];
    
    for (const video of videos) {
        // Create a more comprehensive unique key based on title, thumbnail, and URLs
        const detailUrl = video.detail_url || '';
        const externalUrl = video.external_url || '';
        
        // Normalize the key components to handle variations
        const title = (video.title || '').trim().toLowerCase();
        const thumbnail = (video.thumbnail || '').trim();
        
        // Create a more robust key that handles various edge cases
        // Include more video properties to ensure uniqueness
        const categories = video.categories ? video.categories.join(',') : '';
        const key = `${title}|${thumbnail}|${detailUrl}|${externalUrl}|${categories}`;
        
        // Also create a simpler key for fallback
        const simpleKey = `${title}|${thumbnail}|${detailUrl}|${externalUrl}`;
        
        if (!seen.has(key) && !seen.has(simpleKey)) {
            seen.add(key);
            seen.add(simpleKey);
            uniqueVideos.push(video);
        }
    }
    
    return uniqueVideos;
}

// Function to load search results from videos_cleaned.json with caching
async function loadSearchResults(query) {
    console.log('Loading search results for query:', query);
    
    // Prevent multiple simultaneous requests
    if (isLoading) return;
    
    isLoading = true;
    
    try {
        // Update the search query display
        document.getElementById('search-query').textContent = `"${query}"`;
        
        // Show loading state
        const resultsContainer = document.getElementById('search-results-grid');
        resultsContainer.innerHTML = '<p class="loading-message">Searching videos...</p>';
        
        // Check if we have cached data
        let videos;
        if (videosCache) {
            videos = videosCache;
        } else {
            // Fetch videos with a timeout to prevent hanging
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 20000); // 20 second timeout for large files
            
            try {
                // Use the videos.json file
                const response = await fetch('videos.json', { signal: controller.signal });
                clearTimeout(timeoutId);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                // For very large files, we might need to process in chunks
                const text = await response.text();
                console.log('Videos JSON text length:', text.length);
                videos = JSON.parse(text);
                console.log('Videos loaded, count:', videos ? videos.length : 0);
            } catch (fetchError) {
                clearTimeout(timeoutId);
                console.error('Fetch error:', fetchError);
                // Try to load a smaller sample file if available
                try {
                    const sampleResponse = await fetch('videos_sample.json');
                    if (sampleResponse.ok) {
                        const sampleText = await sampleResponse.text();
                        videos = JSON.parse(sampleText);
                    } else {
                        throw new Error('Sample file not available');
                    }
                } catch (sampleError) {
                    console.error('Sample file error:', sampleError);
                    throw fetchError; // Re-throw the original error
                }
            }
            
            // Cache the data
            // Limit cache size to prevent memory issues with very large datasets
            if (videos && videos.length > 10000) {
                videosCache = videos.slice(0, 10000);
            } else {
                videosCache = videos;
            }
        }
        
        // Remove duplicate videos
        let uniqueVideos = [];
        try {
            const originalCount = videos ? videos.length : 0;
            uniqueVideos = removeDuplicateVideos(videos);
            const uniqueCount = uniqueVideos.length;
            console.log(`Duplicate removal: ${originalCount} -> ${uniqueCount} videos`);
        } catch (duplicateError) {
            console.error('Error removing duplicates:', duplicateError);
            // If duplicate removal fails, use a sample of videos to prevent performance issues
            uniqueVideos = videos && videos.length > 5000 ? videos.slice(0, 5000) : videos;
        }
        
        // Filter videos based on query (case insensitive) - EXACT MATCH in title OR category
        let filteredVideos = [];
        try {
            filteredVideos = uniqueVideos.filter(video => {
                // Check if video has valid URLs
                const hasValidUrl = (video.external_url && video.external_url.trim() !== '') || 
                                   (video.detail_url && video.detail_url.trim() !== '' && video.detail_url !== '#');
                
                if (!hasValidUrl) return false;
                
                // Filter out videos without valid thumbnails
                if (!isValidThumbnail(video.thumbnail)) return false;
                
                // Check if title contains the exact query (case insensitive)
                const titleMatch = video.title && video.title.toLowerCase().includes(query.toLowerCase());
                
                // Also check for partial matches in title words
                const titleWords = video.title.toLowerCase().split(' ');
                const queryWords = query.toLowerCase().split(' ');
                const partialTitleMatch = queryWords.every(word => 
                    titleWords.some(titleWord => titleWord.includes(word))
                );
                
                // Check if any category matches query exactly (case insensitive)
                let categoryMatch = false;
                if (video.categories && Array.isArray(video.categories)) {
                    categoryMatch = video.categories.some(category => 
                        category.toLowerCase() === query.toLowerCase());
                }
                
                // Only return videos that match either title or category exactly
                // Or have partial word matches in the title
                return titleMatch || categoryMatch || partialTitleMatch;
            });
            
            // Limit results to prevent overwhelming the user and improve performance
            if (filteredVideos.length > 1000) {
                console.log(`Limiting results from ${filteredVideos.length} to 1000`);
                filteredVideos = filteredVideos.slice(0, 1000);
            }
        } catch (filterError) {
            console.error('Error filtering videos:', filterError);
            // If filtering fails, return an empty array to prevent further errors
            filteredVideos = [];
        }
        
        // Use filtered videos directly (no sorting)
        const sortedVideos = filteredVideos;
        
        // Update result count
        document.getElementById('result-count').textContent = sortedVideos.length;
        
        // Store filtered videos for pagination
        allFilteredVideos = sortedVideos;
        
        // Reset to first page
        currentPage = 1;
        
        // Display first page of results
        displayVideos();
    } catch (error) {
        console.error('Error loading search results:', error);
        document.getElementById('search-results-grid').innerHTML = `
            <div class="error-message">
                <h3>Error loading search results</h3>
                <p>Please try again later</p>
            </div>
        `;
    } finally {
        isLoading = false;
    }
}

// Function to display videos for current page
function displayVideos() {
    try {
        const startIndex = (currentPage - 1) * videosPerPage;
        const endIndex = startIndex + videosPerPage;
        const videosToDisplay = allFilteredVideos.slice(startIndex, endIndex);
        
        const resultsContainer = document.getElementById('search-results-grid');
        
        if (videosToDisplay.length > 0) {
            // Create video cards for videos, passing index for consistent duration assignment
            const videoCards = [];
            for (const [index, video] of videosToDisplay.entries()) {
                try {
                    videoCards.push(createVideoCard(video, index));
                } catch (cardError) {
                    console.error('Error creating video card:', cardError);
                    // Skip this video and continue with others
                }
            }
            
            // Replace content with video cards
            resultsContainer.innerHTML = videoCards.join('');
        } else {
            if (currentPage === 1) {
                resultsContainer.innerHTML = `
                    <div class="no-results">
                        <h3>No videos found</h3>
                        <p>Try different search terms</p>
                    </div>
                `;
            }
        }
        
        // Update pagination controls
        updatePagination();
    } catch (displayError) {
        console.error('Error displaying videos:', displayError);
        const resultsContainer = document.getElementById('search-results-grid');
        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="error-message">
                    <h3>Error displaying search results</h3>
                    <p>Please try again later</p>
                </div>
            `;
        }
    }
}

// Function to go to a specific page
function goToPage(pageNumber) {
    if (pageNumber >= 1 && pageNumber <= Math.ceil(allFilteredVideos.length / videosPerPage)) {
        currentPage = pageNumber;
        displayVideos();
        updatePagination();
        
        // Scroll to top of video grid
        const videoGrid = document.getElementById('search-results-grid');
        if (videoGrid) {
            videoGrid.scrollIntoView({ behavior: 'smooth' });
        }
    }
}

// Function to update pagination controls with numbered buttons
function updatePagination() {
    const totalPages = Math.ceil(allFilteredVideos.length / videosPerPage);
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
function handleSearch() {
    const searchInput = document.getElementById('search-input');
    const query = searchInput.value.trim();
    
    console.log('Search initiated with query:', query);
    
    if (query) {
        // Update URL with search query
        const url = new URL(window.location);
        url.searchParams.set('q', query);
        window.history.replaceState({}, '', url);
        
        // Load search results
        loadSearchResults(query);
    } else {
        console.log('No search query provided');
    }
}

// Function to initialize the search page
function init() {
    const searchQuery = getSearchQuery();
    
    // Pre-fill search input with query
    const searchInput = document.getElementById('search-input');
    if (searchInput && searchQuery) {
        searchInput.value = searchQuery;
        // Add a small delay to ensure DOM is fully loaded before searching
        setTimeout(() => {
            loadSearchResults(searchQuery);
        }, 100);
    }
    
    const searchButton = document.getElementById('search-button');
    
    if (searchButton && searchInput) {
        searchButton.addEventListener('click', handleSearch);
        
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleSearch();
            }
        });
    }
    
    // Set up filter change handlers
    // Sort by filter removed as per user request
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    // DOM is already loaded
    // Add a small delay to ensure all elements are ready
    setTimeout(init, 100);
}