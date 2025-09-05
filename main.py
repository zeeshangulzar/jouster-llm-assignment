from fastapi import FastAPI, HTTPException
from datetime import datetime
from models import TextInput, AnalysisResponse
from database import init_db, save_analysis, search_analyses
from llm_service import analyze_with_llm, generate_summary

app = FastAPI(title="LLM Knowledge Extractor")

# Initialize database on startup
init_db()

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(input_data: TextInput):
    """Process text and return analysis"""
    
    # Handle empty input
    if not input_data.text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty")
    
    try:
        # Generate summary
        summary = generate_summary(input_data.text)
        
        # Extract metadata
        metadata = analyze_with_llm(input_data.text)
        
        # Store in database
        analysis_id = save_analysis(input_data.text, summary, metadata)
        
        return AnalysisResponse(
            id=analysis_id,
            summary=summary,
            metadata=metadata,
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/search")
async def search_analyses_endpoint(topic: str = None, keyword: str = None):
    """Search analyses by topic or keyword"""
    analyses = search_analyses(topic, keyword)
    return {"analyses": analyses}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)