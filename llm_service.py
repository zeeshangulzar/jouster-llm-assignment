import json
import os
import openai
from fastapi import HTTPException
from text_processing import extract_keywords

def analyze_with_llm(text: str) -> dict:
    """Use OpenAI to analyze text and extract structured data"""
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
        
        # Add simple confidence score (0.5 to 0.9 based on text length)
        confidence = min(0.9, 0.5 + (len(text) / 2000) * 0.4)
        result['confidence'] = round(confidence, 2)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM analysis failed: {str(e)}")

def generate_summary(text: str) -> str:
    """Generate a 1-2 sentence summary using OpenAI"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY environment variable not set")
        
        openai.api_key = api_key
        summary_response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": f"Summarize this text in 1-2 sentences: {text}"}
            ],
            max_tokens=100
        )
        return summary_response.choices[0].message.content
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")
