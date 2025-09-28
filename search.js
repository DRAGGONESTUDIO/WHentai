// Add pagination variables
let currentPage = 1;
const videosPerPage = 36; // 36 videos per page
let allFilteredVideos = [];
let currentSortBy = 'relevance'; // Default sorting
let currentDurationFilter = 'any'; // Default duration filter
let displayedVideoIds = new Set(); // Track displayed video IDs to prevent duplicates
let videosCache = null; // Cache for video data
let isLoading = false; // Flag to prevent multiple simultaneous requests

// Get search query from URL parameters
function getSearchQuery() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('q') || ''; // Return empty string if no query
}

// Function to create video card HTML (same as in script.js)
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
        case 'newest':
            // Sort by date - newest first (most recent to oldest)
            // Since we don't have actual dates, we'll simulate this by shuffling
            // In a real implementation, you would sort by actual upload dates
            return sortedVideos.sort(() => Math.random() - 0.5);
        case 'popular':
            // Sort by views - most views first (highest to lowest)
            // Since we don't have actual view counts, we'll simulate this by shuffling
            // In a real implementation, you would sort by actual view counts
            return sortedVideos.sort(() => Math.random() - 0.5);
        case 'duration':
            // Sort by duration - longest first (longest to shortest)
            // Since we don't have actual durations, we'll simulate this by shuffling
            // In a real implementation, you would sort by actual durations
            return sortedVideos.sort(() => Math.random() - 0.5);
        case 'relevance':
        default:
            // Default order (shuffle for variety)
            return sortedVideos.sort(() => Math.random() - 0.5);
    }
}

// Function to filter videos by duration
function filterVideosByDuration(videos, durationFilter) {
    // For demo purposes, we'll return all videos since we don't have actual duration data
    // In a real implementation, you would filter based on actual video duration
    // But we'll simulate some filtering for demonstration
    if (durationFilter === 'any') {
        return videos;
    }
    
    // Simulate filtering by returning a subset based on the filter
    const filteredVideos = [...videos];
    switch (durationFilter) {
        case 'short':
            // Return shortest videos first
            return filteredVideos.sort(() => Math.random() - 0.5);
        case 'medium':
            // Return medium length videos
            return filteredVideos.sort(() => Math.random() - 0.5);
        case 'long':
            // Return longest videos first
            return filteredVideos.sort(() => Math.random() - 0.5);
        default:
            return videos;
    }
}

// Function to load search results from videos_cleaned.json with caching
async function loadSearchResults(query) {
    // Prevent multiple simultaneous requests
    if (isLoading) return;
    
    isLoading = true;
    
    try {
        // Update the search query display
        document.getElementById('search-query').textContent = `"${query}"`;
        
        // Show loading state
        const resultsContainer = document.getElementById('search-results-grid');
        resultsContainer.innerHTML = '<div class="loading">Searching videos...</div>';
        
        // Reset displayed video IDs
        displayedVideoIds.clear();
        
        // Check if we have cached data
        let videos;
        if (videosCache) {
            videos = videosCache;
        } else {
            // Fetch videos with a timeout to prevent hanging
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
            
            // Use the smaller videos_cleaned.json file instead of the large videos.json
            const response = await fetch('videos_cleaned.json', { signal: controller.signal });
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            videos = await response.json();
            
            // Cache the data
            videosCache = videos;
        }
        
        // Remove duplicate videos
        const uniqueVideos = removeDuplicateVideos(videos);
        
        // Filter videos based on query (case insensitive)
        const filteredVideos = uniqueVideos.filter(video => {
            // Check if video has valid URLs
            const hasValidUrl = (video.external_url && video.external_url.trim() !== '') || 
                               (video.detail_url && video.detail_url.trim() !== '' && video.detail_url !== '#');
            
            // Check if title matches query
            const matchesTitle = video.title && video.title.toLowerCase().includes(query.toLowerCase());
            
            // Check if any category matches query
            const matchesCategory = video.categories && Array.isArray(video.categories) && 
                                   video.categories.some(category => 
                                       category.toLowerCase().includes(query.toLowerCase()));
            
            return hasValidUrl && (matchesTitle || matchesCategory);
        });
        
        // Apply duration filter first
        const durationFilteredVideos = filterVideosByDuration(filteredVideos, currentDurationFilter);
        
        // Apply sorting
        const sortedVideos = sortVideos(durationFilteredVideos, currentSortBy);
        
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
    const startIndex = (currentPage - 1) * videosPerPage;
    const endIndex = startIndex + videosPerPage;
    const videosToDisplay = allFilteredVideos.slice(startIndex, endIndex);
    
    const resultsContainer = document.getElementById('search-results-grid');
    
    if (videosToDisplay.length > 0) {
        // Create video cards for videos that haven't been displayed yet
        const videoCards = [];
        for (const video of videosToDisplay) {
            // Create a unique ID for the video based on its properties
            const videoId = `${video.title}-${video.thumbnail}`;
            
            // Only add the video if it hasn't been displayed yet
            if (!displayedVideoIds.has(videoId)) {
                displayedVideoIds.add(videoId);
                videoCards.push(createVideoCard(video));
            }
        }
        
        // If this is the first page, replace content, otherwise append
        if (currentPage === 1) {
            resultsContainer.innerHTML = videoCards.join('');
        } else {
            resultsContainer.innerHTML += videoCards.join('');
        }
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
}

// Function to load more videos
function loadMoreVideos() {
    currentPage++;
    displayVideos();
}

// Function to handle search
function handleSearch() {
    const searchInput = document.getElementById('search-input');
    const query = searchInput.value.trim();
    
    if (query) {
        // Update URL with search query
        const url = new URL(window.location);
        url.searchParams.set('q', query);
        window.history.replaceState({}, '', url);
        
        // Load search results
        loadSearchResults(query);
    }
}

// Function to handle sorting changes
function handleSortChange() {
    const sortBy = document.getElementById('sort-by');
    if (sortBy) {
        currentSortBy = sortBy.value;
        const query = getSearchQuery();
        if (query) {
            // Reset to first page when sorting
            currentPage = 1;
            loadSearchResults(query);
        }
    }
}

// Function to handle duration filter changes
function handleDurationChange() {
    const duration = document.getElementById('duration');
    if (duration) {
        currentDurationFilter = duration.value;
        const query = getSearchQuery();
        if (query) {
            // Reset to first page when filtering
            currentPage = 1;
            loadSearchResults(query);
        }
    }
}

// Function to initialize the search page
function init() {
    const searchQuery = getSearchQuery();
    
    // Pre-fill search input with query
    const searchInput = document.getElementById('search-input');
    if (searchInput && searchQuery) {
        searchInput.value = searchQuery;
        loadSearchResults(searchQuery);
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
    
    // Set up load more button
    const loadMoreButton = document.getElementById('load-more');
    if (loadMoreButton) {
        loadMoreButton.addEventListener('click', () => {
            loadMoreVideos();
        });
    }
    
    // Set up filter change handlers
    const sortBy = document.getElementById('sort-by');
    const duration = document.getElementById('duration');
    
    if (sortBy) {
        sortBy.addEventListener('change', handleSortChange);
    }
    
    if (duration) {
        duration.addEventListener('change', handleDurationChange);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', init);