from typing import List, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from config import settings
import tempfile
import shutil
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app_logging.logger import Logger
logger = Logger().get_logger(__name__)

class VectorService:
    def __init__(self):
        if settings.LLM_PROVIDER == "openai":
            logger.info("using openai embedding")
            self.embeddings = OpenAIEmbeddings(
                api_key=settings.OPENAI_API_KEY
            )
        else:
            logger.info("using gemini embedding")
            self.embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001", google_api_key=settings.GOOGLE_API_KEY)

        self.current_vectorstore: Optional[Chroma] = None
        self.temp_dir = None
    
    def store_documents(self, documents: List[Document]) -> None:
        """Store documents - replaces previous session"""
        if not documents:
            logger.warning("No documents provided to store_documents.")
            return
        try:
            self.clear_current_session()
            
            # Create temp directory
            self.temp_dir = tempfile.mkdtemp(prefix="chroma_session_")
            
            # Create vectorstore
            self.current_vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                # persist_directory=self.temp_dir,
                collection_name="current_document"
            )
            logger.info(f"Created vectorstore successfully")
        except Exception as e:
            logger.error(f"Error in store_documents: {e}", exc_info=True)
            raise
    
    def clear_current_session(self) -> None:
        """Clear current session"""
        if self.current_vectorstore:
            try:
                self.current_vectorstore._client.delete_collection("current_document")
                logger.info("Deleted old Chroma collection.")
            except Exception as e:
                logger.warning(f"Error deleting Chroma collection: {e}", exc_info=True)
            finally:
                self.current_vectorstore = None

        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temp directory: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Error cleaning up temp directory: {e}", exc_info=True)
        
        self.temp_dir = None
    
    def has_documents(self) -> bool:
        """Check if session has documents"""
        result = self.current_vectorstore is not None
        return result