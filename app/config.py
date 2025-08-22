import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys
    LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # App Settings
    APP_NAME = "NotebookLM Backend"
    DEBUG = True
    
    # File Settings
    UPLOAD_DIR = "static/uploads"
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    # Processing Settings
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    MAX_CHUNKS_PER_QUERY = 5

settings = Settings()

# Validate required API keys
if not settings.LLAMA_CLOUD_API_KEY:
    raise ValueError("LLAMA_CLOUD_API_KEY is required in .env file")
if not settings.OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required in .env file")