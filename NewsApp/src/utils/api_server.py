from flask import Flask, jsonify
from flask_cors import CORS
from indianexpress_scraper import IndianExpressScraper
import threading
import time

app = Flask(__name__)
CORS(app)

# Global variable to store cached articles
cached_articles = []
last_update = 0
cache_duration = 300  # 5 minutes

def update_cache():
    """Update the cached articles"""
    global cached_articles, last_update
    try:
        scraper = IndianExpressScraper()
        articles = scraper.scrape_latest_news(30)
        cached_articles = articles
        last_update = time.time()
        print(f"Cache updated with {len(articles)} articles from Indian Express")
    except Exception as e:
        print(f"Error updating cache: {e}")

@app.route('/api/news', methods=['GET'])
def get_news():
    """Get latest news articles"""
    global cached_articles, last_update
    
    # Update cache if it's expired or empty
    if time.time() - last_update > cache_duration or not cached_articles:
        update_cache()
    
    return jsonify({
        'articles': cached_articles,
        'total': len(cached_articles),
        'last_updated': last_update
    })

@app.route('/api/news/refresh', methods=['POST'])
def refresh_news():
    """Manually refresh the news cache"""
    update_cache()
    return jsonify({
        'message': 'News refreshed successfully',
        'total': len(cached_articles)
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'articles_cached': len(cached_articles),
        'last_update': last_update
    })

if __name__ == '__main__':
    # Initial cache update
    update_cache()
    
    # Start the Flask server
    app.run(host='0.0.0.0', port=5000, debug=True) 