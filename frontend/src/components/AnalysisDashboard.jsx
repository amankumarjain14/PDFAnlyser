import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Download, Copy, Share2, ArrowLeft, ExternalLink, FileText, MessageSquare } from 'lucide-react';
import ChatBox from './ChatBox';
import styles from './AnalysisDashboard.module.css';

const AnalysisDashboard = ({ result, onReset }) => {
  const [activeTab, setActiveTab] = useState('report'); // 'report' | 'chat'
  const [copyStatus, setCopyStatus] = useState('Copy Summary');

  const handleCopySummary = () => {
    navigator.clipboard.writeText(result.summary);
    setCopyStatus('Copied!');
    setTimeout(() => setCopyStatus('Copy Summary'), 2000);
  };

  return (
    <div className={styles.dashboard}>
      <div className={styles.topBar}>
        <button onClick={onReset} className={styles.backBtn}>
          <ArrowLeft size={16} />
          Back
        </button>
        <div className={styles.docInfo}>
          <FileText size={18} className={styles.fileIcon} />
          <span className={styles.fileName}>{result.original_filename}</span>
          <span className={styles.pill}>{result.word_count} words</span>
        </div>
        <div className={styles.actions}>
          <button onClick={handleCopySummary} className="btn-ghost btn-sm">
            <Copy size={16} />
            {copyStatus}
          </button>
          <a href={result.docx_download_url} className="btn-primary btn-sm">
            <Download size={16} />
            DOCX
          </a>
        </div>
      </div>

      <div className={styles.mainContainer}>
        <div className={styles.tabsMobile}>
          <button 
            className={activeTab === 'report' ? styles.activeTab : ''} 
            onClick={() => setActiveTab('report')}
          >
            <FileText size={18} />
            Report
          </button>
          <button 
            className={activeTab === 'chat' ? styles.activeTab : ''} 
            onClick={() => setActiveTab('chat')}
          >
            <MessageSquare size={18} />
            Chat
          </button>
        </div>

        <div className={`${styles.reportPane} ${activeTab !== 'report' ? styles.hiddenMobile : ''}`}>
          <div className={styles.paneHeader}>
            <div className={styles.headerInfo}>
              <h2>Enhanced Report</h2>
              <p>Generated on {result.processed_date}</p>
            </div>
            {result.google_drive_view_link && (
              <a href={result.google_drive_view_link} target="_blank" rel="noreferrer" className={styles.driveLink}>
                Google Drive <ExternalLink size={14} />
              </a>
            )}
          </div>
          <div className={`${styles.scrollArea} markdown-body`}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {result.enhanced_content}
            </ReactMarkdown>
          </div>
        </div>

        <div className={`${styles.chatPane} ${activeTab !== 'chat' ? styles.hiddenMobile : ''}`}>
          <ChatBox jobId={result.job_id} />
        </div>
      </div>
    </div>
  );
};

export default AnalysisDashboard;
