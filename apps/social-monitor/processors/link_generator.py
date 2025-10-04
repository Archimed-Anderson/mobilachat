"""
Générateur de liens de contact uniques
"""
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
from ..config.mastodon_config import settings

logger = logging.getLogger(__name__)


class LinkGenerator:
    def __init__(self):
        self.base_url = settings.FRONTEND_URL
        self.link_expiry_hours = 24  # Liens valides 24h
    
    def generate_contact_link(
        self, 
        mastodon_user: str, 
        post_id: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère un lien de contact unique pour un utilisateur Mastodon"""
        try:
            # Génération d'un token unique
            token = self._generate_unique_token(mastodon_user, post_id, context)
            
            # URL de contact avec token
            contact_url = f"{self.base_url}/?token={token}&source=mastodon"
            
            # Données de contexte à sauvegarder
            context_data = {
                "mastodon_user": mastodon_user,
                "post_id": post_id,
                "original_content": context.get("content", ""),
                "complaint_type": context.get("complaint_type", "general"),
                "urgency": context.get("urgency", "medium"),
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=self.link_expiry_hours)).isoformat(),
                "used": False,
                "response_sent": False
            }
            
            return {
                "token": token,
                "url": contact_url,
                "context": context_data,
                "expires_in_hours": self.link_expiry_hours
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du lien: {e}")
            return {
                "token": None,
                "url": None,
                "context": None,
                "expires_in_hours": 0
            }
    
    def _generate_unique_token(
        self, 
        mastodon_user: str, 
        post_id: str, 
        context: Dict[str, Any]
    ) -> str:
        """Génère un token unique basé sur les données du post"""
        # Données pour le hash
        data = f"{mastodon_user}:{post_id}:{datetime.now().isoformat()}:{uuid.uuid4()}"
        
        # Génération du hash
        hash_object = hashlib.sha256(data.encode())
        token = hash_object.hexdigest()[:16]  # 16 caractères
        
        return token
    
    def generate_response_message(
        self, 
        mastodon_user: str, 
        complaint_type: str, 
        urgency: str,
        contact_url: str
    ) -> str:
        """Génère un message de réponse personnalisé"""
        
        # Messages de base selon le type de réclamation
        base_messages = {
            "billing": "Nous comprenons votre préoccupation concernant la facturation.",
            "technical": "Nous sommes désolés pour les difficultés techniques que vous rencontrez.",
            "customer_service": "Nous nous excusons pour la qualité de notre service client.",
            "cancellation": "Nous comprenons votre souhait de résilier votre contrat.",
            "general": "Nous sommes désolés de constater votre mécontentement."
        }
        
        # Messages selon l'urgence
        urgency_messages = {
            "urgent": "Votre demande est prioritaire et sera traitée en urgence.",
            "high": "Votre demande sera traitée rapidement par notre équipe.",
            "medium": "Nous allons examiner votre demande attentivement.",
            "low": "Nous allons nous pencher sur votre demande."
        }
        
        # Construction du message
        base_message = base_messages.get(complaint_type, base_messages["general"])
        urgency_message = urgency_messages.get(urgency, urgency_messages["medium"])
        
        message = f"""Bonjour @{mastodon_user},

{base_message} {urgency_message}

Pour vous aider au mieux, nous vous invitons à nous contacter directement via notre support client : {contact_url}

Notre équipe se fera un plaisir de vous accompagner dans la résolution de votre problème.

Cordialement,
L'équipe Free Mobile 🆓"""
        
        return message
    
    def generate_escalation_message(
        self, 
        mastodon_user: str, 
        complaint_type: str,
        contact_url: str
    ) -> str:
        """Génère un message d'escalade pour les cas urgents"""
        
        message = f"""Bonjour @{mastodon_user},

Nous avons pris connaissance de votre message et nous comprenons votre frustration.

Votre demande a été immédiatement transmise à notre équipe de supervision qui va vous contacter dans les plus brefs délais.

En attendant, vous pouvez également nous contacter directement : {contact_url}

Nous nous excusons sincèrement pour les désagréments causés.

Cordialement,
L'équipe Free Mobile 🆓"""
        
        return message
    
    def generate_follow_up_message(
        self, 
        mastodon_user: str, 
        days_since_contact: int
    ) -> str:
        """Génère un message de suivi"""
        
        if days_since_contact == 1:
            message = f"""Bonjour @{mastodon_user},

Nous espérons que notre équipe a pu vous aider hier.

Si vous avez encore des questions ou si votre problème n'est pas résolu, n'hésitez pas à nous le faire savoir.

Cordialement,
L'équipe Free Mobile 🆓"""
        
        elif days_since_contact == 3:
            message = f"""Bonjour @{mastodon_user},

Nous souhaitons nous assurer que votre problème a été résolu.

Si ce n'est pas le cas, notre équipe reste à votre disposition pour vous accompagner.

Cordialement,
L'équipe Free Mobile 🆓"""
        
        else:
            message = f"""Bonjour @{mastodon_user},

Nous espérons que tout va bien de votre côté.

N'hésitez pas à nous contacter si vous avez besoin d'aide.

Cordialement,
L'équipe Free Mobile 🆓"""
        
        return message
    
    def validate_token(self, token: str) -> bool:
        """Valide un token de contact"""
        try:
            # Vérification basique du format
            if not token or len(token) != 16:
                return False
            
            # Vérification que c'est un hexadécimal
            int(token, 16)
            return True
            
        except ValueError:
            return False
    
    def get_link_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques des liens générés"""
        # Cette méthode pourrait être étendue pour récupérer les stats depuis la base de données
        return {
            "total_links_generated": 0,
            "active_links": 0,
            "expired_links": 0,
            "used_links": 0,
            "response_rate": 0.0
        }
    
    def cleanup_expired_links(self) -> int:
        """Nettoie les liens expirés"""
        # Cette méthode pourrait être étendue pour nettoyer la base de données
        return 0
    
    def get_contact_url_variants(self, base_url: str) -> Dict[str, str]:
        """Retourne différentes variantes d'URL de contact"""
        return {
            "main": base_url,
            "chat": f"{base_url}#chat",
            "support": f"{base_url}#support",
            "contact": f"{base_url}#contact",
            "mobile": base_url.replace("http://", "https://") if base_url.startswith("http://") else base_url
        }
    
    def generate_qr_code_data(self, contact_url: str) -> str:
        """Génère les données pour un QR code (à implémenter avec une lib QR)"""
        # Placeholder pour la génération de QR code
        return f"QR_CODE_DATA_FOR:{contact_url}"
    
    def get_link_analytics(self, token: str) -> Dict[str, Any]:
        """Retourne les analytics pour un lien spécifique"""
        # Cette méthode pourrait être étendue pour récupérer les analytics depuis la base de données
        return {
            "token": token,
            "created_at": None,
            "last_accessed": None,
            "access_count": 0,
            "response_sent": False,
            "satisfaction_score": None
        }


