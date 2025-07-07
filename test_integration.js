const axios = require('axios');

// Configuration
const BACKEND_URL = 'http://localhost:3000';
const SUMMARIZATION_URL = 'http://localhost:5000';
const BIAS_DETECTION_URL = 'http://localhost:8000';

// Test article URL (replace with a real news article URL)
const TEST_ARTICLE_URL = 'https://www.bbc.com/news/world-us-canada-67812345';

async function testHealthChecks() {
    console.log('🏥 Testing health checks...');
    
    try {
        // Test backend health
        const backendHealth = await axios.get(`${BACKEND_URL}/api/health`);
        console.log('✅ Backend health check passed');
        
        // Test summarization API health
        const summaryHealth = await axios.get(`${SUMMARIZATION_URL}/health`);
        console.log('✅ Summarization API health check passed');
        
        // Test bias detection API health
        const biasHealth = await axios.get(`${BIAS_DETECTION_URL}/health`);
        console.log('✅ Bias detection API health check passed');
        
        return true;
    } catch (error) {
        console.log('❌ Health check failed:', error.message);
        return false;
    }
}

async function testNewsFetching() {
    console.log('\n📰 Testing news fetching...');
    
    try {
        const response = await axios.get(`${BACKEND_URL}/api/news`);
        
        if (response.data.success && response.data.articles.length > 0) {
            console.log(`✅ News fetching passed - ${response.data.articles.length} articles retrieved`);
            return response.data.articles[0]; // Return first article for further testing
        } else {
            console.log('❌ News fetching failed - no articles returned');
            return null;
        }
    } catch (error) {
        console.log('❌ News fetching failed:', error.message);
        return null;
    }
}

async function testArticleSummarization(articleUrl) {
    console.log('\n📝 Testing article summarization...');
    
    try {
        const response = await axios.post(`${BACKEND_URL}/api/article/summarize`, {
            url: articleUrl,
            summary_type: 'extractive',
            num_sentences: 3
        });
        
        if (response.data.success && response.data.summary) {
            console.log('✅ Article summarization passed');
            console.log(`📄 Summary: ${response.data.summary.substring(0, 100)}...`);
            return true;
        } else {
            console.log('❌ Article summarization failed - no summary generated');
            return false;
        }
    } catch (error) {
        console.log('❌ Article summarization failed:', error.message);
        return false;
    }
}

async function testBiasAnalysis(articleUrl) {
    console.log('\n🎯 Testing bias analysis...');
    
    try {
        const response = await axios.post(`${BACKEND_URL}/api/article/bias-analysis`, {
            url: articleUrl
        });
        
        if (response.data.success && response.data.bias_analysis) {
            console.log('✅ Bias analysis passed');
            console.log(`📊 Overall bias score: ${response.data.bias_analysis.overall_bias_score}`);
            console.log(`🔍 Bias types detected: ${response.data.bias_analysis.bias_results.length}`);
            return true;
        } else {
            console.log('❌ Bias analysis failed - no analysis generated');
            return false;
        }
    } catch (error) {
        console.log('❌ Bias analysis failed:', error.message);
        return false;
    }
}

async function testCompleteAnalysis(articleUrl) {
    console.log('\n🔬 Testing complete analysis...');
    
    try {
        const response = await axios.post(`${BACKEND_URL}/api/article/complete-analysis`, {
            url: articleUrl,
            summary_type: 'extractive',
            num_sentences: 3
        });
        
        if (response.data.success && response.data.summary && response.data.bias_analysis) {
            console.log('✅ Complete analysis passed');
            console.log(`📄 Summary length: ${response.data.summary.split(' ').length} words`);
            console.log(`📊 Bias score: ${response.data.bias_analysis.overall_bias_score}`);
            return true;
        } else {
            console.log('❌ Complete analysis failed');
            return false;
        }
    } catch (error) {
        console.log('❌ Complete analysis failed:', error.message);
        return false;
    }
}

async function runAllTests() {
    console.log('🧪 Starting Integration Tests...');
    console.log('=' * 50);
    
    let allTestsPassed = true;
    
    // Test 1: Health checks
    const healthPassed = await testHealthChecks();
    if (!healthPassed) {
        console.log('❌ Health checks failed. Make sure all services are running.');
        return;
    }
    
    // Test 2: News fetching
    const firstArticle = await testNewsFetching();
    if (!firstArticle) {
        console.log('❌ News fetching failed. Check your API key.');
        return;
    }
    
    // Test 3: Article summarization
    const summaryPassed = await testArticleSummarization(firstArticle.url);
    if (!summaryPassed) allTestsPassed = false;
    
    // Test 4: Bias analysis
    const biasPassed = await testBiasAnalysis(firstArticle.url);
    if (!biasPassed) allTestsPassed = false;
    
    // Test 5: Complete analysis
    const completePassed = await testCompleteAnalysis(firstArticle.url);
    if (!completePassed) allTestsPassed = false;
    
    console.log('\n' + '=' * 50);
    if (allTestsPassed) {
        console.log('🎉 All integration tests passed!');
        console.log('✅ Your integrated backend is working correctly.');
    } else {
        console.log('⚠️  Some tests failed. Check the logs above for details.');
    }
    console.log('=' * 50);
}

// Run tests
runAllTests().catch(console.error); 