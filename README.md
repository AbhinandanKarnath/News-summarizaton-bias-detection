# Integrated News Analysis Backend

A comprehensive backend system that combines news fetching, article scraping, summarization, and bias detection capabilities.

## 🏗️ Architecture

The system consists of three main components:

1. **Node.js Backend** (Port 3000) - Main API gateway and news fetching
2. **Python Summarization API** (Port 5000) - Article scraping and text summarization
3. **Python Bias Detection API** (Port 8000) - Advanced bias analysis

## 🚀 Quick Start

### Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- npm or yarn

### Installation

1. **Install Node.js dependencies:**
   ```bash
   cd backend
   npm install
   ```

2. **Install Python dependencies:**
   ```bash
   cd python_api
   pip install -r requirements.txt
   ```

3. **Start all services:**
   
   **Windows:**
   ```bash
   start_services.bat
   ```
   
   **Linux/Mac:**
   ```bash
   python start_services.py
   ```

   **Manual start:**
   ```bash
   # Terminal 1 - Bias Detection API
   cd python_api
   python main.py
   
   # Terminal 2 - Summarization API
   cd python_api
   python summarization.py
   
   # Terminal 3 - Node.js Backend
   cd backend
   npm start
   ```

## 📋 API Endpoints

### Main Backend (Node.js) - Port 3000

#### 1. Fetch News Articles
```http
GET /api/news
```
Returns latest Indian news articles from the News API.

**Response:**
```json
{
  "success": true,
  "count": 10,
  "articles": [
    {
      "title": "Article Title",
      "description": "Article description",
      "source": "News Source",
      "url": "https://example.com/article",
      "published_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### 2. Summarize Article
```http
POST /api/article/summarize
Content-Type: application/json

{
  "url": "https://example.com/article",
  "summary_type": "extractive",
  "num_sentences": 3
}
```

**Response:**
```json
{
  "success": true,
  "url": "https://example.com/article",
  "article_text": "Full article content...",
  "summary": "Summarized content...",
  "summary_type": "extractive"
}
```

#### 3. Analyze Article for Bias
```http
POST /api/article/bias-analysis
Content-Type: application/json

{
  "url": "https://example.com/article"
}
```

**Response:**
```json
{
  "success": true,
  "url": "https://example.com/article",
  "article_text": "Full article content...",
  "bias_analysis": {
    "text_id": "analysis_123",
    "timestamp": "2024-01-01T00:00:00",
    "overall_bias_score": 0.45,
    "bias_results": [
      {
        "bias_type": "gender",
        "confidence": 0.3,
        "evidence": ["Male-coded terms detected: 2"],
        "suggestions": ["Consider using gender-neutral language"],
        "severity": "medium"
      }
    ],
    "word_count": 500,
    "processing_time_ms": 150.5
  }
}
```

#### 4. Complete Article Analysis
```http
POST /api/article/complete-analysis
Content-Type: application/json

{
  "url": "https://example.com/article",
  "summary_type": "extractive",
  "num_sentences": 3
}
```

**Response:**
```json
{
  "success": true,
  "url": "https://example.com/article",
  "article_text": "Full article content...",
  "summary": "Summarized content...",
  "summary_type": "extractive",
  "bias_analysis": {
    "overall_bias_score": 0.45,
    "bias_results": [...]
  }
}
```

#### 5. Batch Process Multiple Articles
```http
POST /api/news/batch-analysis
Content-Type: application/json

{
  "limit": 5,
  "summary_type": "extractive"
}
```

**Response:**
```json
{
  "success": true,
  "processed_count": 5,
  "results": [
    {
      "title": "Article Title",
      "source": "News Source",
      "url": "https://example.com/article",
      "summary": "Summarized content...",
      "bias_analysis": {
        "overall_bias_score": 0.45,
        "bias_results": [...]
      }
    }
  ]
}
```

### Health Check
```http
GET /api/health
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# News API Configuration
NEWS_API_KEY=your_news_api_key_here

# Python API URLs
SUMMARIZATION_API_URL=http://localhost:5000
BIAS_DETECTION_API_URL=http://localhost:8000

# Server Configuration
PORT=3000
NODE_ENV=development
```

### API Keys

1. **News API**: Get a free API key from [The News API](https://thenewsapi.com/)
2. Update the `NEWS_API_KEY` in your `.env` file

## 🧪 Testing the APIs

### Using curl

1. **Fetch news:**
   ```bash
   curl http://localhost:3000/api/news
   ```

2. **Summarize an article:**
   ```bash
   curl -X POST http://localhost:3000/api/article/summarize \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com/article", "summary_type": "extractive"}'
   ```

3. **Analyze bias:**
   ```bash
   curl -X POST http://localhost:3000/api/article/bias-analysis \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com/article"}'
   ```

### Using Postman

Import these sample requests:

1. **GET** `http://localhost:3000/api/news`
2. **POST** `http://localhost:3000/api/article/summarize`
3. **POST** `http://localhost:3000/api/article/bias-analysis`
4. **POST** `http://localhost:3000/api/article/complete-analysis`

## 🔍 Bias Detection Types

The bias detection API analyzes text for:

- **Gender Bias**: Detects gender-coded language
- **Confirmation Bias**: Identifies language that assumes agreement
- **Racial Bias**: Flags potentially problematic racial descriptors
- **Loaded Language**: Detects emotionally charged terms
- **Sentiment Bias**: Analyzes extreme sentiment

## 📊 Summarization Types

- **Extractive**: Frequency-based sentence selection
- **Transformer**: BART model-based summarization (requires transformers library)

## 🛠️ Development

### Project Structure
```
├── backend/                 # Node.js backend
│   ├── server.js           # Main server file
│   ├── package.json        # Node.js dependencies
│   └── config.env          # Environment variables
├── python_api/             # Python APIs
│   ├── main.py             # Bias detection API (FastAPI)
│   ├── summarization.py    # Summarization API (Flask)
│   └── requirements.txt    # Python dependencies
├── start_services.bat      # Windows startup script
├── start_services.py       # Python startup script
└── README.md              # This file
```

### Adding New Features

1. **New API endpoints**: Add to `backend/server.js`
2. **New bias detection**: Extend `python_api/main.py`
3. **New summarization**: Extend `python_api/summarization.py`

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Windows
   netstat -ano | findstr :3000
   taskkill /PID <PID> /F
   
   # Linux/Mac
   lsof -ti:3000 | xargs kill -9
   ```

2. **Python dependencies not found:**
   ```bash
   pip install -r python_api/requirements.txt
   ```

3. **Node.js dependencies not found:**
   ```bash
   cd backend
   npm install
   ```

4. **News API errors:**
   - Check your API key in `.env`
   - Verify API key is valid at [The News API](https://thenewsapi.com/)

### Logs

- **Node.js Backend**: Check terminal output
- **Python APIs**: Check terminal output for each service
- **Health Check**: `http://localhost:3000/api/health`

## 📝 License

This project is for educational purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Happy coding! 🚀** 