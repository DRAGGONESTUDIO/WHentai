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
    
    // Generate HTML for video cards, passing index for consistent duration assignment
    const videoHTML = videosToDisplay.map((video, index) => createVideoCard(video, index)).join('');
    
    // Replace content with video cards
    videoGrid.innerHTML = videoHTML;
    
    // Update pagination controls
    updatePagination();
}

// Function to go to a specific page
function goToPage(pageNumber) {
    if (pageNumber >= 1 && pageNumber <= Math.ceil(filteredVideos.length / videosPerPage)) {
        currentPage = pageNumber;
        displayVideos();
        updatePagination();
        
        // Scroll to top of video grid
        const videoGrid = document.getElementById('video-grid');
        if (videoGrid) {
            videoGrid.scrollIntoView({ behavior: 'smooth' });
        }
    }
}

// Function to update pagination controls with numbered buttons
function updatePagination() {
    const totalPages = Math.ceil(filteredVideos.length / videosPerPage);
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

// Function to create video card HTML with proper metadata display
function createVideoCard(video, index = 0) {
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
    const durationSeed = title.length + (detailUrl ? detailUrl.length : 0) + index;
    const durationIndex = durationSeed % durations.length;
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
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initSearch();
});