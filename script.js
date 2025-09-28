// Add pagination variables
let currentPage = 1;
const videosPerPage = 36; // 18 trending + 18 latest per page
let allVideos = [];
let displayedVideoIds = new Set(); // Track displayed video IDs to prevent duplicates

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
    
    // Use actual metadata if available, otherwise generate random values for demo
    const duration = video.duration || ["15:30", "18:42", "22:15", "24:10", "28:05", "32:40", "35:15", "40:20"][Math.floor(Math.random() * 8)];
    const views = video.views || ["1.2M", "980K", "2.1M", "3.5M", "1.8M", "1.5M", "2.7M", "1.3M"][Math.floor(Math.random() * 8)];
    const uploadDate = video.upload_date || ["2 days ago", "1 week ago", "3 days ago", "2 weeks ago", "5 days ago", "4 days ago", "1 day ago", "3 days ago"][Math.floor(Math.random() * 8)];
    
    return `
        <div class="video-card">
            <a href="${externalUrl}" target="_blank" rel="noopener noreferrer">
                <div class="video-thumbnail">
                    <img src="${thumbnail}" alt="${title}" onerror="this.src='https://placehold.co/300x200/1a1a1a/ff6b6b?text=No+Thumbnail';">
                    <div class="video-duration">${duration}</div>
                </div>
                <div class="video-info">
                    <div class="video-title">${title}</div>
                    <div class="video-meta">
                        <div class="video-views">
                            <i class="fas fa-eye"></i>
                            ${views}
                        </div>
                        <div class="video-date">
                            <i class="far fa-clock"></i>
                            ${uploadDate}
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

// Function to load videos from videos.json
async function loadVideosFromJSON() {
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
        
        // Shuffle videos to avoid repetition
        const shuffledVideos = [...uniqueVideos].sort(() => 0.5 - Math.random());
        
        // Take a larger sample for pagination
        allVideos = shuffledVideos.slice(0, 5000); // Load more videos for pagination
        
        // Reset displayed video IDs
        displayedVideoIds.clear();
        
        // Display first page of videos
        displayVideos();
        
        // Load popular categories
        loadPopularCategories(uniqueVideos);
    } catch (error) {
        console.error('Error loading videos:', error);
        // Fallback to sample data
        populateVideoGrids();
    }
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
    const videosToDisplay = allVideos.slice(startIndex, endIndex);
    
    // Populate the grids with real data
    const trendingContainer = document.getElementById('trending-videos');
    const latestContainer = document.getElementById('latest-videos');
    
    if (trendingContainer && latestContainer) {
        // Split videos for trending and latest (first half for trending, second for latest)
        const half = Math.ceil(videosToDisplay.length / 2);
        const trendingVideos = videosToDisplay.slice(0, half);
        const latestVideos = videosToDisplay.slice(half);
        
        // Create video cards for trending videos that haven't been displayed yet
        const trendingVideoCards = [];
        for (const video of trendingVideos) {
            // Create a unique ID for the video based on its properties
            const videoId = `${video.title}-${video.thumbnail}`;
            
            // Only add the video if it hasn't been displayed yet
            if (!displayedVideoIds.has(videoId)) {
                displayedVideoIds.add(videoId);
                trendingVideoCards.push(createVideoCard(video));
            }
        }
        
        // Create video cards for latest videos that haven't been displayed yet
        const latestVideoCards = [];
        for (const video of latestVideos) {
            // Create a unique ID for the video based on its properties
            const videoId = `${video.title}-${video.thumbnail}`;
            
            // Only add the video if it hasn't been displayed yet
            if (!displayedVideoIds.has(videoId)) {
                displayedVideoIds.add(videoId);
                latestVideoCards.push(createVideoCard(video));
            }
        }
        
        // Clear containers only on first page
        if (currentPage === 1) {
            trendingContainer.innerHTML = trendingVideoCards.join('');
            latestContainer.innerHTML = latestVideoCards.join('');
        } else {
            // Append new videos
            trendingContainer.innerHTML += trendingVideoCards.join('');
            latestContainer.innerHTML += latestVideoCards.join('');
        }
    }
}

// Function to load more videos
function loadMoreVideos() {
    currentPage++;
    displayVideos();
}

// Sample video data - fallback if videos.json fails to load
const sampleVideos = [
    {
        title: "Demon Slayer - Tanjiro's Adventure",
        thumbnail: "https://placehold.co/300x200/1a1a1a/ff6b6b?text=Video+1",
        detail_url: "#",
        external_url: "#"
    },
    {
        title: "My Hero Academia - Hero vs Villain",
        thumbnail: "https://placehold.co/300x200/1a1a1a/ff6b6b?text=Video+2",
        detail_url: "#",
        external_url: "#"
    },
    {
        title: "Attack on Titan - Final Season",
        thumbnail: "https://placehold.co/300x200/1a1a1a/ff6b6b?text=Video+3",
        detail_url: "#",
        external_url: "#"
    },
    {
        title: "Spirited Away - Studio Ghibli",
        thumbnail: "https://placehold.co/300x200/1a1a1a/ff6b6b?text=Video+4",
        detail_url: "#",
        external_url: "#"
    },
    {
        title: "One Piece - Pirate King Dream",
        thumbnail: "https://placehold.co/300x200/1a1a1a/ff6b6b?text=Video+5",
        detail_url: "#",
        external_url: "#"
    },
    {
        title: "Naruto - Shadow Clone Jutsu",
        thumbnail: "https://placehold.co/300x200/1a1a1a/ff6b6b?text=Video+6",
        detail_url: "#",
        external_url: "#"
    },
    {
        title: "Dragon Ball Z - Super Saiyan",
        thumbnail: "https://placehold.co/300x200/1a1a1a/ff6b6b?text=Video+7",
        detail_url: "#",
        external_url: "#"
    },
    {
        title: "Death Note - Light's Plan",
        thumbnail: "https://placehold.co/300x200/1a1a1a/ff6b6b?text=Video+8",
        detail_url: "#",
        external_url: "#"
    }
];

// Function to populate video grids with sample data
function populateVideoGrids() {
    const trendingContainer = document.getElementById('trending-videos');
    const latestContainer = document.getElementById('latest-videos');
    
    if (trendingContainer) {
        trendingContainer.innerHTML = sampleVideos.map(createVideoCard).join('');
    }
    
    if (latestContainer) {
        latestContainer.innerHTML = sampleVideos.map(createVideoCard).join('');
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
    // Load videos
    loadVideosFromJSON();
    
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
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', init);

// Add smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});