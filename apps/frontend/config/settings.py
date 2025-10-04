"""
Configuration du frontend Streamlit
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class FrontendSettings(BaseSettings):
    # Application
    APP_NAME: str = "Free Mobile Chatbot"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # URLs des services
    BACKEND_API_URL: str = os.getenv("BACKEND_API_URL", "http://localhost:8000")
    AI_ENGINE_URL: str = os.getenv("AI_ENGINE_URL", "http://localhost:8001")
    SOCIAL_MONITOR_URL: str = os.getenv("SOCIAL_MONITOR_URL", "http://localhost:8002")
    
    # Configuration Streamlit
    PAGE_TITLE: str = "Free Mobile - Support Client"
    PAGE_ICON: str = "🆓"
    LAYOUT: str = "wide"
    SIDEBAR_STATE: str = "expanded"
    
    # Session
    SESSION_TIMEOUT: int = int(os.getenv("SESSION_TIMEOUT", 3600))  # 1 heure
    MAX_MESSAGES: int = int(os.getenv("MAX_MESSAGES", 100))
    
    # UI
    THEME: str = "light"
    PRIMARY_COLOR: str = "#FF6600"  # Orange Free Mobile
    BACKGROUND_COLOR: str = "#FFFFFF"
    SECONDARY_COLOR: str = "#F0F0F0"
    
    # Chat
    CHAT_HEIGHT: int = 400
    MESSAGE_ANIMATION: bool = True
    TYPING_INDICATOR: bool = True
    
    # Analytics
    ENABLE_ANALYTICS: bool = os.getenv("ENABLE_ANALYTICS", "true").lower() == "true"
    REFRESH_INTERVAL: int = int(os.getenv("REFRESH_INTERVAL", 30))  # secondes
    
    # Mastodon
    MASTODON_BASE_URL: str = os.getenv("MASTODON_BASE_URL", "https://mastodon.social")
    
    # Free Mobile Links
    FREE_MOBILE_FAQ_URL: str = os.getenv("FREE_MOBILE_FAQ_URL", "https://mobile.free.fr/assistance/")
    FREE_MOBILE_ESPACE_CLIENT_URL: str = os.getenv("FREE_MOBILE_ESPACE_CLIENT_URL", "https://mobile.free.fr/moncompte/")
    FREE_MOBILE_CONTACT_URL: str = os.getenv("FREE_MOBILE_CONTACT_URL", "https://mobile.free.fr/assistance/contact.html")
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = FrontendSettings()


