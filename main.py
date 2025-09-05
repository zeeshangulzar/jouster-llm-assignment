from fastapi import FastAPI, HTTPException
from datetime import datetime
from models import TextInput, AnalysisResponse, BatchTextInput, BatchAnalysisResponse
from database import init_db, save_analysis, search_analyses
from llm_service import analyze_text_with_llm

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
        # Generate summary and extract metadata in one API call
        summary, metadata = analyze_text_with_llm(input_data.text)
        
        # Store in database
        analysis_id = save_analysis(input_data.text, summary, metadata)
        
        return AnalysisResponse(
            id=analysis_id,
            summary=summary,
            metadata=metadata,
            created_at=datetime.now().isoformat()
        )
        
    except HTTPException as e:
        # Re-raise HTTPExceptions from LLM service
        print(f"HTTPException caught: {e.detail}")
        raise
    except Exception as e:
        print(f"Generic exception caught: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/batch", response_model=BatchAnalysisResponse)
async def analyze_batch_texts(input_data: BatchTextInput):
    """Process multiple texts at once"""
    
    if not input_data.texts:
        raise HTTPException(status_code=400, detail="Texts list cannot be empty")
    
    if len(input_data.texts) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 texts allowed per batch")
    
    results = []
    for i, text in enumerate(input_data.texts):
        if not text.strip():
            results.append({"error": f"Text {i+1} is empty", "index": i})
            continue
            
        try:
            # Generate summary and extract metadata in one API call
            summary, metadata = analyze_text_with_llm(text)
            
            # Store in database
            analysis_id = save_analysis(text, summary, metadata)
            
            results.append({
                "id": analysis_id,
                "summary": summary,
                "metadata": metadata,
                "created_at": datetime.now().isoformat(),
                "index": i
            })
            
        except HTTPException as e:
            results.append({"error": f"Analysis failed: {e.detail}", "index": i})
        except Exception as e:
            results.append({"error": f"Analysis failed: {str(e)}", "index": i})
    
    return BatchAnalysisResponse(results=results)

@app.get("/search")
async def search_analyses_endpoint(topic: str = None, keyword: str = None):
    """Search analyses by topic or keyword"""
    analyses = search_analyses(topic, keyword)
    return {"analyses": analyses}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)