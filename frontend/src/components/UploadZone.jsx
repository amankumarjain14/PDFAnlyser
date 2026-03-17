import { useCallback, useRef, useState } from 'react';
import styles from './UploadZone.module.css';

export default function UploadZone({ onFileSelect, uploading }) {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const inputRef = useRef(null);

  const handle = useCallback((file) => {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Please select a PDF file.');
      return;
    }
    setSelectedFile(file);
  }, []);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    handle(e.dataTransfer.files[0]);
  }, [handle]);

  const onDragOver = (e) => { e.preventDefault(); setDragOver(true); };
  const onDragLeave = () => setDragOver(false);

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className={styles.wrapper}>
      <div
        className={`${styles.zone} ${dragOver ? styles.dragOver : ''} ${selectedFile ? styles.hasFile : ''}`}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onClick={() => !uploading && inputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
        aria-label="PDF upload drop zone"
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          className={styles.hiddenInput}
          onChange={(e) => handle(e.target.files[0])}
          id="pdf-file-input"
        />

        <div className={styles.iconWrap}>
          {selectedFile ? (
            <svg width="52" height="52" viewBox="0 0 52 52" fill="none">
              <rect width="52" height="52" rx="14" fill="rgba(79,124,255,0.15)"/>
              <path d="M16 14h14l8 8v16a2 2 0 01-2 2H16a2 2 0 01-2-2V16a2 2 0 012-2z" stroke="#4f7cff" strokeWidth="1.8" fill="none"/>
              <path d="M30 14v8h8" stroke="#4f7cff" strokeWidth="1.8" fill="none"/>
              <text x="26" y="35" textAnchor="middle" fill="#4f7cff" fontSize="8" fontWeight="700" fontFamily="Inter">PDF</text>
            </svg>
          ) : (
            <svg width="52" height="52" viewBox="0 0 52 52" fill="none" className={styles.floatIcon}>
              <rect width="52" height="52" rx="14" fill="rgba(79,124,255,0.10)"/>
              <path d="M26 33V19M20 25l6-6 6 6" stroke="#4f7cff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M16 37h20" stroke="#4f7cff" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          )}
        </div>

        {selectedFile ? (
          <div className={styles.fileInfo}>
            <p className={styles.fileName}>{selectedFile.name}</p>
            <p className={styles.fileMeta}>{formatSize(selectedFile.size)} &nbsp;·&nbsp; PDF Document</p>
          </div>
        ) : (
          <div className={styles.hint}>
            <p className={styles.dropText}>
              {dragOver ? 'Drop it here!' : 'Drag & drop your PDF here'}
            </p>
            <p className={styles.orText}>or click to browse</p>
            <p className={styles.limitText}>Max file size: 50 MB</p>
          </div>
        )}
      </div>

      {selectedFile && (
        <div className={styles.actions}>
          <button
            className="btn btn-ghost"
            onClick={(e) => { e.stopPropagation(); setSelectedFile(null); }}
            disabled={uploading}
            id="clear-file-btn"
          >
            ✕ Clear
          </button>
          <button
            className="btn btn-primary"
            onClick={() => onFileSelect(selectedFile)}
            disabled={uploading}
            id="analyse-btn"
          >
            {uploading ? (
              <><span className="spinner" /> Uploading…</>
            ) : (
              <>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M8 1L14 7H10V15H6V7H2L8 1Z" fill="currentColor"/>
                </svg>
                Analyse PDF
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
}
