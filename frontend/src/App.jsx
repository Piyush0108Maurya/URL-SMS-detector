import { useState, useEffect, useRef } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  Zap, 
  Cpu, 
  Activity, 
  UploadCloud, 
  Download, 
  CheckCircle2, 
  AlertTriangle, 
  Lock, 
  ArrowRight,
  ExternalLink,
  History,
  FileText,
  Search
} from 'lucide-react';
import ShaderDithering from './components/ui/shader-dithering';
import './index.css';

function App() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [benchmark, setBenchmark] = useState(null);
  const [metrics, setMetrics] = useState(null);
  
  // History state for last 5 scans
  const [history, setHistory] = useState([]);

  // Batch scan states
  const [batchFile, setBatchFile] = useState(null);
  const [batchResults, setBatchResults] = useState([]);
  const [batchLoading, setBatchLoading] = useState(false);
  const [batchError, setBatchError] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const fileInputRef = useRef(null);

  useEffect(() => {
    // Fetch Snapdragon benchmark from backend
    fetch('http://127.0.0.1:8000/benchmark')
      .then(r => r.json())
      .then(data => setBenchmark(data))
      .catch(e => console.error('Failed to load benchmark data', e));

    // Fetch Model Metrics from backend
    fetch('http://127.0.0.1:8000/metrics')
      .then(r => r.json())
      .then(data => setMetrics(data))
      .catch(e => {
        console.error('Failed to load metrics data', e);
        setMetrics({ accuracy: 0.9808, f1: 0.9807 });
      });
  }, []);

  const handleScan = async (scanText = text) => {
    const textToScan = scanText || text;
    if (!textToScan.trim()) return;
    
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textToScan })
      });
      
      if (!res.ok) throw new Error('Backend server error');
      const data = await res.json();
      setResult(data);

      // Add to history (keep last 5)
      setHistory(prev => [
        {
          id: Date.now(),
          text: textToScan,
          label: data.label,
          confidence: data.confidence,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        },
        ...prev.slice(0, 4)
      ]);
    } catch (err) {
      setError('Backend is unreachable. Ensure the FastAPI server is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleText) => {
    setText(exampleText);
    handleScan(exampleText);
  };

  // Drag and drop handlers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.name.endsWith('.csv')) {
        setBatchFile(file);
      } else {
        setBatchError('Please upload a valid .csv file');
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setBatchFile(e.target.files[0]);
    }
  };

  const handleBatchScan = async () => {
    if (!batchFile) return;
    setBatchLoading(true);
    setBatchError('');
    
    const formData = new FormData();
    formData.append('file', batchFile);

    try {
      const res = await fetch('http://127.0.0.1:8000/predict-batch', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Batch scan failed');
      }

      const data = await res.json();
      setBatchResults(data);
    } catch (err) {
      setBatchError(err.message || 'Error processing batch file');
    } finally {
      setBatchLoading(false);
    }
  };

  const downloadCSV = () => {
    if (batchResults.length === 0) return;
    
    const headers = ['Text', 'Verdict', 'Confidence'];
    const rows = batchResults.map(r => [
      `"${r.text.replace(/"/g, '""')}"`,
      r.label,
      `${(r.confidence * 100).toFixed(2)}%`
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'phishguard_batch_results.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const flaggedCount = batchResults.filter(r => r.label === 'phishing').length;
  const cleanCount = batchResults.length - flaggedCount;

  // Format accuracy & F1 metrics
  const accuracyStr = metrics ? `${(metrics.accuracy * 100).toFixed(1)}%` : '98.1%';
  const f1Str = metrics ? `${(metrics.f1 * 100).toFixed(1)}%` : '98.1%';

  return (
    <>
      <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: -1 }}>
        <ShaderDithering
          width={window.innerWidth > 0 ? window.innerWidth : 1920}
          height={window.innerHeight > 0 ? window.innerHeight : 1080}
          colorBack="#070a12"
          colorFront="#0a2a43"
          speed={0.5}
        />
      </div>
      <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="brand">
          <div className="brand-icon-wrapper">
            <ShieldCheck size={26} />
          </div>
          <div className="brand-text">
            <h1>PhishGuard Edge</h1>
            <p>On-device phishing detection, powered by Snapdragon</p>
          </div>
        </div>

        <nav className="header-nav">
          <a href="#scan-section" className="nav-link active">Scan</a>
          <a href="#batch-section" className="nav-link">Batch</a>
          <a href="#how-it-works-section" className="nav-link">How it works</a>
        </nav>
      </header>

      {/* Hero Stats Row */}
      <div className="hero-stats-grid">
        {/* Card 1: Model Accuracy & F1 */}
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">
              <Activity size={16} className="stat-icon" /> Model Performance
            </span>
          </div>
          <div className="stat-value">{accuracyStr}</div>
          <div className="stat-sub">
            <span>Accuracy &amp; F1: {f1Str}</span>
          </div>
        </div>

        {/* Card 2: Snapdragon Benchmark */}
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">
              <Zap size={16} className="stat-icon" /> Qualcomm AI Hub benchmark
            </span>
            <span className="verified-badge">
              <CheckCircle2 size={12} /> Verified on Qualcomm AI Hub
            </span>
          </div>
          <div className="stat-value">
            {benchmark ? `${benchmark.inference_latency_ms.toFixed(1)} ms` : '2.0 ms'}
          </div>
          <div className="stat-sub">
            <span>Snapdragon X Elite benchmark</span>
          </div>
        </div>

        {/* Card 3: Compute Unit */}
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">
              <Cpu size={16} className="stat-icon" /> Compute Target
            </span>
          </div>
          <div className="stat-value">NPU (246/247 ops)</div>
          <div className="stat-sub">
            <span>Hardware-accelerated on-device NPU execution</span>
          </div>
        </div>
      </div>

      {/* Single Scan Section */}
      <section id="scan-section" className="section-container">
        <div className="section-title-row">
          <h2>
            <Search size={22} style={{ color: 'var(--accent-teal)' }} /> Real-Time Single Scan
          </h2>
        </div>

        {/* Example Chips */}
        <div className="example-chips">
          <span className="chip phish-chip" onClick={() => handleExampleClick('http://secure-login-paypal-update.com/login')}>
            <AlertTriangle size={13} style={{ color: '#ef4444' }} /> Example 1 (Phishing URL)
          </span>
          <span className="chip phish-chip" onClick={() => handleExampleClick('Urgent: Your bank account has been compromised. Click here http://bit.ly/3xyz to verify.')}>
            <AlertTriangle size={13} style={{ color: '#ef4444' }} /> Example 2 (Phishing SMS)
          </span>
          <span className="chip safe-chip" onClick={() => handleExampleClick('https://github.com/Piyush0108Maurya/URL-SMS-detector')}>
            <CheckCircle2 size={13} style={{ color: '#10b981' }} /> Example 3 (Safe URL)
          </span>
          <span className="chip safe-chip" onClick={() => handleExampleClick('Hey, are we still meeting for lunch today at 1 PM?')}>
            <CheckCircle2 size={13} style={{ color: '#10b981' }} /> Example 4 (Safe Message)
          </span>
        </div>

        {/* Text Area Input */}
        <div className="input-group">
          <textarea
            className="scan-textarea"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste a URL or message..."
            rows={4}
          />
        </div>

        <button 
          className="btn-primary"
          onClick={() => handleScan()} 
          disabled={loading || !text.trim()}
        >
          {loading ? (
            <>
              <div className="spinner" /> Scanning...
            </>
          ) : (
            <>
              Analyze Content <ArrowRight size={16} />
            </>
          )}
        </button>

        {error && (
          <div className="error-banner">
            <AlertTriangle size={18} />
            <span>{error}</span>
          </div>
        )}

        {/* Result Card */}
        {result && (
          <div className="result-card-container">
            <div className="result-main-row">
              <div className="gauge-and-verdict">
                {/* Circular Gauge */}
                <div className="circular-gauge">
                  <svg viewBox="0 0 36 36">
                    <circle className="gauge-bg" cx="18" cy="18" r="15.915" />
                    <circle
                      className="gauge-fill"
                      cx="18"
                      cy="18"
                      r="15.915"
                      stroke={result.label === 'phishing' ? '#ef4444' : '#10b981'}
                      strokeDasharray={`${result.confidence * 100}, 100`}
                    />
                  </svg>
                  <div className="gauge-text">
                    {(result.confidence * 100).toFixed(0)}%
                  </div>
                </div>

                <div className="verdict-info">
                  <div className={`verdict-badge ${result.label}`}>
                    {result.label === 'phishing' ? (
                      <>
                        <ShieldAlert size={18} /> Phishing Detected
                      </>
                    ) : (
                      <>
                        <ShieldCheck size={18} /> Safe
                      </>
                    )}
                  </div>
                  <div className="local-timing-text">
                    <Activity size={14} />
                    Local inference: {result.local_inference_ms.toFixed(2)} ms (this machine)
                  </div>
                </div>
              </div>
            </div>

            {/* URL Indicators (rule-based) Panel */}
            <div className="indicators-panel">
              <h4>
                <FileText size={16} style={{ color: 'var(--accent-teal)' }} />
                URL indicators (rule-based)
              </h4>
              {result.url_indicators && result.url_indicators.length > 0 ? (
                <div className="indicators-grid">
                  {result.url_indicators.map((ind, idx) => (
                    <div className="indicator-row" key={idx}>
                      <span className="indicator-name">{ind.name}</span>
                      <span className={`indicator-status-badge ${ind.status}`}>
                        {ind.status === 'pass' ? <CheckCircle2 size={12} /> : <AlertTriangle size={12} />}
                        {ind.detail}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)' }}>
                  No URL pattern identified in text. Content evaluated directly via transformer sequence classification.
                </p>
              )}
            </div>
          </div>
        )}

        {/* Scan History (Last 5 scans) */}
        {history.length > 0 && (
          <div className="history-section">
            <h4>
              <History size={15} style={{ verticalAlign: 'middle', marginRight: '6px' }} />
              Recent Scans (Local Session)
            </h4>
            <div className="history-list">
              {history.map((item) => (
                <div 
                  key={item.id} 
                  className="history-item"
                  onClick={() => {
                    setText(item.text);
                    handleScan(item.text);
                  }}
                >
                  <span className="history-text">{item.text}</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{item.time}</span>
                    <span className={`history-tag ${item.label}`}>
                      {item.label === 'phishing' ? 'PHISHING' : 'SAFE'} ({(item.confidence * 100).toFixed(0)}%)
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* Batch Scan Section */}
      <section id="batch-section" className="section-container">
        <div className="section-title-row">
          <h2>
            <UploadCloud size={22} style={{ color: 'var(--accent-teal)' }} /> Batch Scan (CSV Upload)
          </h2>
        </div>

        {/* Dropzone */}
        <div 
          className={`dropzone ${dragActive ? 'drag-active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input 
            ref={fileInputRef}
            type="file" 
            accept=".csv" 
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
          <UploadCloud size={40} className="dropzone-icon" />
          <p className="dropzone-text">
            {batchFile ? `Selected: ${batchFile.name}` : 'Drag & drop your CSV file here, or click to browse'}
          </p>
          <p className="dropzone-sub">
            Supports CSV with a "text" column (Up to 500 rows).{' '}
            <a 
              href="/sample.csv" 
              download
              onClick={(e) => e.stopPropagation()}
              style={{ color: 'var(--accent-teal)', textDecoration: 'none' }}
            >
              Download sample CSV
            </a>
          </p>
        </div>

        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
          <button 
            className="btn-primary"
            onClick={handleBatchScan}
            disabled={batchLoading || !batchFile}
          >
            {batchLoading ? (
              <>
                <div className="spinner" /> Processing Batch...
              </>
            ) : (
              'Run Batch Scan'
            )}
          </button>
        </div>

        {batchError && (
          <div className="error-banner">
            <AlertTriangle size={18} />
            <span>{batchError}</span>
          </div>
        )}

        {/* Batch Results Table & Summary */}
        {batchResults.length > 0 && (
          <div>
            <div className="batch-summary-bar">
              <div className="summary-counters">
                <span className="counter-badge scanned">{batchResults.length} scanned</span>
                <span className="counter-badge flagged">{flaggedCount} flagged</span>
                <span className="counter-badge clean">{cleanCount} safe</span>
              </div>
              <button className="btn-secondary" onClick={downloadCSV}>
                <Download size={14} /> Download results (CSV)
              </button>
            </div>

            <div className="table-container">
              <table className="results-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Text Content</th>
                    <th>Verdict</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {batchResults.map((r, i) => (
                    <tr key={i}>
                      <td style={{ color: 'var(--text-dim)', width: '40px' }}>{i + 1}</td>
                      <td style={{ color: '#ffffff', maxWidth: '450px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={r.text}>
                        {r.text}
                      </td>
                      <td>
                        <span className={`history-tag ${r.label}`}>
                          {r.label === 'phishing' ? 'PHISHING' : 'SAFE'}
                        </span>
                      </td>
                      <td style={{ fontWeight: '600', color: 'var(--text-muted)' }}>
                        {(r.confidence * 100).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>

      {/* How It Works Section */}
      <section id="how-it-works-section" className="section-container">
        <div className="section-title-row">
          <h2>How it works</h2>
        </div>

        <div className="steps-timeline">
          <div className="timeline-line"></div>
          
          <div className="step-card">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Fine-tune DistilBERT</h3>
              <p>
                Trained on high-risk phishing datasets to perform lightweight, high-accuracy sequence classification for URLs and SMS text.
              </p>
            </div>
          </div>

          <div className="step-card">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>Compile with AI Hub</h3>
              <p>
                Quantized and optimized for target Snapdragon architectures using Qualcomm AI Hub workbench toolchains.
              </p>
            </div>
          </div>

          <div className="step-card">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Run on Snapdragon NPU</h3>
              <p>
                Executes 246 out of 247 operators directly on the hardware NPU for ultra-fast, zero-cloud on-device latency.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-privacy-badge">
          <Lock size={13} />
          <span>Runs locally. No URLs are sent to any cloud service.</span>
        </div>
        <p style={{ marginTop: '0.5rem' }}>
          PhishGuard Edge &copy; {new Date().getFullYear()} &bull; On-Device Phishing Detection
        </p>
      </footer>
    </div>
    </>
  );
}

export default App;
