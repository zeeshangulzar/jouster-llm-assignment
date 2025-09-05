from pydantic import BaseModel
from typing import List

class TextInput(BaseModel):
    text: str

class AnalysisResponse(BaseModel):
    id: int
    summary: str
    metadata: dict
    created_at: str
