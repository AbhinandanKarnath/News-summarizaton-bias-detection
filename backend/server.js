const express = require('express');
const axios = require('axios');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// API Configuration
const NEWS_API_KEY = process.env.NEWS_API_KEY || '0VmFbHG7SMUXUxF8GDEAERa1RQnuRXoSzhxRES0U';
const SUMMARIZATION_API_URL = 'http://localhost:5000';
const BIAS_DETECTION_API_URL = 'http://localhost:8000';

// Helper function to call Python summarization API
async function callSummarizationAPI(text, type = 'extractive', options = {}) {
    try {
        const endpoint = type === 'transformer' ? '/transformer_summary' : '/extractive_summary';
        const response = await axios.post(`${SUMMARIZATION_API_URL}${endpoint}`, {
            text: text,
            ...options
        });
        return response.data.summary;
    } catch (error) {
        console.error('Summarization API error:', error.message);
        throw new Error('Summarization failed');
    }
}

// Helper function to call Python bias detection API
async function callBiasDetectionAPI(text) {
    try {
        const response = await axios.post(`${BIAS_DETECTION_API_URL}/analyze`, {
            text: text,
            analysis_types: ["all"]
        });
        return response.data;
    } catch (error) {
        console.error('Bias detection API error:', error.message);
        throw new Error('Bias detection failed');
    }
}

// Helper function to scrape article content
async function scrapeArticle(url) {
    try {
        const response = await axios.post(`${SUMMARIZATION_API_URL}/scrape_article`, {
            url: url
        });
        return response.data.article_text;
    } catch (error) {
        console.error('Article scraping error:', error.message);
        throw new Error('Article scraping failed');
    }
}

// 1. Fetch Indian News
app.get('/api/news', async (req, res) => {
    try {
        const response = await axios.get(
            `https://api.thenewsapi.com/v1/news/all?api_token=${NEWS_API_KEY}&search=india&language=en`
        );

        const articles = response.data.data || response.data.articles;
        
        if (!Array.isArray(articles)) {
            return res.status(500).json({ error: 'Invalid response format from news API' });
        }

        // Prepare news data
        const newsData = articles.map(article => ({
            title: article.title,
            url: article.url,
            source: article.source,
            published_at: article.published_at
        }));

        // For each article, scrape and summarize, then analyze bias
        const summarizedArticles = await Promise.all(newsData.map(async (article) => {
            try {
                // Scrape article content
                const scrapeRes = await axios.post('http://localhost:5000/scrape_article', { url: article.url });
                const scrapedText = scrapeRes.data.article_text;
                if (!scrapedText) {
                    return { ...article, description: 'Could not extract article content.' };
                }
                // Summarize scraped content
                const summaryRes = await axios.post('http://localhost:5000/extractive_summary', { text: scrapedText, num_sentences: 3 });
                const summary = summaryRes.data.summary || 'No summary available.';
                // Bias analysis
                let biasScore = null;
                let biasTypes = [];
                try {
                    const biasRes = await axios.post('http://localhost:8000/analyze', {
                        text: scrapedText,
                        analysis_types: ["all"]
                    });
                    biasScore = biasRes.data.overall_bias_score;
                    biasTypes = biasRes.data.bias_results?.map(b => b.bias_type) || [];
                } catch (biasErr) {
                    biasScore = 'N/A';
                    biasTypes = ['Bias analysis failed'];
                }
                return { ...article, description: summary, bias_score: biasScore, bias_types: biasTypes };
            } catch (err) {
                return { ...article, description: 'Error processing article.', bias_score: 'N/A', bias_types: ['Error'] };
            }
        }));

        res.json({
            success: true,
            count: summarizedArticles.length,
            articles: summarizedArticles
        });

    } catch (error) {
        console.error('Error fetching, scraping, or summarizing news:', error.message);
        res.status(500).json({ 
            error: 'Failed to fetch, scrape, or summarize news',
            details: error.response?.data || error.message 
        });
    }
});

// 2. Get article with summarization
app.post('/api/article/summarize', async (req, res) => {
    try {
        const { url, summary_type = 'extractive', num_sentences = 3 } = req.body;

        if (!url) {
            return res.status(400).json({ error: 'URL is required' });
        }

        // Scrape article content
        const articleText = await scrapeArticle(url);

        if (!articleText) {
            return res.status(400).json({ error: 'Failed to scrape article content' });
        }

        // Generate summary
        const summary = await callSummarizationAPI(articleText, summary_type, {
            num_sentences: num_sentences
        });

        res.json({
            success: true,
            url: url,
            article_text: articleText,
            summary: summary,
            summary_type: summary_type
        });

    } catch (error) {
        console.error('Error in article summarization:', error.message);
        res.status(500).json({ 
            error: 'Failed to process article',
            details: error.message 
        });
    }
});

// 3. Get article with bias analysis
app.post('/api/article/bias-analysis', async (req, res) => {
    try {
        const { url } = req.body;

        if (!url) {
            return res.status(400).json({ error: 'URL is required' });
        }

        // Scrape article content
        const articleText = await scrapeArticle(url);

        if (!articleText) {
            return res.status(400).json({ error: 'Failed to scrape article content' });
        }

        // Perform bias analysis
        const biasAnalysis = await callBiasDetectionAPI(articleText);

        res.json({
            success: true,
            url: url,
            article_text: articleText,
            bias_analysis: biasAnalysis
        });

    } catch (error) {
        console.error('Error in bias analysis:', error.message);
        res.status(500).json({ 
            error: 'Failed to analyze article bias',
            details: error.message 
        });
    }
});

// 4. Complete article analysis (summary + bias detection)
app.post('/api/article/complete-analysis', async (req, res) => {
    try {
        const { url, summary_type = 'extractive', num_sentences = 3 } = req.body;

        if (!url) {
            return res.status(400).json({ error: 'URL is required' });
        }

        // Scrape article content
        const articleText = await scrapeArticle(url);

        if (!articleText) {
            return res.status(400).json({ error: 'Failed to scrape article content' });
        }

        // Perform both summarization and bias analysis in parallel
        const [summary, biasAnalysis] = await Promise.all([
            callSummarizationAPI(articleText, summary_type, { num_sentences }),
            callBiasDetectionAPI(articleText)
        ]);

        res.json({
            success: true,
            url: url,
            article_text: articleText,
            summary: summary,
            summary_type: summary_type,
            bias_analysis: biasAnalysis
        });

    } catch (error) {
        console.error('Error in complete analysis:', error.message);
        res.status(500).json({ 
            error: 'Failed to perform complete analysis',
            details: error.message 
        });
    }
});

// 5. Batch process multiple articles
app.post('/api/news/batch-analysis', async (req, res) => {
    try {
        const { limit = 5, summary_type = 'extractive' } = req.body;

        // Fetch news
        const newsResponse = await axios.get(
            `https://api.thenewsapi.com/v1/news/all?api_token=${NEWS_API_KEY}&search=india&language=en`
        );

        const articles = newsResponse.data.data || newsResponse.data.articles;
        
        if (!Array.isArray(articles)) {
            return res.status(500).json({ error: 'Invalid response format from news API' });
        }

        // Limit articles
        const limitedArticles = articles.slice(0, limit);
        const results = [];

        // Process each article
        for (const article of limitedArticles) {
            try {
                const articleText = await scrapeArticle(article.url);
                
                if (articleText) {
                    const [summary, biasAnalysis] = await Promise.all([
                        callSummarizationAPI(articleText, summary_type),
                        callBiasDetectionAPI(articleText)
                    ]);

                    results.push({
                        title: article.title,
                        source: article.source,
                        url: article.url,
                        summary: summary,
                        bias_analysis: biasAnalysis
                    });
                }
            } catch (error) {
                console.error(`Error processing article ${article.url}:`, error.message);
                results.push({
                    title: article.title,
                    source: article.source,
                    url: article.url,
                    error: 'Failed to process article'
                });
            }
        }

        res.json({
            success: true,
            processed_count: results.length,
            results: results
        });

    } catch (error) {
        console.error('Error in batch analysis:', error.message);
        res.status(500).json({ 
            error: 'Failed to perform batch analysis',
            details: error.message 
        });
    }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        services: {
            news_api: 'configured',
            summarization_api: SUMMARIZATION_API_URL,
            bias_detection_api: BIAS_DETECTION_API_URL
        }
    });
});

// Root endpoint
app.get('/', (req, res) => {
    res.json({
        message: 'Integrated News Analysis API',
        version: '1.0.0',
        endpoints: {
            'GET /api/news': 'Fetch Indian news articles',
            'POST /api/article/summarize': 'Summarize article from URL',
            'POST /api/article/bias-analysis': 'Analyze article for bias',
            'POST /api/article/complete-analysis': 'Complete analysis (summary + bias)',
            'POST /api/news/batch-analysis': 'Batch process multiple articles',
            'GET /api/health': 'Health check'
        }
    });
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('Unhandled error:', error);
    res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Integrated Backend Server running on port ${PORT}`);
    console.log(`📰 News API: Configured`);
    console.log(`📝 Summarization API: ${SUMMARIZATION_API_URL}`);
    console.log(`🎯 Bias Detection API: ${BIAS_DETECTION_API_URL}`);
    console.log(`🌐 Health check: http://localhost:${PORT}/api/health`);
}); 