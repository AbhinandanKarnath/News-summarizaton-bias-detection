import React, { useState, useEffect, useRef } from 'react';
import LoginForm from './LoginForm';
import SignupForm from './SignupForm';
import './AppPlain.css';

const getBiasColor = (score) => {
  if (score === undefined || score === null) return '#bbb';
  if (score <= 0.1) return '#22c55e'; // green
  if (score <= 0.3) return '#eab308'; // yellow
  return '#ef4444'; // red
};

function App() {
  const [auth, setAuth] = React.useState(() => {
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');
    return token ? { token, username } : null;
  });
  const [showSignup, setShowSignup] = React.useState(false);
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [modalArticle, setModalArticle] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const synthRef = useRef(window.speechSynthesis);
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState(null);

  useEffect(() => {
    const fetchNews = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch('http://localhost:5000/api/news');
        const data = await response.json();
        if (data.articles && data.articles.length > 0) {
          setNews(data.articles);
        } else {
          setError('No news articles found.');
        }
      } catch (err) {
        setError('Failed to fetch news: ' + err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchNews();
  }, []);

  // Stop speech when modal closes or article changes
  useEffect(() => {
    if (!modalArticle) {
      synthRef.current.cancel();
      setIsSpeaking(false);
    }
  }, [modalArticle]);

  const handleListen = () => {
    if (!modalArticle) return;
    synthRef.current.cancel();
    const text = `${modalArticle.title}. ${modalArticle.author ? 'By ' + modalArticle.author + '. ' : ''}${modalArticle.full_text || modalArticle.description || ''}`;
    const utterance = new window.SpeechSynthesisUtterance(text);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    synthRef.current.speak(utterance);
    setIsSpeaking(true);
  };

  const handleStop = () => {
    synthRef.current.cancel();
    setIsSpeaking(false);
  };

  const handleLogin = (data) => {
    localStorage.setItem('token', data.token);
    localStorage.setItem('username', data.username);
    setAuth({ token: data.token, username: data.username });
  };
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setAuth(null);
  };
  const handleSignup = () => {
    setShowSignup(false);
  };

  // Save to history when opening article modal
  const handleOpenModal = (article) => {
    setModalArticle(article);
    // Save to history (only if logged in)
    if (auth && auth.token) {
      fetch('http://localhost:5001/api/history', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${auth.token}`
        },
        body: JSON.stringify({
          title: article.title,
          url: article.url,
          source: article.source || article.source_name || '',
          publishedAt: article.publishedAt || '',
        })
      });
    }
  };

  // Fetch history
  const fetchHistory = async () => {
    setHistoryLoading(true);
    setHistoryError(null);
    try {
      const res = await fetch('http://localhost:5001/api/history', {
        headers: { 'Authorization': `Bearer ${auth.token}` }
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to fetch history');
      setHistory(data.history || []);
    } catch (err) {
      setHistoryError(err.message);
    } finally {
      setHistoryLoading(false);
    }
  };

  if (!auth) {
    return showSignup ? (
      <SignupForm onSignup={handleSignup} switchToLogin={() => setShowSignup(false)} />
    ) : (
      <LoginForm onLogin={handleLogin} switchToSignup={() => setShowSignup(true)} />
    );
  }

  return (
    <div>
      {/* Navbar */}
      <nav className="navbar">
        <span className="navbar-title">📰 News Portal</span>
        <button className="navbar-btn" onClick={() => setShowSettings(true)}>
          Settings
        </button>
        <button className="navbar-btn" onClick={() => { setShowHistory(true); fetchHistory(); }}>
          History
        </button>
        <button className="navbar-btn" onClick={handleLogout}>
          Logout
        </button>
      </nav>

      <main className="main-content">
        <h1 className="page-title">Latest News</h1>
        {loading ? (
          <div>Loading news...</div>
        ) : error ? (
          <div style={{ color: 'red', textAlign: 'center' }}>{error}</div>
        ) : (
          <div className="news-grid">
            {news.map((item, idx) => (
              <div className="card" key={idx}>
                {item.image && <img src={item.image} alt={item.title} className="card-image" />}
                <div className="card-body">
                  <div className="card-title">{item.title}</div>
                  <div className="card-desc">{item.description}</div>
                  {/* Bias Score and Types */}
                  {(item.bias_score !== undefined || (item.bias_types && item.bias_types.length > 0)) && (
                    <div style={{ margin: '0.7rem 0 0.5rem 0', display: 'flex', alignItems: 'center', gap: '0.7rem', flexWrap: 'wrap' }}>
                      {item.bias_score !== undefined && (
                        <span style={{
                          background: getBiasColor(item.bias_score),
                          color: '#fff',
                          borderRadius: '12px',
                          padding: '0.2rem 0.8rem',
                          fontWeight: 600,
                          fontSize: '0.97rem',
                          letterSpacing: '0.5px',
                        }}>
                          Bias Score: {(item.bias_score * 100).toFixed(0)}%
                        </span>
                      )}
                      {item.bias_types && item.bias_types.length > 0 && (
                        <span style={{
                          background: '#fbbf24',
                          color: '#222',
                          borderRadius: '12px',
                          padding: '0.2rem 0.8rem',
                          fontWeight: 500,
                          fontSize: '0.97rem',
                          letterSpacing: '0.5px',
                        }}>
                          Bias Types: {item.bias_types.join(', ')}
                        </span>
                      )}
                    </div>
                  )}
                  <div className="card-footer">
                    <span>{item.author}</span>
                    <span>{item.publishedAt ? new Date(item.publishedAt).toLocaleDateString() : ''}</span>
                  </div>
                  <button className="card-btn" onClick={() => handleOpenModal(item)}>
                    Read More
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Article Modal */}
      {modalArticle && (
        <div className="modal-overlay" onClick={e => { if (e.target.classList.contains('modal-overlay')) setModalArticle(null); }}>
          <div className="modal-box" style={{ maxWidth: 600 }}>
            <button className="modal-close" onClick={() => setModalArticle(null)}>&times;</button>
            {modalArticle.image && <img src={modalArticle.image} alt={modalArticle.title} className="card-image" style={{ marginBottom: 16 }} />}
            <h2 style={{ fontWeight: 700, fontSize: '1.3rem', marginBottom: '0.7rem' }}>{modalArticle.title}</h2>
            <div style={{ color: '#374151', marginBottom: 12 }}>{modalArticle.author} | {modalArticle.publishedAt ? new Date(modalArticle.publishedAt).toLocaleDateString() : ''}</div>
            {(modalArticle.bias_score !== undefined || (modalArticle.bias_types && modalArticle.bias_types.length > 0)) && (
              <div style={{ margin: '0.7rem 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.7rem', flexWrap: 'wrap' }}>
                {modalArticle.bias_score !== undefined && (
                  <span style={{
                    background: getBiasColor(modalArticle.bias_score),
                    color: '#fff',
                    borderRadius: '12px',
                    padding: '0.2rem 0.8rem',
                    fontWeight: 600,
                    fontSize: '0.97rem',
                    letterSpacing: '0.5px',
                  }}>
                    Bias Score: {(modalArticle.bias_score * 100).toFixed(0)}%
                  </span>
                )}
                {modalArticle.bias_types && modalArticle.bias_types.length > 0 && (
                  <span style={{
                    background: '#fbbf24',
                    color: '#222',
                    borderRadius: '12px',
                    padding: '0.2rem 0.8rem',
                    fontWeight: 500,
                    fontSize: '0.97rem',
                    letterSpacing: '0.5px',
                  }}>
                    Bias Types: {modalArticle.bias_types.join(', ')}
                  </span>
                )}
              </div>
            )}
            <div style={{ color: '#222', fontSize: '1.08rem', lineHeight: 1.7, marginTop: 8, marginBottom: 16 }}>
              {modalArticle.full_text || 'No full article text available.'}
            </div>
            <div style={{ display: 'flex', gap: '1rem', marginTop: 8 }}>
              <button className="card-btn" onClick={handleListen} disabled={isSpeaking}>
                {isSpeaking ? 'Speaking...' : 'Listen'}
              </button>
              <button className="card-btn" onClick={handleStop} disabled={!isSpeaking}>
                Stop
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Settings Modal */}
      {showSettings && (
        <div className="modal-overlay" onClick={e => { if (e.target.classList.contains('modal-overlay')) setShowSettings(false); }}>
          <div className="modal-box">
            <button className="modal-close" onClick={() => setShowSettings(false)}>&times;</button>
            <h2 style={{ fontWeight: 700, fontSize: '1.3rem', marginBottom: '1.2rem' }}>Settings</h2>
            <div style={{ color: '#374151' }}>Settings content goes here.</div>
          </div>
        </div>
      )}

      {/* History Modal */}
      {showHistory && (
        <div className="modal-overlay" onClick={() => setShowHistory(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()} style={{maxWidth: 500, minHeight: 200}}>
            <h2 style={{marginBottom: '1rem'}}>Reading History</h2>
            {historyLoading ? <div>Loading...</div> : historyError ? <div style={{color: 'red'}}>{historyError}</div> : (
              <ul style={{maxHeight: 300, overflowY: 'auto', padding: 0, listStyle: 'none'}}>
                {history.length === 0 ? <li>No articles read yet.</li> : history.map((item, i) => (
                  <li key={i} style={{marginBottom: '1rem', borderBottom: '1px solid #eee', paddingBottom: 8}}>
                    <div style={{fontWeight: 600}}>{item.title}</div>
                    <div style={{fontSize: '0.95em', color: '#555'}}>{item.source} {item.publishedAt ? `| ${item.publishedAt.slice(0,10)}` : ''}</div>
                    <a href={item.url} target="_blank" rel="noopener noreferrer" style={{color: '#2563eb', fontSize: '0.97em'}}>Read again</a>
                  </li>
                ))}
              </ul>
            )}
            <button className="modal-close" onClick={() => setShowHistory(false)} style={{marginTop: 16}}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;