"""
Configuration du backend FastAPI
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Free Mobile Chatbot API"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # PostgreSQL Local
    POSTGRES_LOCAL_HOST: str = os.getenv("POSTGRES_LOCAL_HOST", "localhost")
    POSTGRES_LOCAL_PORT: int = int(os.getenv("POSTGRES_LOCAL_PORT", 5432))
    POSTGRES_LOCAL_USER: str = os.getenv("POSTGRES_LOCAL_USER", "chatbot_user")
    POSTGRES_LOCAL_PASSWORD: str = os.getenv("POSTGRES_LOCAL_PASSWORD", "")
    POSTGRES_LOCAL_DB: str = os.getenv("POSTGRES_LOCAL_DB", "chatbot_free_mobile")
    
    # Supabase
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY: Optional[str] = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    SUPABASE_DB_URL: Optional[str] = os.getenv("SUPABASE_DB_URL")
    USE_SUPABASE: bool = os.getenv("USE_SUPABASE", "false").lower() == "true"
    
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    
    # Services URLs
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:8501")
    AI_ENGINE_URL: str = os.getenv("AI_ENGINE_URL", "http://localhost:8001")
    SOCIAL_MONITOR_URL: str = os.getenv("SOCIAL_MONITOR_URL", "http://localhost:8002")
    
    # Free Mobile Links
    FREE_MOBILE_FAQ_URL: str = os.getenv("FREE_MOBILE_FAQ_URL", "https://mobile.free.fr/assistance/")
    FREE_MOBILE_ESPACE_CLIENT_URL: str = os.getenv("FREE_MOBILE_ESPACE_CLIENT_URL", "https://mobile.free.fr/moncompte/")
    FREE_MOBILE_CONTACT_URL: str = os.getenv("FREE_MOBILE_CONTACT_URL", "https://mobile.free.fr/assistance/contact.html")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", 100))
    RATE_LIMIT_AUTH_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_AUTH_PER_MINUTE", 5))
    RATE_LIMIT_CHAT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_CHAT_PER_MINUTE", 20))
    
    # Timeouts
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", 30))
    AI_TIMEOUT: int = int(os.getenv("AI_TIMEOUT", 60))
    REDIS_TIMEOUT: int = int(os.getenv("REDIS_TIMEOUT", 5))
    
    @property
    def DATABASE_URL(self) -> str:
        """Retourne l'URL de la base de données selon la configuration"""
        if self.USE_SUPABASE and self.SUPABASE_DB_URL:
            return self.SUPABASE_DB_URL
        else:
            import urllib.parse
            # Encoder le mot de passe pour éviter les problèmes d'encodage
            encoded_password = urllib.parse.quote_plus(self.POSTGRES_LOCAL_PASSWORD)
            return (
                f"postgresql://{self.POSTGRES_LOCAL_USER}:{encoded_password}"
                f"@{self.POSTGRES_LOCAL_HOST}:{self.POSTGRES_LOCAL_PORT}/{self.POSTGRES_LOCAL_DB}"
            )
    
    @property
    def REDIS_URL(self) -> str:
        """Retourne l'URL Redis"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()


