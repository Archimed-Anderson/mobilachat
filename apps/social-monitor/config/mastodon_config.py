"""
Configuration du monitor Mastodon
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class MastodonSettings(BaseSettings):
    # Application
    APP_NAME: str = "Free Mobile Social Monitor"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Mastodon Configuration
    MASTODON_INSTANCE_URL: str = os.getenv("MASTODON_INSTANCE_URL", "https://mastodon.social")
    MASTODON_CLIENT_ID: Optional[str] = os.getenv("MASTODON_CLIENT_ID")
    MASTODON_CLIENT_SECRET: Optional[str] = os.getenv("MASTODON_CLIENT_SECRET")
    MASTODON_ACCESS_TOKEN: Optional[str] = os.getenv("MASTODON_ACCESS_TOKEN")
    
    # Monitoring Configuration
    MONITOR_HASHTAGS: List[str] = os.getenv("MASTODON_MONITOR_HASHTAGS", "Free,FreeMobile,SAVFree").split(",")
    MONITOR_MENTIONS: bool = os.getenv("MONITOR_MENTIONS", "true").lower() == "true"
    MONITOR_KEYWORDS: List[str] = [
        "free mobile", "freemobile", "free mobile", "free-mobile",
        "sav free", "support free", "aide free", "problème free",
        "facture free", "forfait free", "résiliation free"
    ]
    
    # Backend URLs
    BACKEND_API_URL: str = os.getenv("BACKEND_API_URL", "http://localhost:8000")
    AI_ENGINE_URL: str = os.getenv("AI_ENGINE_URL", "http://localhost:8001")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:8501")
    
    # Processing Configuration
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", 10))
    PROCESSING_DELAY: int = int(os.getenv("PROCESSING_DELAY", 5))  # secondes
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", 3))
    
    # Response Configuration
    AUTO_RESPOND: bool = os.getenv("AUTO_RESPOND", "true").lower() == "true"
    RESPONSE_DELAY: int = int(os.getenv("RESPONSE_DELAY", 30))  # secondes
    MAX_RESPONSES_PER_HOUR: int = int(os.getenv("MAX_RESPONSES_PER_HOUR", 10))
    
    # Free Mobile Links
    FREE_MOBILE_FAQ_URL: str = os.getenv("FREE_MOBILE_FAQ_URL", "https://mobile.free.fr/assistance/")
    FREE_MOBILE_ESPACE_CLIENT_URL: str = os.getenv("FREE_MOBILE_ESPACE_CLIENT_URL", "https://mobile.free.fr/moncompte/")
    FREE_MOBILE_CONTACT_URL: str = os.getenv("FREE_MOBILE_CONTACT_URL", "https://mobile.free.fr/assistance/contact.html")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_DEBUG_LOGS: bool = os.getenv("ENABLE_DEBUG_LOGS", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
    
    def is_configured(self) -> bool:
        """Vérifie si la configuration Mastodon est complète"""
        return all([
            self.MASTODON_INSTANCE_URL,
            self.MASTODON_CLIENT_ID,
            self.MASTODON_CLIENT_SECRET,
            self.MASTODON_ACCESS_TOKEN
        ])
    
    def get_hashtags_for_search(self) -> List[str]:
        """Retourne les hashtags formatés pour la recherche"""
        return [f"#{tag.strip()}" for tag in self.MONITOR_HASHTAGS if tag.strip()]
    
    def get_keywords_for_search(self) -> List[str]:
        """Retourne les mots-clés pour la recherche"""
        return [keyword.lower() for keyword in self.MONITOR_KEYWORDS]


settings = MastodonSettings()
