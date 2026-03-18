import { useState, useEffect } from 'react';
import { getAdminStats, downloadAdminFile } from '../services/api';
import { Users, FileUp, Clock, ShieldCheck, Lock, AlertCircle, RefreshCw, LogOut, Download, FileText, File } from 'lucide-react';
import styles from './AdminDashboard.module.css';

const AdminDashboard = ({ onBack }) => {
  const [password, setPassword] = useState('');
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const fetchStats = async (pw) => {
    setIsLoading(true);
    setError('');
    try {
      const res = await getAdminStats(pw || password);
      setStats(res.data);
      setIsAuthorized(true);
      setError('');
    } catch (err) {
      setError(err.response?.status === 401 ? 'Invalid password' : 'Failed to load stats');
      setIsAuthorized(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async (type, jobId, filename) => {
    try {
      const response = await downloadAdminFile(password, type, jobId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const downloadName = type === 'pdf' ? filename : filename.replace('.pdf', '_enhanced.docx');
      link.setAttribute('download', downloadName);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Download failed: ' + (err.response?.status === 404 ? 'File not found' : 'Network error'));
    }
  };

  const handleLogin = (e) => {
    e.preventDefault();
    fetchStats();
  };

  if (!isAuthorized) {
    return (
      <div className={styles.loginContainer}>
        <div className={styles.loginCard}>
          <div className={styles.iconCircle}><Lock size={24} /></div>
          <h2>Admin Access</h2>
          <p>Please enter the admin password</p>
          <form onSubmit={handleLogin}>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              autoFocus
            />
            {error && <div className={styles.error}><AlertCircle size={14} /> {error}</div>}
            <button type="submit" disabled={isLoading}>
              {isLoading ? <RefreshCw className={styles.spin} size={18} /> : 'Login'}
            </button>
          </form>
          <button className={styles.backLink} onClick={onBack}>Return to Site</button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.dashboard}>
      <header className={styles.header}>
        <div className={styles.headerTitle}>
          <ShieldCheck className={styles.shieldIcon} />
          <h1>Admin Analytics</h1>
        </div>
        <div className={styles.headerActions}>
          <button className={styles.refreshBtn} onClick={() => fetchStats()} disabled={isLoading}>
            <RefreshCw className={isLoading ? styles.spin : ''} size={16} />
            Refresh
          </button>
          <button className={styles.logoutBtn} onClick={() => setIsAuthorized(false)}>
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </header>

      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={styles.statIcon}><Users size={20} /></div>
          <div className={styles.statInfo}>
            <span className={styles.label}>Total Visits</span>
            <span className={styles.value}>{stats?.total_visits || 0}</span>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon}><ShieldCheck size={20} /></div>
          <div className={styles.statInfo}>
            <span className={styles.label}>Unique Visitors</span>
            <span className={styles.value}>{stats?.total_unique_visitors || 0}</span>
          </div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon}><FileUp size={20} /></div>
          <div className={styles.statInfo}>
            <span className={styles.label}>Total Uploads</span>
            <span className={styles.value}>{stats?.total_uploads || 0}</span>
          </div>
        </div>
      </div>

      <div className={styles.tablesRow}>
        <div className={styles.tableCard}>
          <div className={styles.cardHeader}><Clock size={16} /> Recent Visits</div>
          <div className={styles.tableWrapper}>
            <table>
              <thead>
                <tr>
                  <th>IP Address</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {stats?.recent_visits.map((v, i) => (
                  <tr key={i}>
                    <td><code>{v.ip}</code></td>
                    <td>{new Date(v.timestamp + 'Z').toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className={styles.tableCard}>
          <div className={styles.cardHeader}><FileUp size={16} /> Recent Uploads</div>
          <div className={styles.tableWrapper}>
            <table>
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Uploader IP</th>
                  <th>Timestamp</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {stats?.recent_uploads.map((u, i) => (
                  <tr key={i}>
                    <td className={styles.filenameTd}>{u.filename}</td>
                    <td><code>{u.ip}</code></td>
                    <td>{new Date(u.timestamp + 'Z').toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}</td>
                    <td>
                      <div className={styles.actionGroup}>
                        <button 
                          className={styles.iconBtn} 
                          onClick={() => handleDownload('pdf', u.job_id, u.filename)}
                          title="Download Original PDF"
                        >
                          <File size={16} />
                        </button>
                        <button 
                          className={styles.iconBtn} 
                          onClick={() => handleDownload('docx', u.job_id, u.filename)}
                          title="Download Enhanced DOCX"
                        >
                          <FileText size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
