// Function to update video statistics
async function updateVideoStats() {
    try {
        const response = await fetch('/api/videos');
        const videos = await response.json();
        
        const statsContainer = document.getElementById('video-stats');
        statsContainer.innerHTML = `
            <p><strong>Total Videos:</strong> ${videos.length}</p>
            <p><strong>Last Updated:</strong> ${new Date().toLocaleString()}</p>
        `;
    } catch (error) {
        console.error('Error loading video stats:', error);
        document.getElementById('video-stats').innerHTML = '<p>Error loading statistics</p>';
    }
}

// Function to load recent videos
async function loadRecentVideos() {
    try {
        const response = await fetch('/api/videos');
        const videos = await response.json();
        
        const recentContainer = document.getElementById('recent-videos');
        if (videos.length > 0) {
            const recentVideos = videos.slice(0, 5);
            recentContainer.innerHTML = recentVideos.map(video => `
                <div class="video-item">
                    <img src="${video.thumbnail}" alt="${video.title}" class="video-thumb">
                    <div class="video-details">
                        <h4>${video.title}</h4>
                        <p><a href="${video.detail_url}" target="_blank">View Details</a> | 
                        <a href="${video.external_url}" target="_blank">External Link</a></p>
                    </div>
                </div>
            `).join('');
        } else {
            recentContainer.innerHTML = '<p>No videos found</p>';
        }
    } catch (error) {
        console.error('Error loading recent videos:', error);
        document.getElementById('recent-videos').innerHTML = '<p>Error loading videos</p>';
    }
}

// Function to run the scraper
async function runScraper() {
    const scrapeBtn = document.getElementById('scrape-btn');
    const statusDiv = document.getElementById('scrape-status');
    
    // Disable button and show loading state
    scrapeBtn.disabled = true;
    scrapeBtn.textContent = 'Scraping...';
    statusDiv.innerHTML = '<p class="loading">Running scraper, please wait...</p>';
    
    try {
        const response = await fetch('/scrape');
        const result = await response.json();
        
        if (result.success) {
            statusDiv.innerHTML = `<p class="success">${result.message}</p>`;
            // Refresh stats and recent videos
            updateVideoStats();
            loadRecentVideos();
        } else {
            statusDiv.innerHTML = `<p class="error">Error: ${result.message}</p>`;
        }
    } catch (error) {
        console.error('Error running scraper:', error);
        statusDiv.innerHTML = `<p class="error">Error running scraper: ${error.message}</p>`;
    } finally {
        // Re-enable button
        scrapeBtn.disabled = false;
        scrapeBtn.textContent = 'Run Scraper';
    }
}

// Function to initialize the admin panel
function init() {
    // Load initial data
    updateVideoStats();
    loadRecentVideos();
    
    // Set up event listeners
    const scrapeBtn = document.getElementById('scrape-btn');
    if (scrapeBtn) {
        scrapeBtn.addEventListener('click', runScraper);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', init);