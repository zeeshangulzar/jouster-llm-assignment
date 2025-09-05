from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import json
import re
from collections import Counter
from typing import List, Optional
import openai
import os

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

def extract_keywords(text: str) -> List[str]:
    """Extract 3 most frequent nouns from text"""
    # Simple noun extraction using regex
    words = re.findall(r'\b[A-Za-z]{3,}\b', text.lower())
    # Filter out common words
    stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'man', 'men', 'put', 'say', 'she', 'too', 'use'}
    words = [word for word in words if word not in stop_words and len(word) > 3]
    word_counts = Counter(words)
    return [word for word, count in word_counts.most_common(3)]

def analyze_with_llm(text: str) -> dict:
    """Use OpenAI to analyze text and extract structured data"""
    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured information from text. Return only valid JSON."},
                {"role": "user", "content": f"""
                Analyze this text and return JSON with:
                - title: extract or generate a title (string)
                - topics: 3 key topics (array of strings)
                - sentiment: positive/neutral/negative (string)
                
                Text: {text}
                """}
            ],
            max_tokens=300
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Add keywords using our custom function
        keywords = extract_keywords(text)
        result['keywords'] = keywords
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM analysis failed: {str(e)}")

class TextInput(BaseModel):
    text: str

class AnalysisResponse(BaseModel):
    id: int
    summary: str
    metadata: dict
    created_at: str

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)