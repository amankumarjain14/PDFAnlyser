import { useState, useEffect } from 'react';
import { uploadPDF, createProgressStream, getResult } from './services/api';
import UploadZone from './components/UploadZone';
import ProgressTracker from './components/ProgressTracker';
import ResultCard from './components/ResultCard';

function App() {
  const [view, setView] = useState('upload'); // 'upload' | 'processing' | 'result'
  const [jobId, setJobId] = useState(null);
  const [filename, setFilename] = useState('');
  const [steps, setSteps] = useState([]);
  const [error, setError] = useState(null);
  const [finalResult, setFinalResult] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileUpload = async (file) => {
    setIsUploading(true);
    setError(null);
    setFilename(file.name);

    try {
      const res = await uploadPDF(file);
      const newJobId = res.data.job_id;
      setJobId(newJobId);
      setIsUploading(false);
      setView('processing');

      // Listen for progress events
      createProgressStream(
        newJobId,
        (data) => {
          setSteps(data.steps);
          if (data.error) setError(data.error);
        },
        (err) => {
          console.error('Progress stream error', err);
          setError('Lost connection to server. Retrying...');
        },
        async (status) => {
          if (status === 'done') {
            const resultRes = await getResult(newJobId);
            setFinalResult(resultRes.data);
            setView('result');
          }
        }
      );
    } catch (err) {
      console.error('Upload error', err);
      setError(err.response?.data?.detail || 'Failed to upload PDF.');
      setIsUploading(false);
    }
  };

  const reset = () => {
    setView('upload');
    setJobId(null);
    setFilename('');
    setSteps([]);
    setError(null);
    setFinalResult(null);
  };

  return (
    <div className="container-wrapper">
      <header className="main-header animate-fade-in">
        <div className="logo">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <rect width="32" height="32" rx="8" fill="url(#grad1)"/>
            <path d="M10 10h12v12H10z" stroke="white" strokeWidth="2"/>
            <path d="M14 14l4 4m0-4l-4 4" stroke="white" strokeWidth="2"/>
            <defs>
              <linearGradient id="grad1" x1="0" y1="0" x2="32" y2="32">
                <stop stopColor="#4f7cff" />
                <stop offset="1" stopColor="#a855f7" />
              </linearGradient>
            </defs>
          </svg>
          <span className="logo-text">PDF <span className="logo-accent">Analyser</span></span>
        </div>
        <div className="header-meta">
          <span className="pill pill-blue">v1.0.0</span>
        </div>
      </header>

      <main className="main-content">
        <div className="content-width">
          {view === 'upload' && (
            <div className="upload-section text-center animate-fade-up">
              <h1>Enhance your <span className="gradient-text">PDF Documents</span> with AI</h1>
              <p className="hero-sub">
                Our expert AI analyst will deeply extract content, perform live web research, 
                and generate a professionally formatted enhancement.
              </p>
              <div className="upload-container">
                <UploadZone onFileSelect={handleFileUpload} uploading={isUploading} />
                {error && <div className="error-alert">{error}</div>}
              </div>
            </div>
          )}

          {view === 'processing' && (
            <div className="processing-section animate-fade-in">
              <h1>Analysing <span className="gradient-text">{filename}</span></h1>
              <p className="hero-sub">Sit tight. We're running a deep analysis and verifying data with web research.</p>
              <div className="tracker-container">
                <ProgressTracker steps={steps} error={error} />
              </div>
            </div>
          )}

          {view === 'result' && finalResult && (
            <div className="result-section">
              <h1 className="animate-fade-in">Your <span className="gradient-text">Enhanced Report</span> is Ready</h1>
              <p className="hero-sub animate-fade-in" style={{ animationDelay: '0.1s' }}>
                We've synthesized the PDF content with fresh insights from the web.
              </p>
              <div className="result-container" style={{ animationDelay: '0.2s' }}>
                <ResultCard result={finalResult} onReset={reset} />
              </div>
            </div>
          )}
        </div>
      </main>

      <footer className="main-footer animate-fade-in">
        <p>&copy; 2026 PDF Analyser &bull; Powered by Google & OpenAI</p>
      </footer>

      <style>{`
        .container-wrapper {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }
        .main-header {
          padding: 32px 40px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .logo { display: flex; align-items: center; gap: 12px; }
        .logo-text { font-size: 1.4rem; font-weight: 800; color: #fff; letter-spacing: -0.02em; }
        .logo-accent { color: var(--accent-1); }
        
        .main-content {
          flex: 1;
          display: flex;
          justify-content: center;
          padding: 40px 20px 80px;
        }
        .content-width { width: 100%; max-width: 720px; }
        
        .text-center { text-align: center; }
        .hero-sub {
          color: var(--text-secondary);
          max-width: 560px;
          margin: 16px auto 40px;
          font-size: 1.1rem;
        }
        
        .upload-container, .tracker-container, .result-container {
          margin-top: 20px;
        }

        .error-alert {
          margin-top: 20px;
          padding: 14px 20px;
          background: rgba(248, 113, 113, 0.1);
          border: 1px solid rgba(248, 113, 113, 0.25);
          color: var(--error);
          border-radius: var(--radius-md);
          font-size: 0.9rem;
          font-weight: 500;
        }

        .main-footer {
          padding: 40px;
          text-align: center;
          font-size: 0.85rem;
          color: var(--text-muted);
          border-top: 1px solid var(--border);
        }
      `}</style>
    </div>
  );
}

export default App;
