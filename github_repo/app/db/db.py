import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'analysis.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS videos (
        video_id TEXT PRIMARY KEY,
        filename TEXT,
        result TEXT,
        confidence REAL,
        status TEXT
    )''')
    conn.commit()
    conn.close()

def insert_video(video_id, filename):
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO videos (video_id, filename, status) VALUES (?, ?, ?)', (video_id, filename, 'UPLOADED'))
    conn.commit()
    conn.close()

def update_analysis(video_id, result, confidence, status):
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE videos SET result=?, confidence=?, status=? WHERE video_id=?', (result, confidence, status, video_id))
    conn.commit()
    conn.close()

def get_analysis_result(video_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT result, confidence, status FROM videos WHERE video_id=?', (video_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_video_filename(video_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT filename FROM videos WHERE video_id=?', (video_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None
