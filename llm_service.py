import json
import os
import openai
from fastapi import HTTPException
from text_processing import extract_keywords

def analyze_text_with_llm(text: str) -> tuple[str, dict]:
    """Use OpenAI to analyze text and extract both summary and structured data in one call"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY environment variable not set")
        
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured information from text. Return only valid JSON."},
                {"role": "user", "content": f"""
                Analyze this text and return JSON with:
                - summary: 1-2 sentence summary (string)
                - title: extract or generate a title (string)
                - topics: 3 key topics (array of strings)
                - sentiment: positive/neutral/negative (string)
                
                Text: {text}
                """}
            ],
            max_tokens=400
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Extract summary and metadata separately
        summary = result.pop('summary', '')
        metadata = result
        
        # Add keywords using our custom function
        keywords = extract_keywords(text)
        metadata['keywords'] = keywords
        
        # Add simple confidence score (0.5 to 0.9 based on text length)
        confidence = min(0.9, 0.5 + (len(text) / 2000) * 0.4)
        metadata['confidence'] = round(confidence, 2)
        
        return summary, metadata
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM analysis failed: {str(e)}")
