import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { getDownloadURL } from '../services/api';
import styles from './ResultCard.module.css';

export default function ResultCard({ result, onReset }) {
  const [previewOpen, setPreviewOpen] = useState(false);

  const downloadUrl = getDownloadURL(result.job_id);

  return (
    <div className="animate-fade-up">
      {/* ── Success banner ─────────────────────────────────── */}
      <div className={styles.banner}>
        <div className={styles.bannerIcon}>✅</div>
        <div>
          <h3 className={styles.bannerTitle}>Analysis Complete!</h3>
          <p className={styles.bannerSub}>{result.summary}</p>
        </div>
      </div>

      {/* ── Metadata grid ──────────────────────────────────── */}
      <div className={`${styles.card} glass`}>
        <div className={styles.metaGrid}>
          <MetaTile label="Original File" value={result.original_filename} icon="📄" />
          <MetaTile label="Word Count"    value={result.word_count.toLocaleString()} icon="📊" />
          <MetaTile label="Processed"     value={result.processed_date} icon="🕐" />
          <MetaTile label="Version"       value={result.version} icon="🏷️" />
        </div>
      </div>

      {/* ── Actions ────────────────────────────────────────── */}
      <div className={`${styles.card} glass`}>
        <h3 className={styles.sectionTitle}>Download & Share</h3>
        <div className={styles.actions}>
          <a
            href={downloadUrl}
            download
            className="btn btn-primary"
            id="download-docx-btn"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 1v9M4 7l4 4 4-4M2 13h12" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Download DOCX
          </a>

          <button
            className="btn btn-outline"
            onClick={() => setPreviewOpen(true)}
            id="preview-btn"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="3" stroke="currentColor" strokeWidth="1.8"/>
              <path d="M1 8s2.5-5 7-5 7 5 7 5-2.5 5-7 5-7-5-7-5z" stroke="currentColor" strokeWidth="1.8"/>
            </svg>
            Preview Content
          </button>

          {result.google_drive_view_link && (
            <a
              href={result.google_drive_view_link}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-ghost"
              id="drive-view-btn"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M8 2l4.5 8H3.5L8 2z" stroke="currentColor" strokeWidth="1.6" fill="none"/>
                <path d="M2 12l2-4h8l2 4H2z" stroke="currentColor" strokeWidth="1.6" fill="none"/>
              </svg>
              View on Drive
            </a>
          )}

          <button
            className="btn btn-ghost"
            onClick={onReset}
            id="new-analysis-btn"
          >
            + New Analysis
          </button>
        </div>
      </div>

      {/* ── Content preview modal ──────────────────────────── */}
      {previewOpen && (
        <PreviewModal
          content={result.enhanced_content}
          filename={result.original_filename}
          onClose={() => setPreviewOpen(false)}
        />
      )}
    </div>
  );
}

function MetaTile({ label, value, icon }) {
  return (
    <div className={styles.metaTile}>
      <span className={styles.metaIcon}>{icon}</span>
      <div>
        <p className={styles.metaLabel}>{label}</p>
        <p className={styles.metaValue}>{value}</p>
      </div>
    </div>
  );
}

function PreviewModal({ content, filename, onClose }) {
  return (
    <div className={styles.overlay} onClick={onClose} id="preview-modal-overlay">
      <div
        className={`${styles.modal} glass`}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label="Content preview"
      >
        <div className={styles.modalHeader}>
          <div>
            <h3 className={styles.modalTitle}>Enhanced Content Preview</h3>
            <p className={styles.modalSub}>{filename}</p>
          </div>
          <button className="btn btn-ghost" onClick={onClose} id="close-preview-btn">✕ Close</button>
        </div>
        <div className={styles.modalBody}>
          <div className="markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
}
