import sqlite3
import json
from datetime import datetime

def init_db():
    """Initialize the SQLite database"""
    conn = sqlite3.connect('analyses.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text_input TEXT NOT NULL,
            summary TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_analysis(text: str, summary: str, metadata: dict) -> int:
    """Save analysis to database and return the ID"""
    conn = sqlite3.connect('analyses.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO analyses (text_input, summary, metadata)
        VALUES (?, ?, ?)
    ''', (text, summary, json.dumps(metadata)))
    analysis_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return analysis_id

def search_analyses(topic: str = None, keyword: str = None):
    """Search analyses by topic or keyword"""
    conn = sqlite3.connect('analyses.db')
    cursor = conn.cursor()
    
    if topic:
        cursor.execute('''
            SELECT id, text_input, summary, metadata, created_at
            FROM analyses
            WHERE metadata LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{topic}%',))
    elif keyword:
        cursor.execute('''
            SELECT id, text_input, summary, metadata, created_at
            FROM analyses
            WHERE metadata LIKE ? OR text_input LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{keyword}%', f'%{keyword}%'))
    else:
        cursor.execute('''
            SELECT id, text_input, summary, metadata, created_at
            FROM analyses
            ORDER BY created_at DESC
        ''')
    
    results = cursor.fetchall()
    conn.close()
    
    analyses = []
    for row in results:
        analyses.append({
            "id": row[0],
            "text_input": row[1],
            "summary": row[2],
            "metadata": json.loads(row[3]),
            "created_at": row[4]
        })
    
    return analyses
