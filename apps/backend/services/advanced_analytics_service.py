"""
Service d'analytics avancé pour le monitoring en temps réel
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
import logging
from ..models.conversation import Conversation, Message
from ..models.ticket import Ticket
from ..models.mastodon_post import MastodonPost
from ..models.user import User
from ..schemas.analytics import (
    AnalyticsResponse,
    KPIMetrics,
    ConversationTimeline,
    IntentDistribution,
    TicketStatus,
    HourlyActivity,
    SatisfactionGauge,
    PerformanceMetrics,
    AISystemStats
)

logger = logging.getLogger(__name__)


class AdvancedAnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_comprehensive_analytics(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> AnalyticsResponse:
        """Récupère les analytics complètes"""
        try:
            # Filtrage par dates
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            # KPIs principaux
            kpis = self._calculate_kpi_metrics(start_date, end_date)
            
            # Timeline des conversations
            conversations_timeline = self._get_conversations_timeline(start_date, end_date)
            
            # Distribution des intentions
            intent_distribution = self._get_intent_distribution(start_date, end_date)
            
            # Statuts des tickets
            ticket_status = self._get_ticket_status_distribution(start_date, end_date)
            
            # Activité par heure
            hourly_activity = self._get_hourly_activity(start_date, end_date)
            
            # Métriques de performance
            performance = self._get_performance_metrics(start_date, end_date)
            
            # Gauge de satisfaction
            satisfaction = self._get_satisfaction_gauge(start_date, end_date)
            
            return AnalyticsResponse(
                kpis=kpis,
                conversations_timeline=conversations_timeline,
                intent_distribution=intent_distribution,
                ticket_status=ticket_status,
                hourly_activity=hourly_activity,
                performance=performance,
                satisfaction_gauge=satisfaction,
                generated_at=datetime.now().isoformat(),
                period_start=start_date.isoformat(),
                period_end=end_date.isoformat()
            )
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des analytics: {e}")
            raise
    
    def _calculate_kpi_metrics(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> KPIMetrics:
        """Calcule les KPIs principaux"""
        try:
            # Total des conversations
            total_conversations = self.db.query(Conversation).filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at <= end_date
                )
            ).count()
            
            # Conversations de la période précédente (pour le delta)
            prev_start = start_date - (end_date - start_date)
            prev_conversations = self.db.query(Conversation).filter(
                and_(
                    Conversation.created_at >= prev_start,
                    Conversation.created_at < start_date
                )
            ).count()
            
            conversations_change = self._calculate_percentage_change(
                total_conversations, prev_conversations
            )
            
            # Tickets ouverts
            open_tickets = self.db.query(Ticket).filter(
                Ticket.status.in_(['OPEN', 'IN_PROGRESS'])
            ).count()
            
            # Tickets de la période précédente
            prev_open_tickets = self.db.query(Ticket).filter(
                and_(
                    Ticket.status.in_(['OPEN', 'IN_PROGRESS']),
                    Ticket.created_at < start_date
                )
            ).count()
            
            tickets_change = self._calculate_percentage_change(
                open_tickets, prev_open_tickets
            )
            
            # Taux de résolution
            resolved_tickets = self.db.query(Ticket).filter(
                and_(
                    Ticket.status == 'RESOLVED',
                    Ticket.updated_at >= start_date,
                    Ticket.updated_at <= end_date
                )
            ).count()
            
            total_tickets_period = self.db.query(Ticket).filter(
                and_(
                    Ticket.created_at >= start_date,
                    Ticket.created_at <= end_date
                )
            ).count()
            
            resolution_rate = (resolved_tickets / total_tickets_period * 100) if total_tickets_period > 0 else 0
            
            # Temps de réponse moyen
            avg_response_time = self._calculate_avg_response_time(start_date, end_date)
            
            return KPIMetrics(
                total_conversations=total_conversations,
                conversations_change=conversations_change,
                open_tickets=open_tickets,
                tickets_change=tickets_change,
                resolution_rate=resolution_rate,
                resolution_change=0.0,  # À calculer si nécessaire
                avg_response_time=avg_response_time,
                response_time_change=0.0  # À calculer si nécessaire
            )
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des KPIs: {e}")
            return KPIMetrics()
    
    def _get_conversations_timeline(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[ConversationTimeline]:
        """Récupère la timeline des conversations"""
        try:
            # Groupement par jour
            daily_conversations = self.db.query(
                func.date(Conversation.created_at).label('date'),
                func.count(Conversation.id).label('conversations')
            ).filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at <= end_date
                )
            ).group_by(
                func.date(Conversation.created_at)
            ).order_by('date').all()
            
            return [
                ConversationTimeline(
                    date=row.date.isoformat(),
                    conversations=row.conversations
                )
                for row in daily_conversations
            ]
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la timeline: {e}")
            return []
    
    def _get_intent_distribution(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[IntentDistribution]:
        """Récupère la distribution des intentions"""
        try:
            # Analyse des messages pour extraire les intentions
            # (Cette logique pourrait être améliorée avec un vrai système de détection d'intention)
            
            # Intentions simulées basées sur le contenu des messages
            intent_data = self.db.query(
                func.count(Message.id).label('count')
            ).join(Conversation).filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at <= end_date
                )
            ).first()
            
            # Distribution simulée (à remplacer par une vraie analyse)
            intents = [
                IntentDistribution(intent="facturation", count=25),
                IntentDistribution(intent="technique", count=40),
                IntentDistribution(intent="forfait", count=20),
                IntentDistribution(intent="résiliation", count=10),
                IntentDistribution(intent="général", count=5)
            ]
            
            return intents
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des intentions: {e}")
            return []
    
    def _get_ticket_status_distribution(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[TicketStatus]:
        """Récupère la distribution des statuts de tickets"""
        try:
            status_counts = self.db.query(
                Ticket.status,
                func.count(Ticket.id).label('count')
            ).filter(
                and_(
                    Ticket.created_at >= start_date,
                    Ticket.created_at <= end_date
                )
            ).group_by(Ticket.status).all()
            
            return [
                TicketStatus(status=row.status, count=row.count)
                for row in status_counts
            ]
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statuts: {e}")
            return []
    
    def _get_hourly_activity(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[HourlyActivity]:
        """Récupère l'activité par heure"""
        try:
            hourly_data = self.db.query(
                func.extract('hour', Message.created_at).label('hour'),
                func.count(Message.id).label('messages')
            ).join(Conversation).filter(
                and_(
                    Message.created_at >= start_date,
                    Message.created_at <= end_date
                )
            ).group_by(
                func.extract('hour', Message.created_at)
            ).order_by('hour').all()
            
            return [
                HourlyActivity(hour=int(row.hour), messages=row.messages)
                for row in hourly_data
            ]
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'activité horaire: {e}")
            return []
    
    def _get_performance_metrics(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> PerformanceMetrics:
        """Récupère les métriques de performance"""
        try:
            # Total des messages
            total_messages = self.db.query(Message).join(Conversation).filter(
                and_(
                    Message.created_at >= start_date,
                    Message.created_at <= end_date
                )
            ).count()
            
            # Temps de résolution moyen
            resolved_tickets = self.db.query(Ticket).filter(
                and_(
                    Ticket.status == 'RESOLVED',
                    Ticket.updated_at >= start_date,
                    Ticket.updated_at <= end_date
                )
            ).all()
            
            avg_resolution_time = 0
            if resolved_tickets:
                resolution_times = []
                for ticket in resolved_tickets:
                    if ticket.created_at and ticket.updated_at:
                        resolution_time = (ticket.updated_at - ticket.created_at).total_seconds() / 3600  # en heures
                        resolution_times.append(resolution_time)
                
                avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
            
            # Taux d'escalade
            escalated_conversations = self.db.query(Conversation).filter(
                and_(
                    Conversation.needs_escalation == True,
                    Conversation.created_at >= start_date,
                    Conversation.created_at <= end_date
                )
            ).count()
            
            total_conversations = self.db.query(Conversation).filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at <= end_date
                )
            ).count()
            
            escalation_rate = (escalated_conversations / total_conversations * 100) if total_conversations > 0 else 0
            
            return PerformanceMetrics(
                total_messages=total_messages,
                avg_resolution_time=avg_resolution_time,
                escalation_rate=escalation_rate
            )
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des métriques de performance: {e}")
            return PerformanceMetrics()
    
    def _get_satisfaction_gauge(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> SatisfactionGauge:
        """Récupère le gauge de satisfaction"""
        try:
            # Satisfaction simulée (à remplacer par de vraies données de satisfaction)
            # Dans un vrai système, cela viendrait d'enquêtes de satisfaction
            
            satisfaction_score = 4.2  # Score sur 5
            max_score = 5.0
            
            return SatisfactionGauge(
                value=satisfaction_score,
                max=max_score,
                label="Satisfaction Client"
            )
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul de la satisfaction: {e}")
            return SatisfactionGauge()
    
    def _calculate_avg_response_time(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> float:
        """Calcule le temps de réponse moyen en minutes"""
        try:
            # Récupération des messages utilisateur et assistant
            user_messages = self.db.query(Message).filter(
                and_(
                    Message.role == 'user',
                    Message.created_at >= start_date,
                    Message.created_at <= end_date
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
                    response_time = (next_response.created_at - user_msg.created_at).total_seconds() / 60  # en minutes
                    response_times.append(response_time)
            
            return sum(response_times) / len(response_times) if response_times else 0
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul du temps de réponse: {e}")
            return 0.0
    
    def _calculate_percentage_change(self, current: int, previous: int) -> float:
        """Calcule le pourcentage de changement"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        
        return ((current - previous) / previous) * 100
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques en temps réel"""
        try:
            now = datetime.now()
            last_hour = now - timedelta(hours=1)
            last_24h = now - timedelta(hours=24)
            
            # Conversations de la dernière heure
            conversations_last_hour = self.db.query(Conversation).filter(
                Conversation.created_at >= last_hour
            ).count()
            
            # Messages de la dernière heure
            messages_last_hour = self.db.query(Message).filter(
                Message.created_at >= last_hour
            ).count()
            
            # Tickets ouverts
            open_tickets = self.db.query(Ticket).filter(
                Ticket.status.in_(['OPEN', 'IN_PROGRESS'])
            ).count()
            
            # Tickets créés dans les dernières 24h
            tickets_last_24h = self.db.query(Ticket).filter(
                Ticket.created_at >= last_24h
            ).count()
            
            return {
                "conversations_last_hour": conversations_last_hour,
                "messages_last_hour": messages_last_hour,
                "open_tickets": open_tickets,
                "tickets_last_24h": tickets_last_24h,
                "timestamp": now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des métriques temps réel: {e}")
            return {}
    
    def get_ai_system_stats(self) -> AISystemStats:
        """Récupère les statistiques du système IA"""
        try:
            # Statistiques du vector store (simulées)
            vector_store_stats = {
                "total_documents": 1500,
                "similarity_threshold": 0.75,
                "last_updated": datetime.now().isoformat()
            }
            
            # Informations sur les modèles
            model_info = {
                "llm_model": "HuggingFaceH4/zephyr-7b-beta",
                "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                "device": "cpu",
                "temperature": 0.7
            }
            
            # Statut du système
            system_status = "healthy"
            
            return AISystemStats(
                vector_store_stats=vector_store_stats,
                model_info=model_info,
                system_status=system_status
            )
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des stats IA: {e}")
            return AISystemStats()


