from typing import List
from llama_parse import LlamaParse
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import settings
from app_logging.logger import Logger
logger = Logger().get_logger(__name__)

class PDFService:
    def __init__(self):
        self.parser = LlamaParse(
            api_key=settings.LLAMA_CLOUD_API_KEY,
            result_type="markdown",
            verbose=True
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    async def process_pdf(self, file_path: str) -> List[Document]:
        """Process PDF and return LangChain Documents with proper metadata"""
        try:
            result = await self.parser.aparse(file_path)
            if not result:
                logger.error(f"Parsing failed for file: {file_path}")
                return []
            
            # Get per-page documents (with page numbers in metadata)
            try:
                markdown_documents = result.get_markdown_documents(split_by_page=True)
            except Exception as e:
                logger.exception(f"Error extracting markdown docs from {file_path}: {e}")
                return []
            
            processed_docs = []
            for doc in markdown_documents:
                # Keep original page number metadata from LlamaParse
                page_num = doc.metadata.get("page_number", None)

                lc_doc = Document(
                    page_content=doc.text,
                    metadata={
                        "source": file_path,
                        "page_number": page_num,
                        "file_name": doc.metadata.get("file_name")
                    }
                )

                # Chunk this page
                chunks = self.text_splitter.split_documents([lc_doc])

                for i, chunk in enumerate(chunks):
                    chunk.metadata.update({"chunk_index": i})
                    processed_docs.append(chunk)

        except Exception as e:
            logger.exception(f"Unexpected error while processing PDF {file_path}: {e}")
            return []
        return processed_docs
