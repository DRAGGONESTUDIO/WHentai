// FINAL THUMBNAIL SOLUTION
// This is a comprehensive solution to fix all thumbnail issues once and for all

// Enhanced thumbnail validation function
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
    
    // Check if thumbnail is a placeholder image
    const placeholderPatterns = [
        'placehold.co',
        'placeholder',
        'no thumbnail',
        'no image',
        'image not found',
        'thumbnail not available',
        'not available',
        'default',
        'missing'
    ];
    
    const thumbnailLower = trimmedUrl.toLowerCase();
    
    // If any placeholder pattern is found, it's not a valid thumbnail
    for (const pattern of placeholderPatterns) {
        if (thumbnailLower.includes(pattern)) {
            return false;
        }
    }
    
    // Check for common placeholder URL patterns
    if (thumbnailLower.startsWith('data:image') || 
        thumbnailLower.startsWith('blob:') || 
        thumbnailLower.startsWith('javascript:')) {
        return false;
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

// Enhanced video card creation function with robust error handling
function createVideoCard(video, index = 0) {
    // Validate input
    if (!video) {
        console.error('Invalid video object provided to createVideoCard');
        return '';
    }
    
    // Default values for missing properties
    const title = (video.title && typeof video.title === 'string') ? video.title.trim() : 'Untitled Video';
    const thumbnail = (video.thumbnail && typeof video.thumbnail === 'string') ? video.thumbnail.trim() : '';
    const detailUrl = (video.detail_url && typeof video.detail_url === 'string') ? video.detail_url.trim() : '#';
    
    // Always prioritize external_url over detail_url
    // Only use detail_url as a fallback when external_url is empty or invalid
    let externalUrl = detailUrl;
    if (video.external_url && 
        typeof video.external_url === 'string' && 
        video.external_url.trim() !== '' && 
        video.external_url !== '#') {
        externalUrl = video.external_url.trim();
    }
    
    // Handle thumbnail with robust error handling
    let thumbnailHTML = '';
    if (isValidThumbnail(thumbnail)) {
        // Valid thumbnail - use it with error handling
        thumbnailHTML = `
            <img src="${thumbnail}" alt="${title}" 
                 loading="lazy"
                 onerror="this.src='https://placehold.co/300x200/1a1a1a/ff6b6b?text=Thumbnail+Error'; this.onerror=null;"
                 onload="this.style.opacity='1'; this.style.visibility='visible';">
        `;
    } else {
        // No valid thumbnail - show error placeholder
        thumbnailHTML = `
            <img src="https://placehold.co/300x200/1a1a1a/ff6b6b?text=No+Thumbnail" alt="${title}" 
                 loading="lazy"
                 style="opacity:1; visibility:visible;">
        `;
    }
    
    // Create the complete video card HTML
    return `
        <div class="video-card" data-video-index="${index}">
            <a href="${externalUrl}" target="_blank" rel="noopener noreferrer">
                <div class="video-thumbnail">
                    ${thumbnailHTML}
                </div>
                <div class="video-info">
                    <div class="video-title">${title}</div>
                </div>
            </a>
        </div>
    `;
}

// Enhanced video loading and display function
function loadAndDisplayVideos() {
    const videoGrid = document.getElementById('video-grid');
    if (!videoGrid) {
        console.error('Video grid element not found');
        return;
    }
    
    // Show loading message
    videoGrid.innerHTML = '<div class="loading-message">Loading videos...</div>';
    
    // Fetch videos from JSON file
    fetch('videos.json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Validate data
            if (!Array.isArray(data)) {
                throw new Error('Invalid data format: expected array');
            }
            
            // Filter videos with valid thumbnails
            const videosWithValidThumbnails = filterVideosWithValidThumbnails(data);
            
            // Check if we have any videos left
            if (videosWithValidThumbnails.length === 0) {
                videoGrid.innerHTML = `
                    <div class="no-results">
                        <h3>No Videos Found</h3>
                        <p>No videos with valid thumbnails are available.</p>
                    </div>
                `;
                return;
            }
            
            // Limit to first 100 videos for performance (can be adjusted)
            const displayVideos = videosWithValidThumbnails.slice(0, 100);
            
            // Generate HTML for video cards
            const videoHTML = displayVideos.map((video, index) => createVideoCard(video, index)).join('');
            
            // Display videos
            videoGrid.innerHTML = videoHTML;
            
            // Log statistics
            console.log(`Loaded ${displayVideos.length} videos with valid thumbnails out of ${data.length} total videos`);
            console.log(`${data.length - videosWithValidThumbnails.length} videos were filtered out due to invalid thumbnails`);
        })
        .catch(error => {
            console.error('Error loading videos:', error);
            videoGrid.innerHTML = `
                <div class="error-message">
                    <h3>Error Loading Videos</h3>
                    <p>Unable to load video data: ${error.message}</p>
                    <p>Please try again later.</p>
                </div>
            `;
        });
}

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    // Node.js environment
    module.exports = {
        isValidThumbnail,
        filterVideosWithValidThumbnails,
        createVideoCard,
        loadAndDisplayVideos
    };
} else if (typeof window !== 'undefined') {
    // Browser environment
    window.finalThumbnailSolution = {
        isValidThumbnail,
        filterVideosWithValidThumbnails,
        createVideoCard,
        loadAndDisplayVideos
    };
}