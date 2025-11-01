"""Configuration management for WorkWise backend"""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = "/home/user/app"
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

class Settings:
    """Application settings loaded from environment variables"""
    
    # Faiss (local) configuration
    FAISS_INDEX_PATH: str = os.path.join(DATA_DIR, "faiss.index")
    FAISS_PAYLOADS_PATH: str = os.path.join(DATA_DIR, "faiss_payloads.json")

    # Qdrant Configuration
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "jira_tickets")
    
    # Hugging Face Configuration
    HF_API_URL: str = os.getenv("HF_API_URL", "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1")
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    
    # Embedding Model
    #EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    #EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/multi-qa-MiniLM-L6-cos-v1")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 7860))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "debug")
    
    # CORS
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    
    # Vector Search
    TOP_K: int = 5
    SCORE_THRESHOLD: float = 0.0

settings = Settings()
