"""
Client Redis pour le cache et les sessions
"""
import redis.asyncio as redis
import json
from typing import Optional, Any, Dict
from .config import settings


class RedisClient:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connexion à Redis"""
        self.redis = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def disconnect(self):
        """Déconnexion de Redis"""
        if self.redis:
            await self.redis.close()
    
    async def set_value(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> bool:
        """Stocke une valeur avec expiration optionnelle"""
        if not self.redis:
            await self.connect()
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        return await self.redis.set(key, value, ex=expire)
    
    async def get_value(self, key: str) -> Optional[Any]:
        """Récupère une valeur"""
        if not self.redis:
            await self.connect()
        
        value = await self.redis.get(key)
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    
    async def delete_value(self, key: str) -> bool:
        """Supprime une valeur"""
        if not self.redis:
            await self.connect()
        
        return await self.redis.delete(key) == 1
    
    async def exists(self, key: str) -> bool:
        """Vérifie si une clé existe"""
        if not self.redis:
            await self.connect()
        
        return await self.redis.exists(key) == 1
    
    async def set_context(self, token: str, context: dict, expire: int = 86400):
        """Stocke un contexte de conversation (24h par défaut)"""
        await self.set_value(f"context:{token}", context, expire)
    
    async def get_context(self, token: str) -> Optional[dict]:
        """Récupère un contexte de conversation"""
        return await self.get_value(f"context:{token}")
    
    async def set_rate_limit(
        self, 
        key: str, 
        limit: int, 
        window: int = 60
    ) -> bool:
        """Gère le rate limiting"""
        if not self.redis:
            await self.connect()
        
        current = await self.redis.get(key)
        if current is None:
            await self.redis.setex(key, window, 1)
            return True
        
        if int(current) < limit:
            await self.redis.incr(key)
            return True
        
        return False


# Instance globale
redis_client = RedisClient()


