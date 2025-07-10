import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import time

class TheHinduScraper:
    def __init__(self):
        self.base_url = "https://www.thehindu.com/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_latest_news(self, limit=20):
        """Scrape latest news articles from The Hindu homepage"""
        try:
            # Fetch the homepage
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Try multiple approaches to find articles
            approaches = [
                self._scrape_by_headlines,
                self._scrape_by_links,
                self._scrape_by_sections
            ]
            
            for approach in approaches:
                if len(articles) >= limit:
                    break
                try:
                    found_articles = approach(soup, limit - len(articles))
                    for article in found_articles:
                        if article and article.get('title') and len(article['title']) > 10:
                            # Avoid duplicates
                            if not any(existing['title'] == article['title'] for existing in articles):
                                articles.append(article)
                except Exception as e:
                    print(f"Error with approach {approach.__name__}: {e}")
                    continue
            
            return articles[:limit]
            
        except Exception as e:
            print(f"Error scraping The Hindu: {e}")
            return []
    
    def _extract_article_data(self, article):
        """Extract data from a single article element"""
        try:
            # Try to find title
            title = None
            title_selectors = ['h1', 'h2', 'h3', '.title', '.headline', 'a[title]']
            for selector in title_selectors:
                title_elem = article.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if not title and title_elem.get('title'):
                        title = title_elem.get('title')
                    if title:
                        break
            
            # Try to find link
            link = None
            link_elem = article.find('a', href=True)
            if link_elem:
                link = link_elem['href']
                if link.startswith('/'):
                    link = self.base_url.rstrip('/') + link
            
            # Try to find description/summary
            description = None
            desc_selectors = ['.intro', '.summary', '.description', 'p', '.content']
            for selector in desc_selectors:
                desc_elem = article.select_one(selector)
                if desc_elem:
                    desc_text = desc_elem.get_text(strip=True)
                    if desc_text and len(desc_text) > 20:
                        description = desc_text
                        break
            
            # Try to find image
            image = None
            img_elem = article.find('img')
            if img_elem:
                image = img_elem.get('src') or img_elem.get('data-src')
                if image and not image.startswith('http'):
                    image = self.base_url.rstrip('/') + image
            
            # Try to find author
            author = None
            author_selectors = ['.author', '.byline', '.writer', '[rel="author"]']
            for selector in author_selectors:
                author_elem = article.select_one(selector)
                if author_elem:
                    author = author_elem.get_text(strip=True)
                    break
            
            # Try to find date
            date = None
            date_selectors = ['.date', '.time', '.published', 'time']
            for selector in date_selectors:
                date_elem = article.select_one(selector)
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    if date_text:
                        date = date_text
                        break
            
            if title and link:
                # Extract full article text
                full_text = self._extract_article_text(link)
                
                return {
                    'title': title,
                    'description': description or 'No description available',
                    'full_text': full_text,
                    'url': link,
                    'image': image or '',
                    'author': author or 'The Hindu',
                    'publishedAt': date or datetime.now().strftime('%Y-%m-%d'),
                    'source': 'The Hindu',
                    'category': self._categorize_article(title, description)
                }
            
        except Exception as e:
            print(f"Error extracting article data: {e}")
        
        return None
    
    def _scrape_by_headlines(self, soup, limit):
        """Scrape articles by looking for headline elements"""
        articles = []
        
        # Look for headline elements
        headline_selectors = [
            'h1', 'h2', 'h3', 'h4',
            '.headline', '.title', '.story-title',
            '[class*="headline"]', '[class*="title"]'
        ]
        
        for selector in headline_selectors:
            headlines = soup.select(selector)
            for headline in headlines[:limit * 2]:
                try:
                    title = headline.get_text(strip=True)
                    if len(title) < 10 or len(title) > 200:
                        continue
                    
                    # Find the parent article or link
                    parent = headline.find_parent(['article', 'div', 'section'])
                    if not parent:
                        continue
                    
                    # Find link
                    link_elem = parent.find('a', href=True) or headline.find('a', href=True)
                    if not link_elem:
                        continue
                    
                    href = link_elem['href']
                    if href.startswith('#') or href.startswith('javascript:'):
                        continue
                    
                    # Find description
                    description = None
                    desc_elem = parent.find(['p', 'div'], class_=re.compile(r'intro|summary|description|content', re.I))
                    if desc_elem:
                        description = desc_elem.get_text(strip=True)
                    
                    # Extract full article text
                    full_text = self._extract_article_text(href if href.startswith('http') else self.base_url.rstrip('/') + href)
                    
                    articles.append({
                        'title': title,
                        'description': description or 'No description available',
                        'full_text': full_text,
                        'url': href if href.startswith('http') else self.base_url.rstrip('/') + href,
                        'image': '',
                        'author': 'The Hindu',
                        'publishedAt': datetime.now().strftime('%Y-%m-%d'),
                        'source': 'The Hindu',
                        'category': self._categorize_article(title, description)
                    })
                    
                    if len(articles) >= limit:
                        break
                        
                except Exception as e:
                    continue
        
        return articles
    
    def _scrape_by_links(self, soup, limit):
        """Scrape articles by looking for article links"""
        articles = []
        
        # Look for links that might be articles
        links = soup.find_all('a', href=True)
        for link in links[:limit * 5]:  # Check more links
            try:
                href = link['href']
                title = link.get_text(strip=True)
                
                # Filter out navigation and non-article links
                if (len(title) > 15 and len(title) < 200 and
                    not href.startswith('#') and 
                    not href.startswith('javascript:') and
                    not any(skip in href.lower() for skip in ['login', 'subscribe', 'advertisement', 'cookie', 'newsletter', 'epaper'])):
                    
                    # Check if it looks like an article URL
                    if any(keyword in href.lower() for keyword in ['/news/', '/article/', '/story/', '/india/', '/world/']):
                        
                        # Try to find parent article context
                        parent = link.find_parent(['article', 'div', 'section'])
                        description = None
                        if parent:
                            desc_elem = parent.find(['p', 'div'], class_=re.compile(r'intro|summary|description', re.I))
                            if desc_elem:
                                description = desc_elem.get_text(strip=True)
                        
                        # Extract full article text
                        full_text = self._extract_article_text(href if href.startswith('http') else self.base_url.rstrip('/') + href)
                        
                        articles.append({
                            'title': title,
                            'description': description or 'No description available',
                            'full_text': full_text,
                            'url': href if href.startswith('http') else self.base_url.rstrip('/') + href,
                            'image': '',
                            'author': 'The Hindu',
                            'publishedAt': datetime.now().strftime('%Y-%m-%d'),
                            'source': 'The Hindu',
                            'category': self._categorize_article(title, description)
                        })
                        
                        if len(articles) >= limit:
                            break
                            
            except Exception as e:
                continue
        
        return articles
    
    def _scrape_by_sections(self, soup, limit):
        """Scrape articles by looking for section content"""
        articles = []
        
        # Look for section elements
        section_selectors = [
            '.section', '.category', '.news-section',
            '[class*="section"]', '[class*="category"]'
        ]
        
        for selector in section_selectors:
            sections = soup.select(selector)
            for section in sections[:limit * 2]:
                try:
                    # Find headlines in this section
                    headlines = section.find_all(['h1', 'h2', 'h3', 'h4'])
                    for headline in headlines:
                        if len(articles) >= limit:
                            break
                            
                        title = headline.get_text(strip=True)
                        if len(title) < 10 or len(title) > 200:
                            continue
                        
                        # Find link
                        link_elem = headline.find('a', href=True) or section.find('a', href=True)
                        if not link_elem:
                            continue
                        
                        href = link_elem['href']
                        if href.startswith('#') or href.startswith('javascript:'):
                            continue
                        
                        # Find description
                        description = None
                        desc_elem = section.find(['p', 'div'], class_=re.compile(r'intro|summary|description', re.I))
                        if desc_elem:
                            description = desc_elem.get_text(strip=True)
                        
                        # Extract full article text
                        full_text = self._extract_article_text(href if href.startswith('http') else self.base_url.rstrip('/') + href)
                        
                        articles.append({
                            'title': title,
                            'description': description or 'No description available',
                            'full_text': full_text,
                            'url': href if href.startswith('http') else self.base_url.rstrip('/') + href,
                            'image': '',
                            'author': 'The Hindu',
                            'publishedAt': datetime.now().strftime('%Y-%m-%d'),
                            'source': 'The Hindu',
                            'category': self._categorize_article(title, description)
                        })
                        
                except Exception as e:
                    continue
        
        return articles
    
    def _extract_article_text(self, article_url):
        """Extract the full text content of an article"""
        try:
            # Add a small delay to be respectful to the server
            time.sleep(0.5)
            
            response = requests.get(article_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors to find the article content
            content_selectors = [
                '.article',
                '.story-content',
                '.article-content',
                '.content',
                '.story-body',
                '.article-body',
                '[class*="article"]',
                '[class*="content"]',
                '[class*="story"]'
            ]
            
            article_text = ""
            
            # Try to find the main article content
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Find all paragraph elements within the content
                    paragraphs = content_elem.find_all(['p', 'div'], recursive=True)
                    
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text and len(text) > 20:  # Filter out short text
                            article_text += text + "\n\n"
                    
                    if article_text:
                        break
            
            # If no content found with selectors, try alternative approach
            if not article_text:
                # Look for paragraphs that might be article content
                paragraphs = soup.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 50:  # Longer paragraphs are likely article content
                        article_text += text + "\n\n"
            
            # Clean up the text
            if article_text:
                # Remove extra whitespace and normalize
                article_text = re.sub(r'\n\s*\n', '\n\n', article_text)
                article_text = re.sub(r'\s+', ' ', article_text)
                article_text = article_text.strip()
                
                # Limit to reasonable length (first 2000 characters)
                if len(article_text) > 2000:
                    article_text = article_text[:2000] + "..."
            
            return article_text or "Full article text not available"
            
        except Exception as e:
            print(f"Error extracting article text from {article_url}: {e}")
            return "Full article text not available"
    
    def _categorize_article(self, title, description):
        """Categorize article based on title and description"""
        text = (title + ' ' + (description or '')).lower()
        
        categories = {
            'Politics': ['politics', 'government', 'minister', 'election', 'parliament', 'congress', 'bjp'],
            'Technology': ['technology', 'tech', 'digital', 'ai', 'artificial intelligence', 'software', 'app'],
            'Sports': ['sports', 'cricket', 'football', 'tennis', 'match', 'tournament', 'player'],
            'Business': ['business', 'economy', 'market', 'finance', 'trade', 'company', 'corporate'],
            'Science': ['science', 'research', 'study', 'scientific', 'discovery'],
            'Health': ['health', 'medical', 'hospital', 'doctor', 'disease', 'medicine'],
            'Entertainment': ['entertainment', 'movie', 'film', 'actor', 'actress', 'music', 'celebrity'],
            'World': ['world', 'international', 'global', 'foreign', 'diplomatic']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'General'
    
    def scrape_specific_section(self, section_url):
        """Scrape articles from a specific section"""
        try:
            response = requests.get(section_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Find articles in the section
            article_elements = soup.select('article, .story-card, .story')
            
            for article in article_elements[:15]:
                article_data = self._extract_article_data(article)
                if article_data:
                    articles.append(article_data)
            
            return articles
            
        except Exception as e:
            print(f"Error scraping section {section_url}: {e}")
            return []

# Function to be called from JavaScript
def get_latest_news(limit=20):
    """Main function to get latest news from The Hindu"""
    scraper = TheHinduScraper()
    return scraper.scrape_latest_news(limit)

if __name__ == "__main__":
    # Test the scraper
    scraper = TheHinduScraper()
    articles = scraper.scrape_latest_news(3)  # Test with fewer articles for faster testing
    
    print(f"Found {len(articles)} articles:")
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Category: {article['category']}")
        print(f"   URL: {article['url']}")
        print(f"   Description: {article['description'][:100]}...")
        if article.get('full_text'):
            print(f"   Full Text Preview: {article['full_text'][:200]}...")
        else:
            print(f"   Full Text: Not available") 