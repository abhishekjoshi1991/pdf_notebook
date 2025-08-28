from pydantic import BaseModel
from typing import List, Optional

class UploadResponse(BaseModel):
    message: str
    pages_processed: int
    status: str = "success"

class Citation(BaseModel):
    page_number: int
    content_preview: str

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    status: str = "success"