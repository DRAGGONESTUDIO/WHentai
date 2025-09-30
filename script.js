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

// Function to create video card HTML
function createVideoCard(video) {
    // Default values for missing properties
    const title = video.title || 'Untitled Video';
    let thumbnail = video.thumbnail || 'https://placehold.co/300x200/1a1a1a/ff6b6b?text=No+Thumbnail';
    const detailUrl = video.detail_url || '#';
    
    // Check if thumbnail URL is valid, if not use fallback
    if (!thumbnail || thumbnail.includes('undefined') || thumbnail.includes('null') || 
        !thumbnail.startsWith('http') || thumbnail.trim() === '') {
        thumbnail = 'https://placehold.co/300x200/1a1a1a/ff6b6b?text=No+Thumbnail';
    }
    
    // Additional check for broken image URLs
    const brokenImagePatterns = ['data:image', 'blob:', 'javascript:'];
    if (brokenImagePatterns.some(pattern => thumbnail.startsWith(pattern))) {
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
        
        // Remove duplicate videos
        const uniqueVideos = removeDuplicateVideos(validVideos);
        
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
            // Hide pagination if there's only one page
            paginationContainer.style.display = 'none';
        }
    }
}

// Function to go to a specific page
function goToPage(pageNumber) {
    const totalPages = Math.ceil(allVideos.length / videosPerPage);
    if (pageNumber >= 1 && pageNumber <= totalPages) {
        currentPage = pageNumber;
        displayVideos();
        
        // Scroll to top of page
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// The loadMoreVideos function has been removed as we're now using pagination instead

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
    
    // Hide pagination controls when using sample data
    const paginationContainer = document.getElementById('pagination-controls');
    if (paginationContainer) {
        paginationContainer.style.display = 'none';
    }
}

// Function to handle search
function handleSearch(query) {
    if (query) {
        // Redirect to search page with query
        window.location.href = `search.html?q=${encodeURIComponent(query)}`;
    }
}

// Function to handle trending sort filter changes
function handleTrendingSortChange() {
    const sortFilter = document.getElementById('sort-filter');
    if (sortFilter) {
        currentTrendingSortBy = sortFilter.value;
        // Reset to first page when sorting
        currentPage = 1;
        // Re-display videos with new sort order
        displayVideos();
    }
}

// Function to handle trending duration filter changes
function handleTrendingDurationChange() {
    const durationFilter = document.getElementById('duration-filter');
    if (durationFilter) {
        currentTrendingDurationFilter = durationFilter.value;
        // Reset to first page when filtering
        currentPage = 1;
        // Re-display videos with new duration filter
        displayVideos();
    }
}

// Function to handle latest sort filter changes
function handleLatestSortChange() {
    const sortFilter = document.getElementById('latest-sort-filter');
    if (sortFilter) {
        currentLatestSortBy = sortFilter.value;
        // Reset to first page when sorting
        currentPage = 1;
        // Re-display videos with new sort order
        displayVideos();
    }
}

// Function to handle latest duration filter changes
function handleLatestDurationChange() {
    const durationFilter = document.getElementById('latest-duration-filter');
    if (durationFilter) {
        currentLatestDurationFilter = durationFilter.value;
        // Reset to first page when filtering
        currentPage = 1;
        // Re-display videos with new duration filter
        displayVideos();
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
    
    // Set up trending filters
    const trendingSortFilter = document.getElementById('sort-filter');
    if (trendingSortFilter) {
        trendingSortFilter.addEventListener('change', handleTrendingSortChange);
    }
    
    const trendingDurationFilter = document.getElementById('duration-filter');
    if (trendingDurationFilter) {
        trendingDurationFilter.addEventListener('change', handleTrendingDurationChange);
    }
    
    // Set up latest filters
    const latestSortFilter = document.getElementById('latest-sort-filter');
    if (latestSortFilter) {
        latestSortFilter.addEventListener('change', handleLatestSortChange);
    }
    
    const latestDurationFilter = document.getElementById('latest-duration-filter');
    if (latestDurationFilter) {
        latestDurationFilter.addEventListener('change', handleLatestDurationChange);
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