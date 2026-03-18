import sqlite3
import os
from datetime import datetime
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
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    
    # Ensure IP column exists (if table was already there)
    try:
        cursor.execute("ALTER TABLE uploads ADD COLUMN ip TEXT")
        conn.commit()
    except:
        pass # Already exists
        
    conn.close()

def log_visit(ip: str, user_agent: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if we logged this IP/UA in the last 30 minutes to avoid spam
        cursor.execute('''
            SELECT 1 FROM visits 
            WHERE ip = ? AND user_agent = ? 
            AND timestamp > datetime('now', '-30 minutes')
            LIMIT 1
        ''', (ip, user_agent))
        
        if cursor.fetchone():
            conn.close()
            return # Already logged recently

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

def is_rate_limited(ip: str, action: str = "upload") -> bool:
    """
    Check if IP has exceeded limits.
    Uploads: 5 per hour
    Chat: 20 per hour
    """
    limit = 5 if action == "upload" else 20
    table = "uploads" if action == "upload" else "visits" # Using visits table for chat hits tracking? 
    # Better to have a separate 'actions' table eventually, but for now we follow the user request.
    
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
        cursor = conn.cursor()
        
        # Total visits
        cursor.execute('SELECT COUNT(*) FROM visits')
        total_visits = cursor.fetchone()[0]
        
        # Unique visitors
        cursor.execute('SELECT COUNT(DISTINCT ip) FROM visits')
        total_unique = cursor.fetchone()[0]
        
        # Total uploads
        cursor.execute('SELECT COUNT(*) FROM uploads')
        total_uploads = cursor.fetchone()[0]
        
        # Recent visits (last 10)
        cursor.execute('SELECT ip, user_agent, timestamp FROM visits ORDER BY timestamp DESC LIMIT 10')
        recent_visits = [
            {"ip": r[0], "user_agent": r[1], "timestamp": r[2]} for r in cursor.fetchall()
        ]
        
        # Recent uploads (last 10)
        cursor.execute('SELECT filename, job_id, timestamp, ip FROM uploads ORDER BY timestamp DESC LIMIT 10')
        recent_uploads = [
            {"filename": r[0], "job_id": r[1], "timestamp": r[2], "ip": r[3] or "unknown"} for r in cursor.fetchall()
        ]
        
        conn.close()
        return {
            "total_visits": total_visits,
            "total_unique_visitors": total_unique,
            "total_uploads": total_uploads,
            "recent_visits": recent_visits,
            "recent_uploads": recent_uploads
        }
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {}

# Run init on import
init_db()
