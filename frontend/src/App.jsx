import { useState, useEffect } from 'react';

function App() {
  const [view, setView] = useState('home');
  const [url, setUrl] = useState('');
  const [shortUrl, setShortUrl] = useState(null);
  const [error, setError] = useState('');
  
  const [stats, setStats] = useState({ total_clicks: 0, unique_links_clicked: 0 });
  const [logs, setLogs] = useState([]);

  const shortenUrl = async (e) => {
    e.preventDefault();
    setError('');
    setShortUrl(null);
    try {
      const res = await fetch('/api/shorten', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      setShortUrl(data.short_url);
    } catch (err) {
      setError(err.message);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await fetch('/analytics/system-stats');
      const data = await res.json();
      setStats(data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await fetch('/analytics/logs');
      const data = await res.json();
      setLogs(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (view === 'analytics') fetchStats();
    if (view === 'logs') fetchLogs();
  }, [view]);

  return (
    <div className="min-h-screen flex flex-col items-center p-8">
      
      {/* Header */}
      <header className="w-full max-w-4xl flex justify-between items-center py-6 border-b border-gray-800 mb-10">
        <h1 className="text-2xl font-semibold tracking-tight">Nexus <span className="text-blue-500">Links</span></h1>
        <nav className="flex space-x-6 text-sm font-medium text-gray-400">
          <button onClick={() => setView('home')} className={`hover:text-white transition ${view === 'home' && 'text-white'}`}>Shortener</button>
          <button onClick={() => setView('analytics')} className={`hover:text-white transition ${view === 'analytics' && 'text-white'}`}>Analytics</button>
          <button onClick={() => setView('logs')} className={`hover:text-white transition ${view === 'logs' && 'text-white'}`}>System Logs</button>
        </nav>
      </header>

      {/* Main Content Areas */}
      <main className="flex-grow w-full max-w-4xl flex flex-col items-center">
        
        {view === 'home' && (
          <div className="w-full max-w-lg mt-12 space-y-8">
            <div className="text-center space-y-3">
              <h2 className="text-4xl font-bold tracking-tight">Shorten Your Links.</h2>
              <p className="text-gray-400">Transform incredibly long URLs into manageable links instantly.</p>
            </div>
            
            <form onSubmit={shortenUrl} className="flex flex-col space-y-4">
              <input
                type="url"
                required
                placeholder="https://example.com/long-url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="w-full px-5 py-4 bg-gray-900 border border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-gray-500 transition shadow-lg"
              />
              <button type="submit" className="w-full py-4 bg-blue-600 hover:bg-blue-500 rounded-xl text-white font-semibold transition shadow-lg flex justify-center items-center">
                Generate Link
              </button>
            </form>

            {error && <div className="p-4 bg-red-900/30 border border-red-500/50 text-red-400 rounded-xl text-center text-sm">{error}</div>}
            
            {shortUrl && (
              <div className="p-6 bg-gray-900 border border-gray-700 rounded-xl shadow-xl flex flex-col items-center space-y-3 animate-fade-in">
                <p className="text-gray-400 text-sm">Your shortened URL is ready:</p>
                <a href={shortUrl} target="_blank" rel="noreferrer" className="text-xl font-medium text-blue-400 hover:text-blue-300 break-all">{shortUrl}</a>
              </div>
            )}
          </div>
        )}

        {view === 'analytics' && (
          <div className="w-full mt-8 animate-fade-in">
             <h2 className="text-3xl font-bold tracking-tight mb-8">System Analytics</h2>
             <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-900 border border-gray-800 p-8 rounded-2xl flex flex-col justify-center items-center">
                   <span className="text-5xl font-extrabold text-blue-500">{stats.total_clicks}</span>
                   <span className="text-gray-400 mt-2 font-medium tracking-wide text-sm uppercase">Total Clicks Tracked</span>
                </div>
                <div className="bg-gray-900 border border-gray-800 p-8 rounded-2xl flex flex-col justify-center items-center">
                   <span className="text-5xl font-extrabold text-purple-500">{stats.unique_links_clicked}</span>
                   <span className="text-gray-400 mt-2 font-medium tracking-wide text-sm uppercase">Unique Links Visited</span>
                </div>
             </div>
          </div>
        )}

        {view === 'logs' && (
          <div className="w-full mt-8 animate-fade-in">
            <h2 className="text-3xl font-bold tracking-tight mb-8">System Event Trace</h2>
            <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden shadow-xl">
               <table className="w-full text-left border-collapse">
                  <thead>
                     <tr className="bg-gray-800/50 text-gray-400 text-xs uppercase tracking-wider">
                        <th className="px-6 py-4 font-medium">Timestamp</th>
                        <th className="px-6 py-4 font-medium">Source</th>
                        <th className="px-6 py-4 font-medium">Level</th>
                        <th className="px-6 py-4 font-medium">Message</th>
                     </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800">
                     {logs.length === 0 ? (
                       <tr><td colSpan="4" className="px-6 py-8 text-center text-gray-500 italic">No logs generated yet. Shorten or visit a link to populate.</td></tr>
                     ) : (
                       logs.map((log, i) => (
                         <tr key={i} className="hover:bg-gray-800/30 transition text-sm">
                            <td className="px-6 py-4 text-gray-500 whitespace-nowrap">{new Date(log.created_at).toLocaleString()}</td>
                            <td className="px-6 py-4">
                               <span className="px-2 py-1 bg-gray-800 rounded text-xs text-gray-300">{log.source}</span>
                            </td>
                            <td className="px-6 py-4">
                               <span className={`font-semibold ${log.level === 'INFO' ? 'text-green-400' : 'text-yellow-400'}`}>{log.level}</span>
                            </td>
                            <td className="px-6 py-4 text-gray-300">{log.message}</td>
                         </tr>
                       ))
                     )}
                  </tbody>
               </table>
            </div>
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="w-full max-w-4xl mt-auto pt-10 pb-4 border-t border-gray-800 flex justify-between items-center text-sm text-gray-500">
        <p>&copy; {new Date().getFullYear()} Nexus Links.</p>
        <div className="flex space-x-4">
          <a href="https://github.com/HimanM/SAP01---URL-Shortner" target="_blank" rel="noreferrer" className="hover:text-white transition">GitHub</a>
          <a href="https://www.linkedin.com/in/himanm" target="_blank" rel="noreferrer" className="hover:text-white transition">LinkedIn</a>
        </div>
      </footer>
    </div>
  );
}

export default App;
