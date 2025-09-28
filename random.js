// Add pagination variables at the top of the file
let currentPage = 1;
const videosPerPage = 36;
let allVideos = [];

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

// Function to get random videos from videos.json
async function loadRandomVideos() {
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
        
        // Shuffle the videos array using Fisher-Yates algorithm
        const shuffledVideos = [...uniqueVideos];
        for (let i = shuffledVideos.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffledVideos[i], shuffledVideos[j]] = [shuffledVideos[j], shuffledVideos[i]];
        }
        
        // Take a larger sample and reshuffle for better distribution
        allVideos = shuffledVideos.slice(0, 3000); // Load more videos for pagination
        
        // Display first page of videos
        displayVideos();
    } catch (error) {
        console.error('Error loading random videos:', error);
    }
}

// Function to display videos for current page
function displayVideos() {
    const startIndex = (currentPage - 1) * videosPerPage;
    const endIndex = startIndex + videosPerPage;
    const videosToDisplay = allVideos.slice(startIndex, endIndex);
    
    const randomContainer = document.getElementById('random-videos');
    if (randomContainer) {
        // If this is the first page, replace content, otherwise append
        if (currentPage === 1) {
            randomContainer.innerHTML = videosToDisplay.map(createVideoCard).join('');
        } else {
            randomContainer.innerHTML += videosToDisplay.map(createVideoCard).join('');
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
            // Reset to first page and reload
            currentPage = 1;
            loadRandomVideos();
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
document.addEventListener('DOMContentLoaded', init);