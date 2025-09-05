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
            model="gpt-4o-mini",
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

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(input_data: TextInput):
    """Process text and return analysis"""
    
    # Handle empty input
    if not input_data.text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty")
    
    try:
        # Generate summary
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        summary_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": f"Summarize this text in 1-2 sentences: {input_data.text}"}
            ],
            max_tokens=100
        )
        summary = summary_response.choices[0].message.content
        
        # Extract metadata
        metadata = analyze_with_llm(input_data.text)
        
        # Store in database
        conn = sqlite3.connect('analyses.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analyses (text_input, summary, metadata)
            VALUES (?, ?, ?)
        ''', (input_data.text, summary, json.dumps(metadata)))
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return AnalysisResponse(
            id=analysis_id,
            summary=summary,
            metadata=metadata,
            created_at="now"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/search")
async def search_analyses(topic: Optional[str] = None, keyword: Optional[str] = None):
    """Search analyses by topic or keyword"""
    conn = sqlite3.connect('analyses.db')
    cursor = conn.cursor()
    
    if topic:
        cursor.execute('''
            SELECT id, text_input, summary, metadata, created_at
            FROM analyses
            WHERE metadata LIKE ?
        ''', (f'%{topic}%',))
    elif keyword:
        cursor.execute('''
            SELECT id, text_input, summary, metadata, created_at
            FROM analyses
            WHERE metadata LIKE ? OR text_input LIKE ?
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
    
    return {"analyses": analyses}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)