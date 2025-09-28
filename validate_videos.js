const fs = require('fs');

// Read the videos.json file
fs.readFile('videos.json', 'utf8', (err, data) => {
    if (err) {
        console.error('Error reading file:', err);
        return;
    }

    try {
        const videos = JSON.parse(data);
        console.log(`Total videos: ${videos.length}`);

        // Validation counters
        let validVideos = 0;
        let invalidVideos = 0;
        let videosWithExternalUrl = 0;
        let videosWithDetailUrl = 0;
        let videosWithBothUrls = 0;
        let videosWithNoUrls = 0;

        // Validate each video
        const validVideosArray = videos.filter(video => {
            const hasExternalUrl = video.external_url && video.external_url.trim() !== '';
            const hasDetailUrl = video.detail_url && video.detail_url.trim() !== '' && video.detail_url !== '#';
            
            // Count URL statistics
            if (hasExternalUrl) videosWithExternalUrl++;
            if (hasDetailUrl) videosWithDetailUrl++;
            if (hasExternalUrl && hasDetailUrl) videosWithBothUrls++;
            if (!hasExternalUrl && !hasDetailUrl) {
                videosWithNoUrls++;
                return false; // Filter out videos with no URLs
            }
            
            // Check for required fields
            if (!video.title || video.title.trim() === '') {
                invalidVideos++;
                return false;
            }
            
            if (!video.thumbnail || video.thumbnail.trim() === '') {
                invalidVideos++;
                return false;
            }
            
            validVideos++;
            return true;
        });

        // Statistics
        console.log(`\nValidation Results:`);
        console.log(`Valid videos: ${validVideos}`);
        console.log(`Invalid videos: ${invalidVideos}`);
        console.log(`Videos with external_url: ${videosWithExternalUrl}`);
        console.log(`Videos with detail_url: ${videosWithDetailUrl}`);
        console.log(`Videos with both URLs: ${videosWithBothUrls}`);
        console.log(`Videos with no URLs: ${videosWithNoUrls}`);
        console.log(`Videos after filtering: ${validVideosArray.length}`);

        // Save cleaned data to a new file
        fs.writeFile('videos_cleaned.json', JSON.stringify(validVideosArray, null, 2), (err) => {
            if (err) {
                console.error('Error writing cleaned file:', err);
                return;
            }
            console.log('\nCleaned video data saved to videos_cleaned.json');
        });

        // Sample some videos to check quality
        console.log('\nSample of valid videos:');
        const sample = validVideosArray.slice(0, 5);
        sample.forEach((video, index) => {
            console.log(`\n${index + 1}. Title: ${video.title}`);
            console.log(`   Thumbnail: ${video.thumbnail}`);
            console.log(`   Detail URL: ${video.detail_url || 'None'}`);
            console.log(`   External URL: ${video.external_url || 'None'}`);
        });

    } catch (parseError) {
        console.error('Error parsing JSON:', parseError);
    }
});