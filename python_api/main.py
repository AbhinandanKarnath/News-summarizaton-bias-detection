import asyncio
import re
import string
from typing import Dict, List, Optional, Union
from datetime import datetime
import json
from dataclasses import dataclass, asdict
from functools import lru_cache
import threading
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download required NLTK data
def download_nltk_resources():
    """Download all required NLTK resources"""
    resources = [
        ('tokenizers/punkt', 'punkt'),
        ('tokenizers/punkt_tab', 'punkt_tab'),
        ('corpora/stopwords', 'stopwords')
    ]
    
    for resource_path, resource_name in resources:
        try:
            nltk.data.find(resource_path)
        except LookupError:
            print(f"Downloading NLTK resource: {resource_name}")
            nltk.download(resource_name, quiet=True)

# Initialize NLTK resources
download_nltk_resources()

app = FastAPI(
    title="Bias Detection API",
    description="Advanced bias detection service for text analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread pool for CPU-intensive tasks
executor = ThreadPoolExecutor(max_workers=4)

@dataclass
class BiasResult:
    bias_type: str
    confidence: float
    evidence: List[str]
    suggestions: List[str]
    severity: str  # low, medium, high

class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    analysis_types: Optional[List[str]] = Field(default=["all"])
    language: Optional[str] = Field(default="en")

class BiasAnalysisResponse(BaseModel):
    text_id: str
    timestamp: str
    overall_bias_score: float
    bias_results: List[Dict]
    word_count: int
    processing_time_ms: float

class BiasDetector:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Bias lexicons
        self.gender_bias_terms = {
            'male_coded': ['aggressive', 'ambitious', 'analytical', 'assertive', 'athletic',
                          'competitive', 'confident', 'decisive', 'determined', 'independent',
                          'leader', 'logical', 'objective', 'outspoken', 'persistent'],
            'female_coded': ['collaborative', 'committed', 'compassionate', 'considerate',
                           'cooperative', 'dependable', 'enthusiastic', 'interpersonal',
                           'loyal', 'pleasant', 'polite', 'responsible', 'sensitive',
                           'supportive', 'sympathetic', 'trustworthy', 'understanding']
        }
        
        self.racial_bias_indicators = [
            'urban', 'articulate', 'clean', 'well-spoken', 'exotic', 'ethnic',
            'diverse', 'minority', 'disadvantaged', 'inner-city'
        ]
        
        self.age_bias_terms = [
            'young', 'old', 'senior', 'junior', 'experienced', 'fresh',
            'mature', 'veteran', 'seasoned', 'energetic', 'digital native'
        ]
        
        self.confirmation_bias_phrases = [
            'obviously', 'clearly', 'everyone knows', 'it\'s common sense',
            'without a doubt', 'undeniably', 'certainly', 'definitely'
        ]
        
        self.loaded_language = [
            'terrorist', 'extremist', 'radical', 'fanatic', 'militant',
            'thug', 'criminal', 'suspect', 'alleged', 'controversial'
        ]

    @lru_cache(maxsize=128)
    def preprocess_text(self, text: str) -> tuple:
        """Preprocess text with caching for efficiency"""
        # Clean text
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        text_clean = ' '.join(text_clean.split())
        
        # Tokenize
        words = word_tokenize(text_clean)
        sentences = sent_tokenize(text)
        
        # Remove stop words
        filtered_words = [w for w in words if w not in self.stop_words]
        
        return tuple(filtered_words), tuple(sentences), text_clean

    def detect_gender_bias(self, text: str) -> BiasResult:
        """Detect gender-coded language bias"""
        filtered_words, _, _ = self.preprocess_text(text)
        
        male_score = sum(1 for word in filtered_words if word in self.gender_bias_terms['male_coded'])
        female_score = sum(1 for word in filtered_words if word in self.gender_bias_terms['female_coded'])
        
        total_coded = male_score + female_score
        if total_coded == 0:
            return BiasResult("gender", 0.0, [], [], "low")
        
        bias_ratio = abs(male_score - female_score) / total_coded
        confidence = min(bias_ratio * 2, 1.0)  # Scale to 0-1
        
        evidence = []
        if male_score > female_score:
            evidence.append(f"Male-coded terms detected: {male_score}")
            bias_direction = "male-coded"
        else:
            evidence.append(f"Female-coded terms detected: {female_score}")
            bias_direction = "female-coded"
        
        severity = "high" if confidence > 0.7 else "medium" if confidence > 0.4 else "low"
        
        suggestions = [
            "Consider using gender-neutral language",
            f"Replace {bias_direction} terms with neutral alternatives",
            "Review job descriptions for inclusive language"
        ]
        
        return BiasResult("gender", confidence, evidence, suggestions, severity)

    def detect_confirmation_bias(self, text: str) -> BiasResult:
        """Detect confirmation bias indicators"""
        _, sentences, text_clean = self.preprocess_text(text.lower())
        
        bias_phrases_found = []
        for phrase in self.confirmation_bias_phrases:
            if phrase in text_clean:
                bias_phrases_found.append(phrase)
        
        confidence = min(len(bias_phrases_found) * 0.3, 1.0)
        
        evidence = [f"Confirmation bias phrase: '{phrase}'" for phrase in bias_phrases_found]
        
        severity = "high" if confidence > 0.6 else "medium" if confidence > 0.3 else "low"
        
        suggestions = [
            "Use more tentative language (e.g., 'may', 'could', 'appears')",
            "Provide evidence for strong claims",
            "Consider alternative viewpoints"
        ]
        
        return BiasResult("confirmation", confidence, evidence, suggestions, severity)

    def detect_racial_bias(self, text: str) -> BiasResult:
        """Detect potential racial bias indicators"""
        filtered_words, _, _ = self.preprocess_text(text)
        
        bias_indicators_found = [word for word in filtered_words if word in self.racial_bias_indicators]
        
        confidence = min(len(bias_indicators_found) * 0.4, 1.0)
        
        evidence = [f"Potentially biased term: '{word}'" for word in bias_indicators_found]
        
        severity = "high" if confidence > 0.6 else "medium" if confidence > 0.3 else "low"
        
        suggestions = [
            "Review context of racial/ethnic descriptors",
            "Consider if descriptors are necessary",
            "Use person-first language"
        ]
        
        return BiasResult("racial", confidence, evidence, suggestions, severity)

    def detect_loaded_language(self, text: str) -> BiasResult:
        """Detect emotionally loaded language"""
        filtered_words, _, _ = self.preprocess_text(text)
        
        loaded_words_found = [word for word in filtered_words if word in self.loaded_language]
        
        confidence = min(len(loaded_words_found) * 0.5, 1.0)
        
        evidence = [f"Loaded term: '{word}'" for word in loaded_words_found]
        
        severity = "high" if confidence > 0.7 else "medium" if confidence > 0.4 else "low"
        
        suggestions = [
            "Use neutral, factual language",
            "Replace loaded terms with objective descriptions",
            "Consider the emotional impact of word choices"
        ]
        
        return BiasResult("loaded_language", confidence, evidence, suggestions, severity)

    def detect_sentiment_bias(self, text: str) -> BiasResult:
        """Detect extreme sentiment that might indicate bias"""
        blob = TextBlob(text)
        polarity = abs(blob.sentiment.polarity)
        subjectivity = blob.sentiment.subjectivity
        
        # High subjectivity + extreme polarity suggests potential bias
        confidence = (polarity * subjectivity)
        
        evidence = [
            f"Sentiment polarity: {blob.sentiment.polarity:.2f}",
            f"Subjectivity: {subjectivity:.2f}"
        ]
        
        severity = "high" if confidence > 0.7 else "medium" if confidence > 0.4 else "low"
        
        suggestions = [
            "Consider more balanced language",
            "Include multiple perspectives",
            "Use objective, factual statements"
        ]
        
        return BiasResult("sentiment", confidence, evidence, suggestions, severity)

    async def analyze_text(self, text: str, analysis_types: List[str]) -> List[BiasResult]:
        """Main analysis function with async processing"""
        if "all" in analysis_types:
            analysis_types = ["gender", "confirmation", "racial", "loaded_language", "sentiment"]
        
        # Run bias detection methods in parallel
        loop = asyncio.get_event_loop()
        tasks = []
        
        if "gender" in analysis_types:
            tasks.append(loop.run_in_executor(executor, self.detect_gender_bias, text))
        if "confirmation" in analysis_types:
            tasks.append(loop.run_in_executor(executor, self.detect_confirmation_bias, text))
        if "racial" in analysis_types:
            tasks.append(loop.run_in_executor(executor, self.detect_racial_bias, text))
        if "loaded_language" in analysis_types:
            tasks.append(loop.run_in_executor(executor, self.detect_loaded_language, text))
        if "sentiment" in analysis_types:
            tasks.append(loop.run_in_executor(executor, self.detect_sentiment_bias, text))
        
        results = await asyncio.gather(*tasks)
        return results

# Initialize detector
detector = BiasDetector()

@app.post("/analyze", response_model=BiasAnalysisResponse)
async def analyze_bias(request: TextAnalysisRequest):
    """Analyze text for various types of bias"""
    start_time = datetime.now()
    
    try:
        # Generate unique ID for this analysis
        text_id = f"analysis_{hash(request.text)}_{int(start_time.timestamp())}"
        
        # Perform bias analysis
        bias_results = await detector.analyze_text(request.text, request.analysis_types)
        
        # Calculate overall bias score
        overall_score = sum(result.confidence for result in bias_results) / len(bias_results) if bias_results else 0.0
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return BiasAnalysisResponse(
            text_id=text_id,
            timestamp=start_time.isoformat(),
            overall_bias_score=round(overall_score, 3),
            bias_results=[asdict(result) for result in bias_results],
            word_count=len(request.text.split()),
            processing_time_ms=round(processing_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/bias-types")
async def get_bias_types():
    """Get available bias detection types"""
    return {
        "available_types": [
            "gender",
            "confirmation", 
            "racial",
            "loaded_language",
            "sentiment",
            "all"
        ],
        "descriptions": {
            "gender": "Detects gender-coded language that may bias against certain genders",
            "confirmation": "Identifies language that assumes agreement or presents opinion as fact",
            "racial": "Flags potentially problematic racial/ethnic descriptors",
            "loaded_language": "Detects emotionally charged or prejudicial terms",
            "sentiment": "Analyzes extreme sentiment that might indicate bias",
            "all": "Runs all available bias detection types"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Bias Detection API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "POST /analyze - Analyze text for bias",
            "bias_types": "GET /bias-types - Get available bias detection types",
            "health": "GET /health - Health check",
            "docs": "GET /docs - API documentation"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Set to False for production
        workers=1,     # Increase for production
        loop="asyncio"
    )