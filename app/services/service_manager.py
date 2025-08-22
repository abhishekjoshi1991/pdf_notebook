from services.pdf_service import PDFService
from services.vector_service import VectorService
from services.chat_service import ChatService

class ServiceManager:
    """Singleton to manage shared services across the application"""
    
    _instance = None
    _pdf_service = None
    _vector_service = None
    _chat_service = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceManager, cls).__new__(cls)
        return cls._instance
    
    def get_pdf_service(self) -> PDFService:
        if self._pdf_service is None:
            self._pdf_service = PDFService()
        return self._pdf_service
    
    def get_vector_service(self) -> VectorService:
        if self._vector_service is None:
            self._vector_service = VectorService()
        return self._vector_service
    
    def get_chat_service(self) -> ChatService:
        if self._chat_service is None:
            # Pass the SAME vector_service instance
            self._chat_service = ChatService(self.get_vector_service())
        return self._chat_service

# Global instance
service_manager = ServiceManager()