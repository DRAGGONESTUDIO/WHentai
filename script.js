// Add pagination variables
let currentPage = 1;
const videosPerPage = 36; // 18 trending + 18 latest per page
let allVideos = [];
let videosCache = null; // Cache for video data
let isLoading = false; // Flag to prevent multiple simultaneous requests
let currentTrendingSortBy = 'random'; // Default sorting for trending videos
let currentTrendingDurationFilter = 'any'; // Default duration filter for trending videos
let currentLatestSortBy = 'random'; // Default sorting for latest videos
let currentLatestDurationFilter = 'any'; // Default duration filter for latest videos

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

// Function to create video card HTML
function createVideoCard(video) {
    // Default values for missing properties
    const title = video.title || 'Untitled Video';
    let thumbnail = video.thumbnail || 'https://placehold.co/300x200/1a1a1a/ff6b6b?text=No+Thumbnail';
    const detailUrl = video.detail_url || '#';
    
    // Check if thumbnail is valid
    if (!isValidThumbnail(thumbnail)) {
        thumbnail = 'https://placehold.co/300x200/1a1a1a/ff6b6b?text=No+Thumbnail';
    }
    
    // Improved link handling - prioritize direct video links over redirect links
    let externalUrl = detailUrl; // Default to detail_url
    
    // Check if we have a valid external URL
    if (video.external_url && video.external_url.trim() !== '') {
        // List of known redirect URLs that don't lead to actual videos
        const invalidRedirects = [
            'sortporn.com', 'bit.ly', 'lustyheroes.com', 'youfetishbitch.com',
            'bemyhole.com', 'tsyndicate.com', 'theporndude.com', 'rpwmct.com',
            '60fpsanimation.com', 'hentaismile.com', 'lesbian8.com', 'freeporn8.com',
            'welcomix.com', 'fapality.com', 'mylust.com', 'eporner.com',
            'xxxfree.watch', 'zlink7.com', 'adtng.com', 'ylmcash.com',
            'aberatii.com', 'kimsaliese.com', 'whitehardcorp.com', 'brazzersnetwork.com'
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
    
    // Use actual metadata if available, otherwise generate random values for demo
    const duration = video.duration || ["15:30", "18:42", "22:15", "24:10", "28:05", "32:40", "35:15", "40:20"][Math.floor(Math.random() * 8)];
    const views = video.views || ["1.2M", "980K", "2.1M", "3.5M", "1.8M", "1.5M", "2.7M", "1.3M"][Math.floor(Math.random() * 8)];
    const uploadDate = video.upload_date || ["2 days ago", "1 week ago", "3 days ago", "2 weeks ago", "5 days ago", "4 days ago", "1 day ago", "3 days ago"][Math.floor(Math.random() * 8)];
    
    return `
        <div class="video-card">
            <a href="${externalUrl}" target="_blank" rel="noopener noreferrer">
                <div class="video-thumbnail">
                    <img src="${thumbnail}" alt="${title}" loading="lazy" onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\'no-thumbnail\'>No Thumbnail</div>';" onload="this.style.opacity='1';" style="opacity:0; transition: opacity 0.3s;">
                    <div class="video-duration">${duration}</div>
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

// Function to load videos from videos_cleaned.json with caching
async function loadVideosFromJSON() {
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
        
        // Show loading indicator
        showLoadingIndicator();
        
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
        console.error('Error loading videos:', error);
        hideLoadingIndicator();
        // Fallback to sample data
        populateVideoGrids();
    } finally {
        isLoading = false;
    }
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
        
        // Store all videos for filtering
        allVideos = uniqueVideos.slice(0, 5000); // Load more videos for pagination but limit to 5000
        
        // Hide loading indicator
        hideLoadingIndicator();
        
        // Display first page of videos
        displayVideos();
        
        // Load popular categories
        loadPopularCategories(uniqueVideos);
    } catch (error) {
        console.error('Error processing videos:', error);
        hideLoadingIndicator();
        // Fallback to sample data
        populateVideoGrids();
    }
}

// Function to show loading indicator
function showLoadingIndicator() {
    const trendingContainer = document.getElementById('trending-videos');
    const latestContainer = document.getElementById('latest-videos');
    
    if (trendingContainer) {
        trendingContainer.innerHTML = '<div class="loading-message">Loading videos...</div>';
    }
    
    if (latestContainer) {
        latestContainer.innerHTML = '<div class="loading-message">Loading videos...</div>';
    }
}

// Function to hide loading indicator
function hideLoadingIndicator() {
    const loadingMessages = document.querySelectorAll('.loading-message');
    loadingMessages.forEach(el => el.remove());
}

// Function to load popular categories
async function loadPopularCategories(videos) {
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
        
        // Convert to array and sort by count (descending), then take top 6
        const sortedCategories = Object.entries(categoryCount)
            .map(([name, count]) => ({ name, count }))
            .sort((a, b) => b.count - a.count)
            .slice(0, 6);
        
        // Display categories
        const categoriesContainer = document.getElementById('popular-categories');
        if (categoriesContainer) {
            categoriesContainer.innerHTML = sortedCategories.map(category => `
                <div class="category-card" data-category="${category.name}">
                    <div class="category-icon">
                        <i class="fas fa-tag"></i>
                    </div>
                    <h3>${category.name}</h3>
                    <span>${category.count.toLocaleString()} videos</span>
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
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Function to display videos for current page
function displayVideos() {
    const startIndex = (currentPage - 1) * videosPerPage;
    const endIndex = startIndex + videosPerPage;
    let videosToDisplay = allVideos.slice(startIndex, endIndex);
    
    // Apply filters for trending videos
    let trendingVideos = [...videosToDisplay];
    trendingVideos = filterVideosByDuration(trendingVideos, currentTrendingDurationFilter);
    trendingVideos = sortVideos(trendingVideos, currentTrendingSortBy);
    
    // Apply filters for latest videos
    let latestVideos = [...videosToDisplay];
    latestVideos = filterVideosByDuration(latestVideos, currentLatestDurationFilter);
    latestVideos = sortVideos(latestVideos, currentLatestSortBy);
    
    // Populate the grids with real data
    const trendingContainer = document.getElementById('trending-videos');
    const latestContainer = document.getElementById('latest-videos');
    
    if (trendingContainer && latestContainer) {
        // Split videos for trending and latest (first half for trending, second for latest)
        const half = Math.ceil(videosToDisplay.length / 2);
        const trendingVideosToDisplay = trendingVideos.slice(0, half);
        const latestVideosToDisplay = latestVideos.slice(half);
        
        // Create video cards for trending videos
        const trendingVideoCards = trendingVideosToDisplay.map(createVideoCard);
        
        // Create video cards for latest videos
        const latestVideoCards = latestVideosToDisplay.map(createVideoCard);
        
        // Replace content with video cards
        trendingContainer.innerHTML = trendingVideoCards.join('');
        latestContainer.innerHTML = latestVideoCards.join('');
    }
    
    // Update pagination controls
    updatePagination();
}

// Function to update pagination controls with numbered buttons
function updatePagination() {
    const totalPages = Math.ceil(allVideos.length / videosPerPage);
    const paginationContainer = document.getElementById('pagination-controls');
    
    // Show pagination controls only if there's more than one page
    if (paginationContainer) {
        if (totalPages > 1) {
            paginationContainer.style.display = 'flex';
            
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
        } else {
            paginationContainer.style.display = 'none';
        }
    }
}

// Function to go to a specific page
function goToPage(pageNumber) {
    if (pageNumber >= 1 && pageNumber <= Math.ceil(allVideos.length / videosPerPage)) {
        currentPage = pageNumber;
        displayVideos();
        // Scroll to top of page
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Event listeners for sorting and filtering
document.addEventListener('DOMContentLoaded', function() {
    // Load videos when page loads
    loadVideosFromJSON();
    
    // Add event listeners for trending video filters
    const trendingSortSelect = document.getElementById('trending-sort');
    const trendingDurationSelect = document.getElementById('trending-duration');
    
    if (trendingSortSelect) {
        trendingSortSelect.addEventListener('change', function() {
            currentTrendingSortBy = this.value;
            displayVideos();
        });
    }
    
    if (trendingDurationSelect) {
        trendingDurationSelect.addEventListener('change', function() {
            currentTrendingDurationFilter = this.value;
            displayVideos();
        });
    }
    
    // Add event listeners for latest video filters
    const latestSortSelect = document.getElementById('latest-sort');
    const latestDurationSelect = document.getElementById('latest-duration');
    
    if (latestSortSelect) {
        latestSortSelect.addEventListener('change', function() {
            currentLatestSortBy = this.value;
            displayVideos();
        });
    }
    
    if (latestDurationSelect) {
        latestDurationSelect.addEventListener('change', function() {
            currentLatestDurationFilter = this.value;
            displayVideos();
        });
    }
});

// Populate grids with sample data (fallback function)
function populateVideoGrids() {
    const trendingContainer = document.getElementById('trending-videos');
    const latestContainer = document.getElementById('latest-videos');
    
    if (trendingContainer && latestContainer) {
        // Create sample video cards
        const sampleVideos = Array.from({ length: 36 }, (_, i) => ({
            title: `Sample Video ${i + 1}`,
            thumbnail: `https://placehold.co/300x200/1a1a1a/ff6b6b?text=Video+${i + 1}`,
            detail_url: '#',
            external_url: '#',
            duration: ["15:30", "18:42", "22:15", "24:10", "28:05", "32:40", "35:15", "40:20"][Math.floor(Math.random() * 8)],
            views: ["1.2M", "980K", "2.1M", "3.5M", "1.8M", "1.5M", "2.7M", "1.3M"][Math.floor(Math.random() * 8)],
            upload_date: ["2 days ago", "1 week ago", "3 days ago", "2 weeks ago", "5 days ago", "4 days ago", "1 day ago", "3 days ago"][Math.floor(Math.random() * 8)]
        }));
        
        // Split sample videos between trending and latest
        const trendingVideos = sampleVideos.slice(0, 18);
        const latestVideos = sampleVideos.slice(18);
        
        // Create video cards
        const trendingVideoCards = trendingVideos.map(createVideoCard);
        const latestVideoCards = latestVideos.map(createVideoCard);
        
        // Replace content with video cards
        trendingContainer.innerHTML = trendingVideoCards.join('');
        latestContainer.innerHTML = latestVideoCards.join('');
    }
}
