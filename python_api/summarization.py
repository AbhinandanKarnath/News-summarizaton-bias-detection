import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
from collections import Counter
import re
from textstat import flesch_reading_ease
import heapq
import sys
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_nltk_data():
    """Download required NLTK data with error handling"""
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        logger.info("NLTK data downloaded successfully")
    except Exception as e:
        logger.error(f"Error downloading NLTK data: {e}")
        sys.exit(1)

# Download NLTK data at startup
download_nltk_data()

class NewsScraperSummarizer:
    def __init__(self):
        try:
            self.stop_words = set(stopwords.words('english'))
            self.stemmer = PorterStemmer()
            logger.info("NewsScraperSummarizer initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing NewsScraperSummarizer: {e}")
            raise
    
    def scrape_article(self, url):
        """Scrape article content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Try to find article content (common selectors)
            article_selectors = [
                'article', '.article-content', '.post-content', 
                '.entry-content', '.content', 'main', '.story-body',
                '.article-body', '.post-body', '.entry-body'
            ]
            
            article_text = ""
            for selector in article_selectors:
                content = soup.select_one(selector)
                if content:
                    article_text = content.get_text()
                    break
            
            if not article_text:
                # Fallback: get all paragraphs
                paragraphs = soup.find_all('p')
                article_text = ' '.join([p.get_text() for p in paragraphs if len(p.get_text().strip()) > 50])
            
            if not article_text:
                article_text = soup.get_text()
            
            # Clean the text
            article_text = re.sub(r'\s+', ' ', article_text).strip()
            
            if not article_text:
                logger.warning(f"No text content found at URL: {url}")
                return None
                
            logger.info(f"Successfully scraped article from {url}")
            return article_text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while scraping article: {e}")
            return None
        except Exception as e:
            logger.error(f"Error scraping article: {e}")
            return None
    
    def preprocess_text(self, text):
        """Clean and preprocess text"""
        try:
            # Remove special characters and digits
            text = re.sub(r'[^a-zA-Z\s]', '', text)
            # Convert to lowercase
            text = text.lower()
            # Tokenize
            words = word_tokenize(text)
            # Remove stopwords and stem
            words = [self.stemmer.stem(word) for word in words if word not in self.stop_words]
            return words
        except Exception as e:
            logger.error(f"Error preprocessing text: {e}")
            return []
    
    def calculate_sentence_scores(self, sentences, word_freq):
        """Calculate scores for sentences based on word frequency"""
        try:
            sentence_scores = {}
            
            for sentence in sentences:
                words = self.preprocess_text(sentence)
                score = 0
                word_count = 0
                
                for word in words:
                    if word in word_freq:
                        score += word_freq[word]
                        word_count += 1
                
                if word_count > 0:
                    sentence_scores[sentence] = score / word_count
            
            return sentence_scores
        except Exception as e:
            logger.error(f"Error calculating sentence scores: {e}")
            return {}
    
    def extractive_summarize(self, text, num_sentences=3):
        """Create extractive summary using frequency-based approach"""
        try:
            if not text:
                logger.warning("No text provided for summarization")
                return "No text to summarize"
            
            # Tokenize into sentences
            sentences = sent_tokenize(text)
            
            if len(sentences) <= num_sentences:
                logger.info("Text is already shorter than requested summary length")
                return text
            
            # Calculate word frequencies
            words = self.preprocess_text(text)
            word_freq = Counter(words)
            
            if not word_freq:
                logger.warning("No valid words found in text")
                return text
            
            # Normalize frequencies
            max_freq = max(word_freq.values())
            for word in word_freq:
                word_freq[word] = word_freq[word] / max_freq
            
            # Calculate sentence scores
            sentence_scores = self.calculate_sentence_scores(sentences, word_freq)
            
            if not sentence_scores:
                logger.warning("Could not calculate sentence scores")
                return text
            
            # Get top sentences
            top_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
            
            # Maintain original order
            summary_sentences = []
            for sentence in sentences:
                if sentence in top_sentences:
                    summary_sentences.append(sentence)
            
            summary = ' '.join(summary_sentences)
            logger.info(f"Generated summary of {len(summary.split())} words")
            return summary
            
        except Exception as e:
            logger.error(f"Error in extractive summarization: {e}")
            return text
    
    def get_article_stats(self, text):
        """Get basic statistics about the article"""
        try:
            if not text:
                logger.warning("No text provided for statistics")
                return {}
            
            sentences = sent_tokenize(text)
            words = word_tokenize(text)
            
            stats = {
                'word_count': len(words),
                'sentence_count': len(sentences),
                'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
                'reading_ease': flesch_reading_ease(text)
            }
            
            logger.info("Successfully calculated article statistics")
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating article statistics: {e}")
            return {}

class TransformerSummarizer:
    def __init__(self):
        try:
            from transformers import pipeline
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            logger.info("TransformerSummarizer initialized successfully")
        except ImportError:
            logger.warning("Transformers library not installed. Install with: pip install transformers torch")
            self.summarizer = None
        except Exception as e:
            logger.error(f"Error initializing TransformerSummarizer: {e}")
            self.summarizer = None
    
    def summarize(self, text, max_length=130, min_length=30):
        """Summarize using BART model"""
        try:
            if not self.summarizer:
                logger.warning("Transformers library not available")
                return "Transformers library not available"
            
            if len(text.split()) < 50:
                logger.info("Text too short for summarization")
                return text
            
            # Split long text into chunks if needed
            max_chunk_length = 1024
            chunks = [text[i:i+max_chunk_length] for i in range(0, len(text), max_chunk_length)]
            
            summaries = []
            for chunk in chunks:
                if len(chunk.split()) > 30:  # Only summarize substantial chunks
                    summary = self.summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
                    summaries.append(summary[0]['summary_text'])
            
            final_summary = ' '.join(summaries)
            logger.info(f"Generated transformer summary of {len(final_summary.split())} words")
            return final_summary
            
        except Exception as e:
            logger.error(f"Error in transformer summarization: {e}")
            return "Error in summarization"

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize summarizers once
basic_summarizer = NewsScraperSummarizer()
transformer_summarizer = TransformerSummarizer()

@app.route('/extractive_summary', methods=['POST'])
def extractive_summary():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data.get('text', '')
        num_sentences = data.get('num_sentences', 3)
        
        summary = basic_summarizer.extractive_summarize(text, num_sentences)
        return jsonify({'summary': summary})
    except Exception as e:
        logger.error(f"Error in extractive_summary endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/transformer_summary', methods=['POST'])
def transformer_summary():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data.get('text', '')
        max_length = data.get('max_length', 130)
        min_length = data.get('min_length', 30)
        
        summary = transformer_summarizer.summarize(text, max_length, min_length)
        return jsonify({'summary': summary})
    except Exception as e:
        logger.error(f"Error in transformer_summary endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/scrape_article', methods=['POST'])
def scrape_article():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data.get('url', '')
        article_text = basic_summarizer.scrape_article(url)
        
        if article_text is None:
            return jsonify({'error': 'Failed to scrape article'}), 400
        
        return jsonify({'article_text': article_text})
    except Exception as e:
        logger.error(f"Error in scrape_article endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/article_stats', methods=['POST'])
def article_stats():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data.get('text', '')
        stats = basic_summarizer.get_article_stats(text)
        return jsonify({'stats': stats})
    except Exception as e:
        logger.error(f"Error in article_stats endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/batch_summarize', methods=['POST'])
def batch_summarize():
    try:
        data = request.get_json()
        articles = data.get('articles', [])
        num_sentences = data.get('num_sentences', 3)
        summarizer = NewsScraperSummarizer()
        summarized_articles = []
        for article in articles:
            description = article.get('description', '')
            summary = summarizer.extractive_summarize(description, num_sentences=num_sentences)
            summarized_article = dict(article)
            summarized_article['summary'] = summary
            summarized_articles.append(summarized_article)
        return jsonify({
            'success': True,
            'summarized_articles': summarized_articles
        })
    except Exception as e:
        logger.error(f"Error in batch_summarize: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'summarization-api',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'News Summarization API',
        'version': '1.0.0',
        'endpoints': {
            'POST /extractive_summary': 'Generate extractive summary',
            'POST /transformer_summary': 'Generate transformer-based summary',
            'POST /scrape_article': 'Scrape article from URL',
            'POST /article_stats': 'Get article statistics',
            'GET /health': 'Health check'
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)