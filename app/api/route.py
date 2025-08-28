import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException

from models.schemas import UploadResponse, ChatRequest, ChatResponse
from services.pdf_service import PDFService
from services.vector_service import VectorService
from services.chat_service import ChatService
from config import settings
from app_logging.logger import Logger
logger = Logger().get_logger(__name__)

pdf_service = PDFService()
vector_service = VectorService()
chat_service = ChatService(vector_service)

router = APIRouter(prefix="/api", tags=["pdf-chat"])

# Upload Endpoint
@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process PDF file"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.pdf")
    
    try:
        # Save file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Processing PDF: {file.filename}")

        # Process PDF
        documents = await pdf_service.process_pdf(file_path)
        
        vector_service.store_documents(documents)
        pages_processed = len(set(doc.metadata.get('page_number', 1) for doc in documents))
        
        return UploadResponse(
            message=f"PDF '{file.filename}' processed successfully",
            pages_processed=pages_processed
        )
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


# Chat Endpoint
@router.post("/chat", response_model=ChatResponse)
def chat_with_document(request: ChatRequest):
    """Chat with the currently uploaded document"""
    print(vector_service.has_documents())
    if not vector_service.has_documents():
        raise HTTPException(status_code=400, detail="Upload PDF first!")
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        logger.info(f"Processing query: {request.query}")
        answer, citations = chat_service.generate_response(request.query)
        return ChatResponse(answer=answer, citations=citations)
    except Exception as e:
        logger.error(f"Error in processing the query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
