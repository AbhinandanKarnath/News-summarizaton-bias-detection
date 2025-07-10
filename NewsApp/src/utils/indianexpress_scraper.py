import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time
from bias_detector import detect_bias

class IndianExpressScraper:
    def __init__(self):
        self.base_url = "https://indianexpress.com/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_latest_news(self, limit=20):
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []

            # Indian Express homepage: headlines in .title, .other-articles, .nation, .world, etc.
            selectors = [
                '.nation .title a',
                '.world .title a',
                '.city .title a',
                '.lead-story a',
                '.featured a',
                '.other-articles a',
                '.top-news a',
                '.title a',
                'h2.title a',
                'h3.title a',
                'h2 a',
                'h3 a',
            ]
            found = set()
            for selector in selectors:
                for link in soup.select(selector):
                    url = link.get('href')
                    title = link.get_text(strip=True)
                    if not url or not title or url in found or len(title) < 10:
                        continue
                    found.add(url)
                    # Only keep Indian Express articles
                    if not url.startswith('http'):
                        url = self.base_url.rstrip('/') + url
                    if 'indianexpress.com' not in url:
                        continue
                    # Extract article details
                    article_data = self._extract_article_data(url, title)
                    if article_data:
                        articles.append(article_data)
                    if len(articles) >= limit:
                        break
                if len(articles) >= limit:
                    break
            return articles[:limit]
        except Exception as e:
            print(f"Error scraping Indian Express: {e}")
            return []

    def _extract_article_data(self, url, title):
        try:
            # Visit the article page
            time.sleep(0.5)
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            # Description: first paragraph or meta description
            description = ''
            desc_elem = soup.find('meta', attrs={'name': 'description'})
            if desc_elem and desc_elem.get('content'):
                description = desc_elem['content']
            else:
                p = soup.find('p')
                if p:
                    description = p.get_text(strip=True)
            # Author
            author = None
            author_elem = soup.find('span', class_=re.compile(r'author', re.I))
            if author_elem:
                author = author_elem.get_text(strip=True)
            # Date
            publishedAt = None
            date_elem = soup.find('meta', attrs={'property': 'article:published_time'})
            if date_elem and date_elem.get('content'):
                publishedAt = date_elem['content'][:10]
            # Category
            category = None
            cat_elem = soup.find('meta', attrs={'property': 'article:section'})
            if cat_elem and cat_elem.get('content'):
                category = cat_elem['content']
            # Full text
            full_text = self._extract_article_text(soup)
            # Bias detection
            bias_text = full_text if full_text and full_text != 'Full article text not available' else description
            bias_score, bias_types = detect_bias(bias_text)
            return {
                'title': title,
                'description': description or 'No description available',
                'full_text': full_text,
                'url': url,
                'image': '',
                'author': author or 'Indian Express',
                'publishedAt': publishedAt or datetime.now().strftime('%Y-%m-%d'),
                'source': 'Indian Express',
                'category': category or 'General',
                'bias_score': bias_score,
                'bias_types': bias_types
            }
        except Exception as e:
            print(f"Error extracting article data from {url}: {e}")
            return None

    def _extract_article_text(self, soup):
        try:
            # Main article content is often in .full-details, .articles, .story-content, .main-story, etc.
            selectors = [
                '.full-details',
                '.articles',
                '.story-content',
                '.main-story',
                '.article-content',
                '.content',
                '.main-content',
                '[itemprop="articleBody"]',
            ]
            article_text = ''
            for selector in selectors:
                content = soup.select_one(selector)
                if content:
                    paragraphs = content.find_all(['p', 'div'], recursive=True)
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text and len(text) > 20:
                            article_text += text + '\n\n'
                    if article_text:
                        break
            if not article_text:
                # Fallback: all <p> tags
                for p in soup.find_all('p'):
                    text = p.get_text(strip=True)
                    if text and len(text) > 50:
                        article_text += text + '\n\n'
            if article_text:
                article_text = re.sub(r'\n\s*\n', '\n\n', article_text)
                article_text = re.sub(r'\s+', ' ', article_text)
                article_text = article_text.strip()
                if len(article_text) > 2000:
                    article_text = article_text[:2000] + '...'
            return article_text or 'Full article text not available'
        except Exception as e:
            print(f"Error extracting full text: {e}")
            return 'Full article text not available'

if __name__ == "__main__":
    scraper = IndianExpressScraper()
    articles = scraper.scrape_latest_news(3)
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
        print(f"   Bias Score: {article.get('bias_score')}, Types: {article.get('bias_types')}") 