import React, { useState, useEffect } from 'react'
import './App.css'
import Navbar from './components/navbar';

const App = () => {
  const [news, setNews] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const response = await fetch('http://localhost:3000/api/news');
        const data = await response.json();
        console.log('API Response:', data); 
        
        if (data.success) {
          setNews(data.articles);
        } else {
          setError('Failed to fetch news');
        }
      } catch (err) {
        console.error('Fetch Error:', err); 
        setError('Error fetching news: ' + err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, []);

  console.log('Current news state:', news) 

  if (loading) {
    return (
      <div className="app-container">
        <div className="loading">Loading news...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="app-container">
        <div className="error">{error}</div>
      </div>
    )
  }

  // DotsOverlay component for interactive dots
  const DotsOverlay = () => {
    const dotSize = 6;
    const gap = 44;
    const [windowSize, setWindowSize] = useState({ width: window.innerWidth, height: window.innerHeight });
    React.useEffect(() => {
      const handleResize = () => setWindowSize({ width: window.innerWidth, height: window.innerHeight });
      window.addEventListener('resize', handleResize);
      return () => window.removeEventListener('resize', handleResize);
    }, []);
    const cols = Math.ceil(windowSize.width / gap);
    const rows = Math.ceil(windowSize.height / gap);
    const dots = [];
    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        dots.push({ x: x * gap, y: y * gap, key: `${x}-${y}` });
      }
    }
    return (
      <div className="dots-overlay" style={{ pointerEvents: 'auto' }}>
        {dots.map(dot => (
          <span
            key={dot.key}
            className="dot"
            style={{
              position: 'absolute',
              left: dot.x,
              top: dot.y,
              width: dotSize,
              height: dotSize,
              borderRadius: '50%',
              background: '#ffffff22',
              transition: 'background 0.2s',
              display: 'block',
            }}
            onMouseEnter={e => e.target.style.background = '#ff9800'}
            onMouseLeave={e => e.target.style.background = '#ffffff22'}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="app-bg">
      <DotsOverlay />
      <Navbar />
      <main className="main-content">
        <h1 className="page-title">Latest News</h1>
        <div className="news-grid">
          {news && news.length > 0 ? (
            news.map((item, index) => (
              <div key={index} className="news-card">
                <div className="card-content">
                  <h2>{item.title}</h2>
                  <p>{item.description}</p>
                  {item.bias_score !== undefined && (
                    <div style={{margin: '0.5rem 0 0.5rem 0', color: '#ff9800', fontWeight: 500}}>
                      Bias Score: {item.bias_score}
                    </div>
                  )}
                  {item.bias_types && item.bias_types.length > 0 && (
                    <div style={{marginBottom: '0.5rem', color: '#ffb74d', fontSize: '0.97rem'}}>
                      Bias Types: {item.bias_types.join(', ')}
                    </div>
                  )}
                  <div className="card-footer">
                    <span>{item.source || 'Unknown Source'}</span>
                    <span>{item.published_at ? new Date(item.published_at).toLocaleDateString() : ''}</span>
                  </div>
                  <a href={item.url} target="_blank" rel="noopener noreferrer" className="read-more-btn">Read more</a>
                </div>
              </div>
            ))
          ) : (
            <div className="no-news">No news articles available</div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App