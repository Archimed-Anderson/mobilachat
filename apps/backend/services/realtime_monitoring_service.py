"""
Service de monitoring en temps réel
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import json
from ..core.redis_client import redis_client
from ..models.conversation import Conversation, Message
from ..models.ticket import Ticket
from ..models.mastodon_post import MastodonPost

logger = logging.getLogger(__name__)


class RealtimeMonitoringService:
    def __init__(self, db: Session):
        self.db = db
        self.monitoring_active = False
        self.metrics_cache = {}
        self.alert_thresholds = {
            "high_response_time": 5.0,  # minutes
            "low_satisfaction": 3.0,    # score sur 5
            "high_escalation_rate": 20.0,  # pourcentage
            "high_ticket_volume": 50,   # tickets par heure
            "system_error_rate": 5.0    # pourcentage
        }
    
    async def start_monitoring(self):
        """Démarre le monitoring en temps réel"""
        self.monitoring_active = True
        logger.info("🔄 Démarrage du monitoring en temps réel")
        
        try:
            while self.monitoring_active:
                # Collecte des métriques
                await self._collect_metrics()
                
                # Vérification des alertes
                await self._check_alerts()
                
                # Mise à jour du cache Redis
                await self._update_redis_cache()
                
                # Attente avant la prochaine collecte
                await asyncio.sleep(30)  # Collecte toutes les 30 secondes
                
        except Exception as e:
            logger.error(f"Erreur lors du monitoring: {e}")
        finally:
            self.monitoring_active = False
    
    async def stop_monitoring(self):
        """Arrête le monitoring"""
        self.monitoring_active = False
        logger.info("🛑 Arrêt du monitoring en temps réel")
    
    async def _collect_metrics(self):
        """Collecte les métriques en temps réel"""
        try:
            now = datetime.now()
            last_5min = now - timedelta(minutes=5)
            last_hour = now - timedelta(hours=1)
            
            # Métriques des conversations
            conversations_5min = self.db.query(Conversation).filter(
                Conversation.created_at >= last_5min
            ).count()
            
            conversations_hour = self.db.query(Conversation).filter(
                Conversation.created_at >= last_hour
            ).count()
            
            # Métriques des messages
            messages_5min = self.db.query(Message).filter(
                Message.created_at >= last_5min
            ).count()
            
            messages_hour = self.db.query(Message).filter(
                Message.created_at >= last_hour
            ).count()
            
            # Métriques des tickets
            open_tickets = self.db.query(Ticket).filter(
                Ticket.status.in_(['OPEN', 'IN_PROGRESS'])
            ).count()
            
            tickets_5min = self.db.query(Ticket).filter(
                Ticket.created_at >= last_5min
            ).count()
            
            tickets_hour = self.db.query(Ticket).filter(
                Ticket.created_at >= last_hour
            ).count()
            
            # Métriques Mastodon
            mastodon_posts_5min = self.db.query(MastodonPost).filter(
                MastodonPost.created_at >= last_5min
            ).count()
            
            mastodon_posts_hour = self.db.query(MastodonPost).filter(
                MastodonPost.created_at >= last_hour
            ).count()
            
            # Temps de réponse moyen (dernière heure)
            avg_response_time = await self._calculate_avg_response_time(last_hour, now)
            
            # Taux d'escalade (dernière heure)
            escalated_conversations = self.db.query(Conversation).filter(
                and_(
                    Conversation.needs_escalation == True,
                    Conversation.created_at >= last_hour
                )
            ).count()
            
            escalation_rate = (escalated_conversations / conversations_hour * 100) if conversations_hour > 0 else 0
            
            # Mise à jour du cache
            self.metrics_cache = {
                "timestamp": now.isoformat(),
                "conversations": {
                    "last_5min": conversations_5min,
                    "last_hour": conversations_hour,
                    "total_open": open_tickets
                },
                "messages": {
                    "last_5min": messages_5min,
                    "last_hour": messages_hour
                },
                "tickets": {
                    "last_5min": tickets_5min,
                    "last_hour": tickets_hour,
                    "open_count": open_tickets
                },
                "mastodon": {
                    "last_5min": mastodon_posts_5min,
                    "last_hour": mastodon_posts_hour
                },
                "performance": {
                    "avg_response_time": avg_response_time,
                    "escalation_rate": escalation_rate
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des métriques: {e}")
    
    async def _calculate_avg_response_time(self, start_time: datetime, end_time: datetime) -> float:
        """Calcule le temps de réponse moyen"""
        try:
            # Récupération des messages utilisateur
            user_messages = self.db.query(Message).filter(
                and_(
                    Message.role == 'user',
                    Message.created_at >= start_time,
                    Message.created_at <= end_time
                )
            ).order_by(Message.created_at).all()
            
            response_times = []
            
            for user_msg in user_messages:
                # Recherche de la réponse suivante
                next_response = self.db.query(Message).filter(
                    and_(
                        Message.conversation_id == user_msg.conversation_id,
                        Message.role == 'assistant',
                        Message.created_at > user_msg.created_at
                    )
                ).order_by(Message.created_at).first()
                
                if next_response:
                    response_time = (next_response.created_at - user_msg.created_at).total_seconds() / 60
                    response_times.append(response_time)
            
            return sum(response_times) / len(response_times) if response_times else 0
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul du temps de réponse: {e}")
            return 0.0
    
    async def _check_alerts(self):
        """Vérifie les alertes"""
        try:
            alerts = []
            
            # Vérification du temps de réponse
            if self.metrics_cache.get("performance", {}).get("avg_response_time", 0) > self.alert_thresholds["high_response_time"]:
                alerts.append({
                    "type": "high_response_time",
                    "message": f"Temps de réponse élevé: {self.metrics_cache['performance']['avg_response_time']:.1f} min",
                    "severity": "warning",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Vérification du taux d'escalade
            escalation_rate = self.metrics_cache.get("performance", {}).get("escalation_rate", 0)
            if escalation_rate > self.alert_thresholds["high_escalation_rate"]:
                alerts.append({
                    "type": "high_escalation_rate",
                    "message": f"Taux d'escalade élevé: {escalation_rate:.1f}%",
                    "severity": "warning",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Vérification du volume de tickets
            tickets_hour = self.metrics_cache.get("tickets", {}).get("last_hour", 0)
            if tickets_hour > self.alert_thresholds["high_ticket_volume"]:
                alerts.append({
                    "type": "high_ticket_volume",
                    "message": f"Volume de tickets élevé: {tickets_hour} tickets/heure",
                    "severity": "info",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Sauvegarde des alertes dans Redis
            if alerts:
                await self._save_alerts(alerts)
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des alertes: {e}")
    
    async def _save_alerts(self, alerts: List[Dict[str, Any]]):
        """Sauvegarde les alertes dans Redis"""
        try:
            for alert in alerts:
                alert_key = f"alert:{alert['type']}:{datetime.now().strftime('%Y%m%d%H%M%S')}"
                await redis_client.client.setex(
                    alert_key,
                    3600,  # Expire dans 1 heure
                    json.dumps(alert)
                )
            
            logger.info(f"🚨 {len(alerts)} alertes sauvegardées")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des alertes: {e}")
    
    async def _update_redis_cache(self):
        """Met à jour le cache Redis avec les métriques"""
        try:
            # Sauvegarde des métriques en temps réel
            await redis_client.client.setex(
                "realtime_metrics",
                60,  # Expire dans 1 minute
                json.dumps(self.metrics_cache)
            )
            
            # Sauvegarde des métriques par heure
            hour_key = f"hourly_metrics:{datetime.now().strftime('%Y%m%d%H')}"
            await redis_client.client.setex(
                hour_key,
                86400,  # Expire dans 24 heures
                json.dumps(self.metrics_cache)
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du cache Redis: {e}")
    
    async def get_realtime_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques en temps réel"""
        try:
            # Récupération depuis Redis
            cached_metrics = await redis_client.client.get("realtime_metrics")
            
            if cached_metrics:
                return json.loads(cached_metrics)
            else:
                # Fallback vers le cache local
                return self.metrics_cache
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des métriques: {e}")
            return {}
    
    async def get_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère les alertes récentes"""
        try:
            # Recherche des clés d'alertes
            alert_keys = await redis_client.client.keys("alert:*")
            
            alerts = []
            for key in alert_keys[:limit]:
                alert_data = await redis_client.client.get(key)
                if alert_data:
                    alerts.append(json.loads(alert_data))
            
            # Tri par timestamp décroissant
            alerts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des alertes: {e}")
            return []
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Récupère la santé du système"""
        try:
            # Vérification de la base de données
            db_health = await self._check_database_health()
            
            # Vérification de Redis
            redis_health = await self._check_redis_health()
            
            # Vérification des services externes
            external_health = await self._check_external_services()
            
            # Calcul du score de santé global
            health_score = self._calculate_health_score(db_health, redis_health, external_health)
            
            return {
                "overall_status": "healthy" if health_score >= 80 else "degraded" if health_score >= 60 else "unhealthy",
                "health_score": health_score,
                "database": db_health,
                "redis": redis_health,
                "external_services": external_health,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la santé: {e}")
            return {
                "overall_status": "unhealthy",
                "health_score": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Vérifie la santé de la base de données"""
        try:
            # Test de connexion
            self.db.execute("SELECT 1")
            
            # Vérification des tables principales
            tables = ["conversations", "messages", "tickets", "users"]
            table_status = {}
            
            for table in tables:
                try:
                    result = self.db.execute(f"SELECT COUNT(*) FROM {table}")
                    count = result.scalar()
                    table_status[table] = {"status": "healthy", "count": count}
                except Exception as e:
                    table_status[table] = {"status": "error", "error": str(e)}
            
            return {
                "status": "healthy",
                "tables": table_status
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _check_redis_health(self) -> Dict[str, Any]:
        """Vérifie la santé de Redis"""
        try:
            # Test de connexion
            await redis_client.client.ping()
            
            # Vérification de l'espace mémoire
            info = await redis_client.client.info("memory")
            used_memory = info.get("used_memory", 0)
            max_memory = info.get("maxmemory", 0)
            
            memory_usage = (used_memory / max_memory * 100) if max_memory > 0 else 0
            
            return {
                "status": "healthy",
                "memory_usage_percent": memory_usage,
                "used_memory": used_memory
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _check_external_services(self) -> Dict[str, Any]:
        """Vérifie la santé des services externes"""
        # Simulation de vérification des services externes
        return {
            "ai_engine": {"status": "healthy"},
            "mastodon": {"status": "healthy"},
            "frontend": {"status": "healthy"}
        }
    
    def _calculate_health_score(
        self, 
        db_health: Dict[str, Any], 
        redis_health: Dict[str, Any], 
        external_health: Dict[str, Any]
    ) -> int:
        """Calcule le score de santé global (0-100)"""
        score = 0
        
        # Score de la base de données (40%)
        if db_health.get("status") == "healthy":
            score += 40
        elif db_health.get("status") == "degraded":
            score += 20
        
        # Score de Redis (30%)
        if redis_health.get("status") == "healthy":
            score += 30
        elif redis_health.get("status") == "degraded":
            score += 15
        
        # Score des services externes (30%)
        external_services = external_health.values()
        healthy_services = sum(1 for service in external_services if service.get("status") == "healthy")
        total_services = len(external_services)
        
        if total_services > 0:
            score += int((healthy_services / total_services) * 30)
        
        return min(score, 100)
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Retourne le statut du monitoring"""
        return {
            "monitoring_active": self.monitoring_active,
            "metrics_cache_size": len(self.metrics_cache),
            "alert_thresholds": self.alert_thresholds,
            "last_update": self.metrics_cache.get("timestamp")
        }


