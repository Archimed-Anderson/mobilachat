"""
Client API pour le social monitor
"""
import httpx
import asyncio
from typing import Dict, Any, Optional, List
import logging
from ..config.mastodon_config import settings

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self):
        self.backend_url = settings.BACKEND_API_URL
        self.ai_engine_url = settings.AI_ENGINE_URL
        self.timeout = 30
    
    async def _make_request(
        self, 
        method: str, 
        url: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Effectue une requête HTTP"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params
                )
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            logger.error(f"Timeout lors de la requête {method} {url}")
            raise Exception("La requête a expiré. Veuillez réessayer.")
        except httpx.HTTPStatusError as e:
            logger.error(f"Erreur HTTP {e.response.status_code}: {e.response.text}")
            raise Exception(f"Erreur du serveur: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Erreur lors de la requête {method} {url}: {e}")
            raise Exception(f"Erreur de communication: {str(e)}")
    
    async def save_mastodon_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sauvegarde un post Mastodon dans la base de données"""
        url = f"{self.backend_url}/api/v1/mastodon/posts"
        
        return await self._make_request("POST", url, data=post_data)
    
    async def get_mastodon_posts(
        self, 
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Récupère les posts Mastodon"""
        url = f"{self.backend_url}/api/v1/mastodon/posts"
        params = {
            "limit": limit,
            "offset": offset
        }
        
        return await self._make_request("GET", url, params=params)
    
    async def create_conversation_from_mastodon(
        self, 
        post_data: Dict[str, Any],
        context_token: str
    ) -> Dict[str, Any]:
        """Crée une conversation à partir d'un post Mastodon"""
        url = f"{self.backend_url}/api/v1/chat/conversation"
        
        conversation_data = {
            "source": "mastodon",
            "mastodon_user": post_data.get("author_username"),
            "mastodon_post_id": post_data.get("mastodon_id"),
            "context_token": context_token
        }
        
        return await self._make_request("POST", url, data=conversation_data)
    
    async def send_ai_analysis(
        self, 
        content: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Envoie du contenu pour analyse IA"""
        url = f"{self.ai_engine_url}/api/generate"
        
        data = {
            "message": content,
            "conversation_id": context.get("conversation_id"),
            "context_token": context.get("context_token"),
            "user_context": context
        }
        
        return await self._make_request("POST", url, data=data)
    
    async def get_ai_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques du moteur IA"""
        url = f"{self.ai_engine_url}/api/stats"
        
        return await self._make_request("GET", url)
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérifie la santé des services"""
        try:
            # Vérification du backend
            backend_health = await self._make_request("GET", f"{self.backend_url}/health")
            
            # Vérification du moteur IA
            ai_health = await self._make_request("GET", f"{self.ai_engine_url}/health")
            
            return {
                "backend": backend_health,
                "ai_engine": ai_health,
                "overall": "healthy"
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "backend": {"status": "unhealthy"},
                "ai_engine": {"status": "unhealthy"},
                "overall": "unhealthy",
                "error": str(e)
            }
    
    async def log_activity(
        self, 
        activity_type: str, 
        data: Dict[str, Any]
    ) -> bool:
        """Enregistre une activité"""
        try:
            url = f"{self.backend_url}/api/v1/analytics/events"
            
            event_data = {
                "event_type": activity_type,
                "data": data,
                "timestamp": data.get("timestamp")
            }
            
            await self._make_request("POST", url, data=event_data)
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'activité: {e}")
            return False
    
    async def get_analytics(
        self, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Récupère les analytics"""
        url = f"{self.backend_url}/api/v1/analytics"
        params = {}
        
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        return await self._make_request("GET", url, params=params)
    
    async def update_post_status(
        self, 
        post_id: str, 
        status: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Met à jour le statut d'un post"""
        try:
            url = f"{self.backend_url}/api/v1/mastodon/posts/{post_id}"
            
            data = {
                "status": status,
                "metadata": metadata or {}
            }
            
            await self._make_request("PUT", url, data=data)
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du statut: {e}")
            return False
    
    async def get_response_templates(self) -> List[Dict[str, Any]]:
        """Récupère les modèles de réponse"""
        try:
            url = f"{self.backend_url}/api/v1/mastodon/templates"
            return await self._make_request("GET", url)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des modèles: {e}")
            return []
    
    async def report_error(
        self, 
        error_type: str, 
        error_message: str,
        context: Dict[str, Any]
    ) -> bool:
        """Signale une erreur"""
        try:
            url = f"{self.backend_url}/api/v1/errors"
            
            error_data = {
                "error_type": error_type,
                "error_message": error_message,
                "context": context,
                "timestamp": context.get("timestamp")
            }
            
            await self._make_request("POST", url, data=error_data)
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du signalement d'erreur: {e}")
            return False


# Fonctions utilitaires pour l'utilisation synchrone
def save_mastodon_post_sync(post_data: Dict[str, Any]) -> Dict[str, Any]:
    """Version synchrone de save_mastodon_post"""
    return asyncio.run(APIClient().save_mastodon_post(post_data))


def get_mastodon_posts_sync(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Version synchrone de get_mastodon_posts"""
    return asyncio.run(APIClient().get_mastodon_posts(limit, offset))


def health_check_sync() -> Dict[str, Any]:
    """Version synchrone de health_check"""
    return asyncio.run(APIClient().health_check())


# Instance globale
api_client = APIClient()


