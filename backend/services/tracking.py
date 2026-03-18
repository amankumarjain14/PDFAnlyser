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
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def log_visit(ip: str, user_agent: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO visits (ip, user_agent) VALUES (?, ?)', (ip, user_agent))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging visit: {e}")

def log_upload(filename: str, job_id: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO uploads (filename, job_id) VALUES (?, ?)', (filename, job_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging upload: {e}")

def get_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total visits
        cursor.execute('SELECT COUNT(*) FROM visits')
        total_visits = cursor.fetchone()[0]
        
        # Total uploads
        cursor.execute('SELECT COUNT(*) FROM uploads')
        total_uploads = cursor.fetchone()[0]
        
        # Recent visits (last 10)
        cursor.execute('SELECT ip, user_agent, timestamp FROM visits ORDER BY timestamp DESC LIMIT 10')
        recent_visits = [
            {"ip": r[0], "user_agent": r[1], "timestamp": r[2]} for r in cursor.fetchall()
        ]
        
        # Recent uploads (last 10)
        cursor.execute('SELECT filename, job_id, timestamp FROM uploads ORDER BY timestamp DESC LIMIT 10')
        recent_uploads = [
            {"filename": r[0], "job_id": r[1], "timestamp": r[2]} for r in cursor.fetchall()
        ]
        
        conn.close()
        return {
            "total_visits": total_visits,
            "total_uploads": total_uploads,
            "recent_visits": recent_visits,
            "recent_uploads": recent_uploads
        }
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {}

# Run init on import
init_db()
