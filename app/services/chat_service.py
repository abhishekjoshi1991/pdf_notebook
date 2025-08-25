from typing import List
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

from models.schemas import ChatResponse, Citation
from services.vector_service import VectorService
from config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from app_logging.logger import Logger
logger = Logger().get_logger(__name__)

class ChatService:
    def __init__(self, vector_service: VectorService):
        if settings.LLM_PROVIDER == "openai":
            print("using openai model")

            self.llm = ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model="gpt-4.1",
                temperature=0,
                max_tokens=500
            )
        else:
            self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=settings.GOOGLE_API_KEY, temperature=0)

        self.vector_service = vector_service
        self.qa_prompt = PromptTemplate(
            template = """
            Use the following pieces of context to answer the question. 
            - Keep the answer concise and directly relevant.
            - Prefer pointwise/bullet format if multiple aspects exist.
            - If you don't know the answer, just say "I don't know."

            Context:
            {context}

            Question: {question}

            Answer:
            """,
            input_variables=["context", "question"]
        )
    
    def generate_response(self, query: str) -> ChatResponse:
        """Generate response using RetrievalQA"""
        if not self.vector_service.has_documents():
            return ChatResponse(
                answer="No document uploaded. Please upload a PDF first.",
                citations=[]
            )
        
        try:
            retriever = self.vector_service.current_vectorstore.as_retriever(
                search_kwargs={"k": settings.MAX_CHUNKS_PER_QUERY}
            )
            
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": self.qa_prompt},
                return_source_documents=True
            )
            
            logger.info(f"Chat Running QA chain with query: {query}")
            # result = qa_chain({"query": query})
            result = qa_chain.invoke(query)
            answer = result["result"]
            source_docs = result.get("source_documents", [])
            
            citations = [
                Citation(
                    page_number=doc.metadata.get('page_number', 1),
                    content_preview=doc.page_content[:100] + "...",
                )
                for doc in source_docs
            ]
            return answer, citations
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return ChatResponse(
                answer=f"Error: {str(e)}",
                citations=[]
            )