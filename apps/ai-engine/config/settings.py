"""
Configuration du moteur IA
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class AISettings(BaseSettings):
    # Application
    APP_NAME: str = "Free Mobile AI Engine"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Modèles IA
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "HuggingFaceH4/zephyr-7b-beta")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    LLM_DEVICE: str = os.getenv("LLM_DEVICE", "cpu")  # cpu, cuda, mps
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", 512))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", 0.7))
    
    # RAG Configuration
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", 5))
    RAG_SIMILARITY_THRESHOLD: float = float(os.getenv("RAG_SIMILARITY_THRESHOLD", 0.7))
    VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
    VECTOR_STORE_COLLECTION: str = os.getenv("VECTOR_STORE_COLLECTION", "free_mobile_knowledge")
    
    # Free Mobile Links
    FREE_MOBILE_FAQ_URL: str = os.getenv("FREE_MOBILE_FAQ_URL", "https://mobile.free.fr/assistance/")
    FREE_MOBILE_ESPACE_CLIENT_URL: str = os.getenv("FREE_MOBILE_ESPACE_CLIENT_URL", "https://mobile.free.fr/moncompte/")
    FREE_MOBILE_CONTACT_URL: str = os.getenv("FREE_MOBILE_CONTACT_URL", "https://mobile.free.fr/assistance/contact.html")
    
    # Performance
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", 32))
    MAX_CONTEXT_LENGTH: int = int(os.getenv("MAX_CONTEXT_LENGTH", 2048))
    CACHE_EMBEDDINGS: bool = os.getenv("CACHE_EMBEDDINGS", "true").lower() == "true"
    
    # Monitoring
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = AISettings()


