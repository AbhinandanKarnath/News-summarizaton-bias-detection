# News App with The Hindu Scraper

This application now includes a web scraper that fetches the latest news articles directly from [The Hindu](https://www.thehindu.com/) website and displays them on the home page.

## Features

- **Real-time News Scraping**: Automatically fetches latest articles from The Hindu
- **Article Categorization**: Automatically categorizes articles (Politics, Technology, Sports, Business, etc.)
- **Fallback System**: Falls back to the original API if scraping fails
- **Caching**: Implements 5-minute caching to avoid excessive requests
- **Responsive Design**: Beautiful UI with modern styling

## How to Run

### Option 1: Using the Batch File (Windows)
1. Double-click `start_app.bat`
2. The application will automatically install dependencies and start both servers

### Option 2: Manual Start
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the Python API server:
   ```bash
   cd src/utils
   python api_server.py
   ```

3. In a new terminal, start the React app:
   ```bash
   npm run dev
   ```

## API Endpoints

- `GET /api/news` - Get latest news articles
- `POST /api/news/refresh` - Manually refresh the news cache
- `GET /api/health` - Health check endpoint

## Data Structure

Each article contains:
- `title`: Article headline
- `description`: Article summary
- `url`: Link to the full article
- `image`: Article image URL (if available)
- `author`: Article author
- `publishedAt`: Publication date
- `source`: News source (The Hindu)
- `category`: Article category (Politics, Technology, Sports, etc.)

## Technical Details

### Scraping Strategy
The scraper uses multiple strategies to extract articles:
1. Primary method: Looks for article elements with specific CSS selectors
2. Alternative method: Searches for links that appear to be articles
3. Fallback: Uses the original API if scraping fails

### Caching
- Articles are cached for 5 minutes to reduce server load
- Cache is automatically refreshed when expired
- Manual refresh endpoint available

### Error Handling
- Network timeouts and connection errors are handled gracefully
- Fallback to original API if scraping fails
- Detailed error logging for debugging

## Troubleshooting

### Common Issues

1. **"Error loading punkt"**: This is related to NLTK data download. The scraper doesn't use NLTK, so this error can be ignored.

2. **No articles showing**: 
   - Check if the Python API server is running on port 5000
   - Check browser console for network errors
   - Try the manual refresh endpoint

3. **Slow loading**: 
   - The first request may take longer as it needs to scrape the website
   - Subsequent requests will be faster due to caching

### Network Issues
If you're behind a corporate firewall or have network restrictions:
- The scraper may fail to access The Hindu website
- The app will automatically fall back to the original API
- Check your network settings and proxy configuration

## Customization

### Adding More News Sources
To add more news sources, create new scraper classes similar to `TheHinduScraper` and integrate them into the API server.

### Modifying Categories
Edit the `_categorize_article` method in `thehindu_scraper.py` to add or modify article categories.

### Changing Cache Duration
Modify the `cache_duration` variable in `api_server.py` (default: 300 seconds = 5 minutes).

## Legal Notice

This scraper is for educational purposes only. Please respect The Hindu's terms of service and robots.txt file. Consider implementing proper rate limiting and user-agent headers for production use. 