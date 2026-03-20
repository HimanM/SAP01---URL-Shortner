import React, { useState, useEffect } from 'react';
import './index.css';

function App() {
  const [url, setUrl] = useState('');
  const [shortUrl, setShortUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [stats, setStats] = useState(null);
  const [topLinks, setTopLinks] = useState([]);
  
  const fetchDashboardData = async () => {
    try {
      const urlsRes = await fetch('/analytics/system-stats');
      if (urlsRes.ok) {
        const data = await urlsRes.json();
        setStats(data);
      }
      
      const topRes = await fetch('/analytics/top-links');
      if (topRes.ok) {
        const topData = await topRes.json();
        setTopLinks(topData);
      }
    } catch (err) {
      console.error('Failed to fetch dashboard', err);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleShorten = async (e) => {
    e.preventDefault();
    if (!url) return;
    
    setLoading(true);
    setError('');
    setShortUrl('');
    
    try {
      const res = await fetch('/api/shorten', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to shorten');
      
      setShortUrl(data.short_url);
      fetchDashboardData(); // instant refresh
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>Nexus URL</h1>
        <p className="subtitle">Lightning fast, highly scalable link shortening service</p>
      </header>

      <div className="dashboard-grid">
        {/* Shortener Card */}
        <div className="glass-card">
          <h2>Shorten Link</h2>
          <p className="subtitle" style={{marginBottom: '1.5rem', marginTop: '0.5rem'}}>
            Paste your long URL below to magic it away.
          </p>
          <form className="form-group" onSubmit={handleShorten}>
            <input 
              type="url" 
              placeholder="https://very-long-url.com/something..." 
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
            />
            <button type="submit" disabled={loading} className={loading ? 'loading' : ''}>
              {loading ? 'Processing...' : 'Shorten Now'}
            </button>
          </form>
          
          {error && <p style={{color: '#ef4444', marginTop: '1rem', textAlign: 'center'}}>{error}</p>}
          
          {shortUrl && (
            <div className="result-box">
              <p style={{marginBottom: '0.5rem', color: '#a7f3d0'}}>Your shortened link is ready!</p>
              <a href={shortUrl} target="_blank" rel="noreferrer">{shortUrl}</a>
            </div>
          )}
        </div>

        {/* Analytics Card */}
        <div className="glass-card">
          <h2>Analytics Dashboard</h2>
          <p className="subtitle" style={{marginBottom: '1rem', marginTop: '0.5rem'}}>
            Real-time insights powered by Kafka
          </p>
          
          <div style={{marginBottom: '2rem'}}>
            <div className="stat-item">
              <span className="stat-label">Total System Clicks</span>
              <span className="stat-value">{stats ? stats.total_clicks : '...'}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Unique Links Clicked</span>
              <span className="stat-value">{stats ? stats.unique_links_clicked : '...'}</span>
            </div>
          </div>

          <h3>Top Performing Links</h3>
          {topLinks.length > 0 ? (
            <ul className="link-list" style={{marginTop: '1rem'}}>
              {topLinks.map((link) => (
                <li key={link.short_code}>
                  <span>/{link.short_code}</span>
                  <span className="link-clicks">{link.clicks} clicks</span>
                </li>
              ))}
            </ul>
          ) : (
            <p style={{color: 'var(--text-muted)', marginTop: '1rem', fontStyle: 'italic'}}>No click data yet. Shorten a link and visit it to see stats here.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
