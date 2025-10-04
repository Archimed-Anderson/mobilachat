"""
Répondeur automatique pour Mastodon
"""
import asyncio
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timedelta
from ..config.mastodon_config import settings
from ..processors.link_generator import LinkGenerator
from ..processors.complaint_detector import ComplaintDetector

logger = logging.getLogger(__name__)


class AutoResponder:
    def __init__(self):
        self.link_generator = LinkGenerator()
        self.complaint_detector = ComplaintDetector()
        self.response_count = 0
        self.last_response_time = None
        self.response_history = []
    
    async def process_post(
        self, 
        post: Dict[str, Any], 
        mastodon_client
    ) -> Optional[Dict[str, Any]]:
        """Traite un post et génère une réponse si nécessaire"""
        try:
            # Vérification des limites de taux
            if not self._can_respond():
                logger.warning("Limite de taux de réponse atteinte")
                return None
            
            # Détection de réclamation
            complaint_result = self.complaint_detector.detect_complaint(post.get("content", ""))
            
            if not complaint_result["is_complaint"]:
                logger.debug("Post non identifié comme réclamation")
                return None
            
            # Génération du lien de contact
            context = {
                "content": post.get("content", ""),
                "complaint_type": complaint_result["type"],
                "urgency": complaint_result["urgency"],
                "sentiment": complaint_result["sentiment"]
            }
            
            link_data = self.link_generator.generate_contact_link(
                mastodon_user=post.get("account", {}).get("username", ""),
                post_id=post.get("id", ""),
                context=context
            )
            
            if not link_data["token"]:
                logger.error("Impossible de générer le lien de contact")
                return None
            
            # Génération du message de réponse
            response_message = self._generate_response_message(
                post, 
                complaint_result, 
                link_data["url"]
            )
            
            # Envoi de la réponse
            response = await self._send_response(
                mastodon_client, 
                post, 
                response_message
            )
            
            if response:
                # Mise à jour des statistiques
                self._update_response_stats()
                
                # Sauvegarde de l'historique
                self._save_response_history(post, response, link_data)
                
                logger.info(f"Réponse envoyée pour le post {post.get('id')}")
                
                return {
                    "post_id": post.get("id"),
                    "response_id": response.get("id"),
                    "link_token": link_data["token"],
                    "complaint_type": complaint_result["type"],
                    "urgency": complaint_result["urgency"],
                    "sent_at": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement du post: {e}")
            return None
    
    def _can_respond(self) -> bool:
        """Vérifie si on peut envoyer une réponse"""
        # Vérification du nombre de réponses par heure
        if self.response_count >= settings.MAX_RESPONSES_PER_HOUR:
            return False
        
        # Vérification du délai entre les réponses
        if self.last_response_time:
            time_since_last = datetime.now() - self.last_response_time
            if time_since_last.total_seconds() < settings.RESPONSE_DELAY:
                return False
        
        return True
    
    def _generate_response_message(
        self, 
        post: Dict[str, Any], 
        complaint_result: Dict[str, Any], 
        contact_url: str
    ) -> str:
        """Génère le message de réponse approprié"""
        
        username = post.get("account", {}).get("username", "")
        complaint_type = complaint_result["type"]
        urgency = complaint_result["urgency"]
        
        # Message d'escalade pour les cas urgents
        if urgency == "urgent":
            return self.link_generator.generate_escalation_message(
                username, 
                complaint_type, 
                contact_url
            )
        
        # Message standard
        return self.link_generator.generate_response_message(
            username, 
            complaint_type, 
            urgency, 
            contact_url
        )
    
    async def _send_response(
        self, 
        mastodon_client, 
        original_post: Dict[str, Any], 
        message: str
    ) -> Optional[Dict[str, Any]]:
        """Envoie la réponse sur Mastodon"""
        try:
            # Préparation de la réponse
            response_data = {
                "status": message,
                "in_reply_to_id": original_post.get("id"),
                "visibility": "public"
            }
            
            # Envoi de la réponse
            response = await mastodon_client.status_post(**response_data)
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la réponse: {e}")
            return None
    
    def _update_response_stats(self):
        """Met à jour les statistiques de réponse"""
        self.response_count += 1
        self.last_response_time = datetime.now()
        
        # Reset du compteur toutes les heures
        if self.last_response_time.hour != datetime.now().hour:
            self.response_count = 0
    
    def _save_response_history(
        self, 
        post: Dict[str, Any], 
        response: Dict[str, Any], 
        link_data: Dict[str, Any]
    ):
        """Sauvegarde l'historique des réponses"""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "original_post": {
                "id": post.get("id"),
                "content": post.get("content", "")[:100] + "...",
                "username": post.get("account", {}).get("username", ""),
                "url": post.get("url", "")
            },
            "response": {
                "id": response.get("id"),
                "url": response.get("url", "")
            },
            "link_token": link_data["token"],
            "complaint_type": link_data["context"]["complaint_type"],
            "urgency": link_data["context"]["urgency"]
        }
        
        self.response_history.append(history_entry)
        
        # Limitation de l'historique
        if len(self.response_history) > 1000:
            self.response_history = self.response_history[-500:]
    
    async def send_follow_up(
        self, 
        mastodon_client, 
        original_post: Dict[str, Any], 
        days_since_contact: int
    ) -> Optional[Dict[str, Any]]:
        """Envoie un message de suivi"""
        try:
            username = original_post.get("account", {}).get("username", "")
            
            follow_up_message = self.link_generator.generate_follow_up_message(
                username, 
                days_since_contact
            )
            
            response = await self._send_response(
                mastodon_client, 
                original_post, 
                follow_up_message
            )
            
            if response:
                logger.info(f"Message de suivi envoyé pour le post {original_post.get('id')}")
                return response
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du suivi: {e}")
            return None
    
    def get_response_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques des réponses"""
        return {
            "total_responses": len(self.response_history),
            "responses_this_hour": self.response_count,
            "last_response_time": self.last_response_time.isoformat() if self.last_response_time else None,
            "can_respond": self._can_respond(),
            "response_rate_limit": settings.MAX_RESPONSES_PER_HOUR,
            "response_delay_seconds": settings.RESPONSE_DELAY
        }
    
    def get_response_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retourne l'historique des réponses"""
        return self.response_history[-limit:] if self.response_history else []
    
    def clear_response_history(self):
        """Efface l'historique des réponses"""
        self.response_history = []
        self.response_count = 0
        self.last_response_time = None
    
    def get_complaint_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques des réclamations traitées"""
        if not self.response_history:
            return {"total": 0, "by_type": {}, "by_urgency": {}}
        
        by_type = {}
        by_urgency = {}
        
        for entry in self.response_history:
            complaint_type = entry.get("complaint_type", "unknown")
            urgency = entry.get("urgency", "unknown")
            
            by_type[complaint_type] = by_type.get(complaint_type, 0) + 1
            by_urgency[urgency] = by_urgency.get(urgency, 0) + 1
        
        return {
            "total": len(self.response_history),
            "by_type": by_type,
            "by_urgency": by_urgency
        }
    
    def should_send_follow_up(self, post_id: str, days_since_contact: int) -> bool:
        """Détermine si un suivi doit être envoyé"""
        # Vérification si un suivi a déjà été envoyé
        for entry in self.response_history:
            if (entry.get("original_post", {}).get("id") == post_id and 
                "follow_up" in entry):
                return False
        
        # Envoi de suivi selon le délai
        return days_since_contact in [1, 3, 7]  # Suivi à 1, 3 et 7 jours


