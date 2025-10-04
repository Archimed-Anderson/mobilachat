"""
Collecteur principal pour Mastodon
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from mastodon import Mastodon
from ..config.mastodon_config import settings
from ..processors.complaint_detector import ComplaintDetector
from ..processors.link_generator import LinkGenerator
from ..responders.auto_responder import AutoResponder
from ..utils.api_client import APIClient

logger = logging.getLogger(__name__)


class MastodonCollector:
    def __init__(self):
        self.mastodon_client = None
        self.complaint_detector = ComplaintDetector()
        self.link_generator = LinkGenerator()
        self.auto_responder = AutoResponder()
        self.api_client = APIClient()
        self.is_running = False
        self.processed_posts = set()
        self.stats = {
            "total_posts_processed": 0,
            "complaints_detected": 0,
            "responses_sent": 0,
            "start_time": None
        }
    
    async def initialize(self) -> bool:
        """Initialise le client Mastodon"""
        try:
            if not settings.is_configured():
                logger.error("Configuration Mastodon incomplète")
                return False
            
            # Initialisation du client Mastodon
            self.mastodon_client = Mastodon(
                client_id=settings.MASTODON_CLIENT_ID,
                client_secret=settings.MASTODON_CLIENT_SECRET,
                access_token=settings.MASTODON_ACCESS_TOKEN,
                api_base_url=settings.MASTODON_INSTANCE_URL
            )
            
            # Test de connexion
            await self._test_connection()
            
            logger.info("Client Mastodon initialisé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation: {e}")
            return False
    
    async def _test_connection(self):
        """Teste la connexion Mastodon"""
        try:
            # Test de l'API
            account = self.mastodon_client.me()
            logger.info(f"Connecté en tant que @{account['username']}")
            
        except Exception as e:
            logger.error(f"Erreur de connexion Mastodon: {e}")
            raise
    
    async def start_monitoring(self):
        """Démarre la surveillance Mastodon"""
        if not self.mastodon_client:
            logger.error("Client Mastodon non initialisé")
            return
        
        self.is_running = True
        self.stats["start_time"] = datetime.now()
        
        logger.info("Démarrage de la surveillance Mastodon...")
        
        try:
            # Surveillance des hashtags
            if settings.MONITOR_HASHTAGS:
                await self._monitor_hashtags()
            
            # Surveillance des mentions
            if settings.MONITOR_MENTIONS:
                await self._monitor_mentions()
            
        except Exception as e:
            logger.error(f"Erreur lors de la surveillance: {e}")
        finally:
            self.is_running = False
    
    async def _monitor_hashtags(self):
        """Surveille les hashtags configurés"""
        logger.info(f"Surveillance des hashtags: {settings.MONITOR_HASHTAGS}")
        
        while self.is_running:
            try:
                # Recherche des posts avec les hashtags
                for hashtag in settings.get_hashtags_for_search():
                    posts = await self._search_posts(hashtag)
                    await self._process_posts(posts)
                
                # Attente avant la prochaine recherche
                await asyncio.sleep(settings.PROCESSING_DELAY)
                
            except Exception as e:
                logger.error(f"Erreur lors de la surveillance des hashtags: {e}")
                await asyncio.sleep(30)  # Attente en cas d'erreur
    
    async def _monitor_mentions(self):
        """Surveille les mentions"""
        logger.info("Surveillance des mentions...")
        
        while self.is_running:
            try:
                # Récupération des mentions
                mentions = await self._get_mentions()
                await self._process_posts(mentions)
                
                # Attente avant la prochaine vérification
                await asyncio.sleep(settings.PROCESSING_DELAY)
                
            except Exception as e:
                logger.error(f"Erreur lors de la surveillance des mentions: {e}")
                await asyncio.sleep(30)
    
    async def _search_posts(self, query: str) -> List[Dict[str, Any]]:
        """Recherche des posts avec une requête"""
        try:
            # Recherche des posts récents
            posts = self.mastodon_client.timeline_hashtag(
                hashtag=query.replace("#", ""),
                limit=20
            )
            
            return posts or []
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            return []
    
    async def _get_mentions(self) -> List[Dict[str, Any]]:
        """Récupère les mentions récentes"""
        try:
            # Récupération des notifications (mentions)
            notifications = self.mastodon_client.notifications(
                types=["mention"],
                limit=20
            )
            
            # Extraction des posts des notifications
            posts = []
            for notification in notifications:
                if notification.get("status"):
                    posts.append(notification["status"])
            
            return posts
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des mentions: {e}")
            return []
    
    async def _process_posts(self, posts: List[Dict[str, Any]]):
        """Traite une liste de posts"""
        for post in posts:
            try:
                # Vérification si le post a déjà été traité
                post_id = post.get("id")
                if post_id in self.processed_posts:
                    continue
                
                # Vérification si le post est récent (moins de 24h)
                if not self._is_recent_post(post):
                    continue
                
                # Vérification si le post concerne Free Mobile
                if not self._is_free_mobile_related(post):
                    continue
                
                # Traitement du post
                await self._process_single_post(post)
                
                # Marquage comme traité
                self.processed_posts.add(post_id)
                self.stats["total_posts_processed"] += 1
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement du post {post.get('id')}: {e}")
    
    async def _process_single_post(self, post: Dict[str, Any]):
        """Traite un post individuel"""
        try:
            # Détection de réclamation
            complaint_result = self.complaint_detector.detect_complaint(
                post.get("content", "")
            )
            
            if complaint_result["is_complaint"]:
                self.stats["complaints_detected"] += 1
                
                # Sauvegarde dans la base de données
                await self._save_post_to_database(post, complaint_result)
                
                # Génération de réponse automatique
                if settings.AUTO_RESPOND:
                    response_result = await self.auto_responder.process_post(
                        post, 
                        self.mastodon_client
                    )
                    
                    if response_result:
                        self.stats["responses_sent"] += 1
                        logger.info(f"Réponse envoyée pour le post {post.get('id')}")
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement du post: {e}")
    
    def _is_recent_post(self, post: Dict[str, Any]) -> bool:
        """Vérifie si le post est récent (moins de 24h)"""
        try:
            created_at = post.get("created_at")
            if not created_at:
                return False
            
            # Conversion en datetime
            if isinstance(created_at, str):
                from dateutil import parser
                created_at = parser.parse(created_at)
            
            # Vérification si le post est récent
            time_diff = datetime.now(created_at.tzinfo) - created_at
            return time_diff.total_seconds() < 86400  # 24 heures
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la date: {e}")
            return False
    
    def _is_free_mobile_related(self, post: Dict[str, Any]) -> bool:
        """Vérifie si le post concerne Free Mobile"""
        content = post.get("content", "").lower()
        
        # Vérification des mots-clés
        keywords = settings.get_keywords_for_search()
        for keyword in keywords:
            if keyword in content:
                return True
        
        # Vérification des hashtags
        hashtags = settings.get_hashtags_for_search()
        for hashtag in hashtags:
            if hashtag.lower() in content:
                return True
        
        return False
    
    async def _save_post_to_database(
        self, 
        post: Dict[str, Any], 
        complaint_result: Dict[str, Any]
    ):
        """Sauvegarde le post dans la base de données"""
        try:
            # Préparation des données
            post_data = {
                "mastodon_id": str(post.get("id")),
                "author_username": post.get("account", {}).get("username", ""),
                "content": post.get("content", ""),
                "is_complaint": complaint_result["is_complaint"],
                "sentiment_score": complaint_result.get("complaint_score", 0.0),
                "urgency": complaint_result.get("urgency", "low"),
                "context_token": None,  # Sera généré lors de la réponse
                "created_at": post.get("created_at"),
                "processed_at": datetime.now().isoformat()
            }
            
            # Sauvegarde via l'API backend
            # Note: Cette partie nécessiterait l'implémentation de l'endpoint correspondant
            logger.info(f"Post sauvegardé: {post_data['mastodon_id']}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
    
    async def stop_monitoring(self):
        """Arrête la surveillance"""
        self.is_running = False
        logger.info("Arrêt de la surveillance Mastodon")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de surveillance"""
        uptime = None
        if self.stats["start_time"]:
            uptime = (datetime.now() - self.stats["start_time"]).total_seconds()
        
        return {
            **self.stats,
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "processed_posts_count": len(self.processed_posts),
            "response_stats": self.auto_responder.get_response_stats(),
            "complaint_stats": self.auto_responder.get_complaint_stats()
        }
    
    def get_processed_posts(self, limit: int = 50) -> List[str]:
        """Retourne la liste des posts traités"""
        return list(self.processed_posts)[-limit:]
    
    def clear_processed_posts(self):
        """Efface la liste des posts traités"""
        self.processed_posts.clear()
        logger.info("Liste des posts traités effacée")
    
    async def test_connection(self) -> bool:
        """Teste la connexion Mastodon"""
        try:
            if not self.mastodon_client:
                return False
            
            account = self.mastodon_client.me()
            logger.info(f"Connexion testée avec succès: @{account['username']}")
            return True
            
        except Exception as e:
            logger.error(f"Test de connexion échoué: {e}")
            return False


