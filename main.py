from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import json

app = FastAPI(title="LLM Knowledge Extractor")

# Database setup
def init_db():
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

# Initialize database on startup
init_db()

class TextInput(BaseModel):
    text: str

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)