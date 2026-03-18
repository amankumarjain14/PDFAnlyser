import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path

# Database setup
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "analytics.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Table for visits
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            user_agent TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Table for uploads
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            job_id TEXT,
            ip TEXT,
            status TEXT DEFAULT 'PENDING',
            processing_time REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Table for chat hits
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT,
            ip TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    
    # Schema migration helpers
    try:
        cursor.execute("ALTER TABLE uploads ADD COLUMN status TEXT DEFAULT 'PENDING'")
        conn.commit()
    except: pass
    try:
        cursor.execute("ALTER TABLE uploads ADD COLUMN processing_time REAL")
        conn.commit()
    except: pass
    try:
        cursor.execute("ALTER TABLE uploads ADD COLUMN ip TEXT")
        conn.commit()
    except: pass
        
    conn.close()

def log_visit(ip: str, user_agent: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 1 FROM visits WHERE ip = ? AND user_agent = ? 
            AND timestamp > datetime('now', '-30 minutes') LIMIT 1
        ''', (ip, user_agent))
        if cursor.fetchone():
            conn.close()
            return

        cursor.execute('INSERT INTO visits (ip, user_agent) VALUES (?, ?)', (ip, user_agent))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging visit: {e}")

def log_upload(filename: str, job_id: str, ip: str = "unknown"):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO uploads (filename, job_id, ip) VALUES (?, ?, ?)', (filename, job_id, ip))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging upload: {e}")

from typing import Optional, List, Dict

def update_upload_status(job_id: str, status: str, processing_time: Optional[float] = None):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        if processing_time is not None:
            cursor.execute('UPDATE uploads SET status = ?, processing_time = ? WHERE job_id = ?', (status, processing_time, job_id))
        else:
            cursor.execute('UPDATE uploads SET status = ? WHERE job_id = ?', (status, job_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating upload status: {e}")

def log_chat(job_id: str, ip: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO chat_logs (job_id, ip) VALUES (?, ?)', (job_id, ip))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging chat: {e}")

def is_rate_limited(ip: str, action: str = "upload") -> bool:
    limit = 5 if action == "upload" else 20
    table = "uploads" if action == "upload" else "chat_logs"
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE ip = ? AND timestamp > datetime('now', '-1 hour')", (ip,))
        count = cursor.fetchone()[0]
        conn.close()
        return count >= limit
    except Exception as e:
        print(f"Error checking rate limit: {e}")
        return False

def get_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Core counts
        total_visits = cursor.execute('SELECT COUNT(*) FROM visits').fetchone()[0]
        total_unique = cursor.execute('SELECT COUNT(DISTINCT ip) FROM visits').fetchone()[0]
        total_uploads = cursor.execute('SELECT COUNT(*) FROM uploads').fetchone()[0]
        
        # Advanced Metrics
        avg_time = cursor.execute('SELECT AVG(processing_time) FROM uploads WHERE status = "SUCCESS"').fetchone()[0] or 0
        unique_uploaders = cursor.execute('SELECT COUNT(DISTINCT ip) FROM uploads').fetchone()[0]
        conv_rate = (unique_uploaders / total_unique * 100) if total_unique > 0 else 0
        
        # 7-Day Trend
        daily_stats = []
        for i in range(6, -1, -1):
            day = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            v_count = cursor.execute("SELECT COUNT(*) FROM visits WHERE date(timestamp) = ?", (day,)).fetchone()[0]
            u_count = cursor.execute("SELECT COUNT(*) FROM uploads WHERE date(timestamp) = ?", (day,)).fetchone()[0]
            daily_stats.append({"date": day, "visits": v_count, "uploads": u_count})

        recent_visits = [dict(r) for r in cursor.execute('SELECT ip, user_agent, timestamp FROM visits ORDER BY timestamp DESC LIMIT 10').fetchall()]
        recent_uploads = [dict(r) for r in cursor.execute('SELECT filename, job_id, timestamp, ip, status, processing_time FROM uploads ORDER BY timestamp DESC LIMIT 10').fetchall()]
        
        conn.close()
        return {
            "total_visits": total_visits,
            "total_unique_visitors": total_unique,
            "total_uploads": total_uploads,
            "conversion_rate": round(conv_rate, 1),
            "avg_processing_time": round(avg_time, 1),
            "daily_trends": daily_stats,
            "recent_visits": recent_visits,
            "recent_uploads": recent_uploads
        }
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {}

init_db()
