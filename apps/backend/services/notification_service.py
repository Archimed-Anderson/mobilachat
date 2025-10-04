"""
Service de notifications pour les alertes et événements
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import json
from ..core.redis_client import redis_client
from ..utils.api_client import APIClient

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    ALERT = "alert"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"
    ERROR = "error"


class NotificationChannel(Enum):
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    DASHBOARD = "dashboard"


class NotificationService:
    def __init__(self):
        self.api_client = APIClient()
        self.notification_queue = []
        self.subscribers = {}
        self.rate_limits = {
            "email": {"limit": 10, "window": 3600},  # 10 emails par heure
            "slack": {"limit": 50, "window": 3600},  # 50 messages Slack par heure
            "webhook": {"limit": 100, "window": 3600}  # 100 webhooks par heure
        }
        self.sent_notifications = {}
    
    async def send_notification(
        self,
        notification_type: NotificationType,
        title: str,
        message: str,
        channels: List[NotificationChannel],
        data: Optional[Dict[str, Any]] = None,
        priority: str = "normal"
    ) -> bool:
        """Envoie une notification sur les canaux spécifiés"""
        try:
            notification = {
                "id": self._generate_notification_id(),
                "type": notification_type.value,
                "title": title,
                "message": message,
                "channels": [ch.value for ch in channels],
                "data": data or {},
                "priority": priority,
                "timestamp": datetime.now().isoformat(),
                "sent": False
            }
            
            # Vérification des limites de taux
            if not await self._check_rate_limits(channels):
                logger.warning("Limites de taux atteintes, notification mise en queue")
                self.notification_queue.append(notification)
                return False
            
            # Envoi sur chaque canal
            results = []
            for channel in channels:
                result = await self._send_to_channel(notification, channel)
                results.append(result)
            
            # Mise à jour du statut
            notification["sent"] = all(results)
            notification["results"] = dict(zip([ch.value for ch in channels], results))
            
            # Sauvegarde de la notification
            await self._save_notification(notification)
            
            # Mise à jour des compteurs
            await self._update_rate_limits(channels)
            
            logger.info(f"Notification envoyée: {title}")
            return notification["sent"]
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification: {e}")
            return False
    
    async def _send_to_channel(
        self, 
        notification: Dict[str, Any], 
        channel: NotificationChannel
    ) -> bool:
        """Envoie une notification sur un canal spécifique"""
        try:
            if channel == NotificationChannel.DASHBOARD:
                return await self._send_to_dashboard(notification)
            elif channel == NotificationChannel.EMAIL:
                return await self._send_email(notification)
            elif channel == NotificationChannel.SLACK:
                return await self._send_slack(notification)
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook(notification)
            else:
                logger.warning(f"Canal non supporté: {channel}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi sur le canal {channel}: {e}")
            return False
    
    async def _send_to_dashboard(self, notification: Dict[str, Any]) -> bool:
        """Envoie une notification au dashboard"""
        try:
            # Sauvegarde dans Redis pour le dashboard
            notification_key = f"dashboard_notification:{notification['id']}"
            await redis_client.client.setex(
                notification_key,
                86400,  # Expire dans 24 heures
                json.dumps(notification)
            )
            
            # Ajout à la liste des notifications récentes
            await redis_client.client.lpush(
                "recent_notifications",
                json.dumps(notification)
            )
            
            # Limitation à 100 notifications récentes
            await redis_client.client.ltrim("recent_notifications", 0, 99)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi au dashboard: {e}")
            return False
    
    async def _send_email(self, notification: Dict[str, Any]) -> bool:
        """Envoie une notification par email"""
        try:
            # Simulation d'envoi d'email
            # Dans un vrai système, utiliser un service comme SendGrid, SES, etc.
            
            email_data = {
                "to": "admin@freemobile.com",
                "subject": f"[Free Mobile Bot] {notification['title']}",
                "body": notification['message'],
                "priority": notification['priority']
            }
            
            # Sauvegarde pour traitement ultérieur
            email_key = f"email_queue:{notification['id']}"
            await redis_client.client.setex(
                email_key,
                3600,  # Expire dans 1 heure
                json.dumps(email_data)
            )
            
            logger.info(f"Email mis en queue: {notification['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email: {e}")
            return False
    
    async def _send_slack(self, notification: Dict[str, Any]) -> bool:
        """Envoie une notification sur Slack"""
        try:
            # Configuration Slack (à adapter selon votre setup)
            slack_webhook_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
            
            slack_message = {
                "text": f"*{notification['title']}*",
                "attachments": [
                    {
                        "color": self._get_slack_color(notification['type']),
                        "fields": [
                            {
                                "title": "Message",
                                "value": notification['message'],
                                "short": False
                            },
                            {
                                "title": "Priorité",
                                "value": notification['priority'],
                                "short": True
                            },
                            {
                                "title": "Timestamp",
                                "value": notification['timestamp'],
                                "short": True
                            }
                        ]
                    }
                ]
            }
            
            # Sauvegarde pour traitement ultérieur
            slack_key = f"slack_queue:{notification['id']}"
            await redis_client.client.setex(
                slack_key,
                3600,  # Expire dans 1 heure
                json.dumps(slack_message)
            )
            
            logger.info(f"Message Slack mis en queue: {notification['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi sur Slack: {e}")
            return False
    
    async def _send_webhook(self, notification: Dict[str, Any]) -> bool:
        """Envoie une notification via webhook"""
        try:
            # Configuration webhook (à adapter selon votre setup)
            webhook_url = "https://your-webhook-endpoint.com/notifications"
            
            webhook_data = {
                "notification": notification,
                "source": "free-mobile-chatbot",
                "timestamp": datetime.now().isoformat()
            }
            
            # Sauvegarde pour traitement ultérieur
            webhook_key = f"webhook_queue:{notification['id']}"
            await redis_client.client.setex(
                webhook_key,
                3600,  # Expire dans 1 heure
                json.dumps(webhook_data)
            )
            
            logger.info(f"Webhook mis en queue: {notification['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du webhook: {e}")
            return False
    
    def _get_slack_color(self, notification_type: str) -> str:
        """Retourne la couleur Slack selon le type de notification"""
        colors = {
            "alert": "danger",
            "warning": "warning",
            "info": "good",
            "success": "good",
            "error": "danger"
        }
        return colors.get(notification_type, "good")
    
    async def _check_rate_limits(self, channels: List[NotificationChannel]) -> bool:
        """Vérifie les limites de taux pour les canaux"""
        try:
            for channel in channels:
                channel_name = channel.value
                if channel_name not in self.rate_limits:
                    continue
                
                limit = self.rate_limits[channel_name]["limit"]
                window = self.rate_limits[channel_name]["window"]
                
                # Vérification du nombre de notifications envoyées
                sent_count = await self._get_sent_count(channel_name, window)
                
                if sent_count >= limit:
                    logger.warning(f"Limite de taux atteinte pour {channel_name}: {sent_count}/{limit}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des limites: {e}")
            return True  # En cas d'erreur, autoriser l'envoi
    
    async def _get_sent_count(self, channel: str, window_seconds: int) -> int:
        """Récupère le nombre de notifications envoyées dans la fenêtre"""
        try:
            cutoff_time = datetime.now() - timedelta(seconds=window_seconds)
            cutoff_timestamp = cutoff_time.timestamp()
            
            # Comptage des notifications envoyées
            pattern = f"notification_sent:{channel}:*"
            keys = await redis_client.client.keys(pattern)
            
            count = 0
            for key in keys:
                timestamp = await redis_client.client.get(key)
                if timestamp and float(timestamp) > cutoff_timestamp:
                    count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Erreur lors du comptage des notifications: {e}")
            return 0
    
    async def _update_rate_limits(self, channels: List[NotificationChannel]):
        """Met à jour les compteurs de limites de taux"""
        try:
            current_timestamp = datetime.now().timestamp()
            
            for channel in channels:
                channel_name = channel.value
                if channel_name not in self.rate_limits:
                    continue
                
                # Enregistrement de l'envoi
                key = f"notification_sent:{channel_name}:{current_timestamp}"
                await redis_client.client.setex(key, 3600, current_timestamp)
                
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des limites: {e}")
    
    async def _save_notification(self, notification: Dict[str, Any]):
        """Sauvegarde une notification"""
        try:
            notification_key = f"notification:{notification['id']}"
            await redis_client.client.setex(
                notification_key,
                86400,  # Expire dans 24 heures
                json.dumps(notification)
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la notification: {e}")
    
    def _generate_notification_id(self) -> str:
        """Génère un ID unique pour la notification"""
        return f"notif_{datetime.now().strftime('%Y%m%d%H%M%S')}_{id(self) % 10000}"
    
    async def get_recent_notifications(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère les notifications récentes"""
        try:
            notifications = await redis_client.client.lrange(
                "recent_notifications",
                0,
                limit - 1
            )
            
            return [json.loads(notif) for notif in notifications]
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des notifications: {e}")
            return []
    
    async def process_notification_queue(self):
        """Traite la queue des notifications en attente"""
        try:
            while self.notification_queue:
                notification = self.notification_queue.pop(0)
                
                # Vérification des limites de taux
                if await self._check_rate_limits(
                    [NotificationChannel(ch) for ch in notification['channels']]
                ):
                    # Retry de l'envoi
                    await self.send_notification(
                        NotificationType(notification['type']),
                        notification['title'],
                        notification['message'],
                        [NotificationChannel(ch) for ch in notification['channels']],
                        notification['data'],
                        notification['priority']
                    )
                else:
                    # Remise en queue
                    self.notification_queue.append(notification)
                    break
                    
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la queue: {e}")
    
    async def send_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "warning",
        data: Optional[Dict[str, Any]] = None
    ):
        """Envoie une alerte"""
        notification_type = NotificationType.ALERT if severity == "error" else NotificationType.WARNING
        
        return await self.send_notification(
            notification_type,
            f"Alerte {alert_type}",
            message,
            [NotificationChannel.DASHBOARD, NotificationChannel.SLACK],
            data,
            "high"
        )
    
    async def send_system_notification(
        self,
        message: str,
        notification_type: NotificationType = NotificationType.INFO
    ):
        """Envoie une notification système"""
        return await self.send_notification(
            notification_type,
            "Notification Système",
            message,
            [NotificationChannel.DASHBOARD],
            priority="normal"
        )


# Instance globale
notification_service = NotificationService()


