from flask import Flask, jsonify, send_from_directory
import json
import subprocess
import os
import sys
from datetime import datetime

app = Flask(__name__)

# Simple route to serve static files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# API endpoint to get videos
@app.route('/api/videos')
def api_videos():
    try:
        with open('videos.json', 'r', encoding='utf-8') as f:
            videos = json.load(f)
        return jsonify(videos)
    except FileNotFoundError:
        return jsonify([])

# Endpoint to run scraper manually
@app.route('/scrape')
def scrape():
    try:
        result = subprocess.run(['python', 'automated_scraper.py'], 
                              capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            # Reload videos after scraping
            try:
                with open('videos.json', 'r', encoding='utf-8') as f:
                    videos = json.load(f)
                return jsonify({
                    'success': True, 
                    'message': 'Scraping completed successfully',
                    'video_count': len(videos)
                })
            except:
                return jsonify({
                    'success': True, 
                    'message': 'Scraping completed, but could not load video count',
                    'video_count': 0
                })
        else:
            return jsonify({
                'success': False, 
                'message': f'Scraping failed: {result.stderr}'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error running scraper: {str(e)}'
        }), 500

# Endpoint to get scraping status
@app.route('/api/status')
def scraping_status():
    try:
        if os.path.exists('scraping_summary.json'):
            with open('scraping_summary.json', 'r') as f:
                summary = json.load(f)
            return jsonify(summary)
        else:
            return jsonify({
                'status': 'unknown',
                'message': 'No scraping summary available'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error reading status: {str(e)}'
        }), 500

# Endpoint to get video statistics
@app.route('/api/stats')
def video_stats():
    try:
        with open('videos.json', 'r', encoding='utf-8') as f:
            videos = json.load(f)
        
        # Calculate statistics
        total_videos = len(videos)
        
        # Get recent videos (last 24 hours)
        recent_count = 0
        if total_videos > 0:
            try:
                # Try to get recent videos count from summary if available
                if os.path.exists('scraping_summary.json'):
                    with open('scraping_summary.json', 'r') as f:
                        summary = json.load(f)
                    recent_count = summary.get('recent_videos', 0)
            except:
                pass
        
        # Get category statistics
        category_count = {}
        for video in videos:
            if 'categories' in video and isinstance(video['categories'], list):
                for category in video['categories']:
                    if category:  # Only count non-empty categories
                        category_count[category] = category_count.get(category, 0) + 1
        
        # Get top 10 categories
        top_categories = sorted(category_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return jsonify({
            'total_videos': total_videos,
            'recent_videos': recent_count,
            'top_categories': top_categories,
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': f'Error calculating stats: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)