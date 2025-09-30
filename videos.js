// Load videos from JSON file
let allVideos = [];
let currentCategory = '';
let currentPage = 1;
const videosPerPage = 20;

// Fetch videos from JSON file
fetch('videos.json')
    .then(response => response.json())
    .then(data => {
        allVideos = data;
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

// Function to create video card HTML with proper metadata display
function createVideoCard(video, index = 0) {
    // Default values for missing properties
    const title = video.title || 'Untitled Video';
    const thumbnail = video.thumbnail || 'https://placehold.co/300x200/1a1a1a/ff6b6b?text=No+Thumbnail';
    const detailUrl = video.detail_url || '#';
    
    // Always prioritize external_url over detail_url
    // Only use detail_url as a fallback when external_url is empty or invalid
    const externalUrl = video.external_url && video.external_url.trim() !== '' && video.external_url !== '#' 
        ? video.external_url 
        : detailUrl;
    
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