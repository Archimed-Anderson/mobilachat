"""
Client API pour communiquer avec le backend
"""
import httpx
import asyncio
from typing import Optional, Dict, Any, List
import logging
from ..config.settings import settings

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
    
    async def send_message(
        self, 
        message: str, 
        conversation_id: Optional[str] = None,
        context_token: Optional[str] = None,
        user_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Envoie un message au chatbot"""
        url = f"{self.backend_url}/api/v1/chat/message"
        data = {
            "message": message,
            "conversation_id": conversation_id,
            "context_token": context_token,
            "user_info": user_info
        }
        
        return await self._make_request("POST", url, data=data)
    
    async def get_conversation_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Récupère les messages d'une conversation"""
        url = f"{self.backend_url}/api/v1/chat/conversation/{conversation_id}/messages"
        
        return await self._make_request("GET", url)
    
    async def get_tickets(
        self, 
        status: Optional[str] = None,
        priority: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """Récupère les tickets"""
        url = f"{self.backend_url}/api/v1/tickets"
        params = {
            "page": page,
            "size": size
        }
        
        if status:
            params["status"] = status
        if priority:
            params["priority"] = priority
        
        return await self._make_request("GET", url, params=params)
    
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
    
    async def get_ai_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques du moteur IA"""
        url = f"{self.ai_engine_url}/api/stats"
        
        return await self._make_request("GET", url)
    
    async def search_documents(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Recherche dans les documents"""
        url = f"{self.ai_engine_url}/api/search"
        params = {
            "query": query,
            "top_k": top_k
        }
        
        return await self._make_request("GET", url, params=params)
    
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


# Fonctions utilitaires pour Streamlit
def send_message_sync(
    message: str, 
    conversation_id: Optional[str] = None,
    context_token: Optional[str] = None,
    user_info: Optional[Dict] = None
) -> Dict[str, Any]:
    """Version synchrone de send_message pour Streamlit"""
    return asyncio.run(APIClient().send_message(
        message, conversation_id, context_token, user_info
    ))


def get_conversation_messages_sync(conversation_id: str) -> List[Dict[str, Any]]:
    """Version synchrone de get_conversation_messages pour Streamlit"""
    return asyncio.run(APIClient().get_conversation_messages(conversation_id))


def get_tickets_sync(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """Version synchrone de get_tickets pour Streamlit"""
    return asyncio.run(APIClient().get_tickets(status, priority, page, size))


def get_analytics_sync(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Version synchrone de get_analytics pour Streamlit"""
    return asyncio.run(APIClient().get_analytics(start_date, end_date))


def get_ai_stats_sync() -> Dict[str, Any]:
    """Version synchrone de get_ai_stats pour Streamlit"""
    return asyncio.run(APIClient().get_ai_stats())


def health_check_sync() -> Dict[str, Any]:
    """Version synchrone de health_check pour Streamlit"""
    return asyncio.run(APIClient().health_check())


# Instance globale
api_client = APIClient()


