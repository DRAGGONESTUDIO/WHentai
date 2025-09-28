// Add pagination variables at the top of the file
let currentPage = 1;
const videosPerPage = 36;
let allVideos = [];
let currentSortBy = 'date'; // Default sorting for newest page (changed from 'newest')
let displayedVideoIds = new Set(); // Track displayed video IDs to prevent duplicates
let currentDurationFilter = 'any'; // Default duration filter

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
    // In a real app with a backend, this data would come from the database
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
        case 'date':
            // Sort by date - newest first (most recent to oldest)
            // Since we don't have actual dates, we'll simulate this by shuffling
            // In a real implementation, you would sort by actual upload dates
            return sortedVideos.sort(() => Math.random() - 0.5);
        case 'views':
            // Sort by views - most views first (highest to lowest)
            // Since we don't have actual view counts, we'll simulate this by shuffling
            // In a real implementation, you would sort by actual view counts
            return sortedVideos.sort(() => Math.random() - 0.5);
        case 'duration':
            // Sort by duration - longest first (longest to shortest)
            // Since we don't have actual durations, we'll simulate this by shuffling
            // In a real implementation, you would sort by actual durations
            return sortedVideos.sort(() => Math.random() - 0.5);
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

// Function to load newest videos from videos.json
async function loadNewestVideos() {
    try {
        const response = await fetch('videos.json');
        const videos = await response.json();
        
        // Filter out videos without any URLs
        const validVideos = videos.filter(video => 
            (video.external_url && video.external_url.trim() !== '') || 
            (video.detail_url && video.detail_url.trim() !== '' && video.detail_url !== '#')
        );
        
        // Remove duplicate videos
        const uniqueVideos = removeDuplicateVideos(validVideos);
        
        // Apply duration filter first
        const durationFilteredVideos = filterVideosByDuration(uniqueVideos, currentDurationFilter);
        
        // Sort videos based on current sort setting
        const sortedVideos = sortVideos(durationFilteredVideos, currentSortBy);
        
        // Shuffle videos to avoid repetition
        const shuffledVideos = [...sortedVideos].sort(() => 0.5 - Math.random());
        
        // Take a larger sample and reshuffle for better distribution
        allVideos = shuffledVideos.slice(0, 3000); // Load more videos for pagination
        
        // Reset displayed video IDs
        displayedVideoIds.clear();
        
        // Display first page of videos
        displayVideos();
    } catch (error) {
        console.error('Error loading newest videos:', error);
    }
}

// Function to display videos for current page
function displayVideos() {
    const startIndex = (currentPage - 1) * videosPerPage;
    const endIndex = startIndex + videosPerPage;
    const videosToDisplay = allVideos.slice(startIndex, endIndex);
    
    const newestContainer = document.getElementById('newest-videos');
    if (newestContainer) {
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
            newestContainer.innerHTML = videoCards.join('');
        } else {
            newestContainer.innerHTML += videoCards.join('');
        }
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

// Function to handle sort filter changes
function handleSortChange() {
    const sortFilter = document.getElementById('sort-filter');
    if (sortFilter) {
        currentSortBy = sortFilter.value;
        // Reset to first page when sorting
        currentPage = 1;
        // Re-load videos with new sort order
        loadNewestVideos();
    }
}

// Function to handle duration filter changes (updated function)
function handleDurationChange() {
    const durationFilter = document.getElementById('duration-filter');
    if (durationFilter) {
        currentDurationFilter = durationFilter.value;
        // Reset to first page when filtering
        currentPage = 1;
        // Re-load videos with new duration filter
        loadNewestVideos();
    }
}

// Function to initialize the page
function init() {
    // Load newest videos
    loadNewestVideos();
    
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
    
    // Set up load more button
    const loadMoreButton = document.getElementById('load-more');
    if (loadMoreButton) {
        loadMoreButton.addEventListener('click', () => {
            loadMoreVideos();
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
document.addEventListener('DOMContentLoaded', init);