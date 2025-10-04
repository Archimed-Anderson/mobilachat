"""
Service d'analytics
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
from ..models.conversation import Conversation, Message
from ..models.ticket import Ticket
from ..models.user import User


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_kpis(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Récupère les KPIs principaux"""
        # Total conversations
        total_conversations = self.db.query(Conversation).filter(
            and_(
                Conversation.created_at >= start_date,
                Conversation.created_at <= end_date
            )
        ).count()
        
        # Tickets ouverts
        open_tickets = self.db.query(Ticket).filter(
            Ticket.status.in_(["OPEN", "IN_PROGRESS"])
        ).count()
        
        # Taux de résolution
        total_tickets = self.db.query(Ticket).filter(
            and_(
                Ticket.created_at >= start_date,
                Ticket.created_at <= end_date
            )
        ).count()
        
        resolved_tickets = self.db.query(Ticket).filter(
            and_(
                Ticket.created_at >= start_date,
                Ticket.created_at <= end_date,
                Ticket.status == "RESOLVED"
            )
        ).count()
        
        resolution_rate = (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0
        
        # Temps de réponse moyen (simulation)
        avg_response_time = 2.5  # minutes
        
        return {
            "total_conversations": total_conversations,
            "open_tickets": open_tickets,
            "resolution_rate": round(resolution_rate, 1),
            "avg_response_time": avg_response_time
        }
    
    async def get_performance_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Récupère les métriques de performance"""
        # Total messages
        total_messages = self.db.query(Message).filter(
            and_(
                Message.created_at >= start_date,
                Message.created_at <= end_date
            )
        ).count()
        
        # Temps de résolution moyen
        resolved_tickets = self.db.query(Ticket).filter(
            and_(
                Ticket.created_at >= start_date,
                Ticket.created_at <= end_date,
                Ticket.status == "RESOLVED"
            )
        ).all()
        
        avg_resolution_time = 0
        if resolved_tickets:
            total_time = sum([
                (ticket.updated_at - ticket.created_at).total_seconds() / 3600
                for ticket in resolved_tickets
            ])
            avg_resolution_time = total_time / len(resolved_tickets)
        
        # Taux d'escalade
        escalated_conversations = self.db.query(Conversation).filter(
            and_(
                Conversation.created_at >= start_date,
                Conversation.created_at <= end_date,
                Conversation.status == "escalated"
            )
        ).count()
        
        total_conversations = self.db.query(Conversation).filter(
            and_(
                Conversation.created_at >= start_date,
                Conversation.created_at <= end_date
            )
        ).count()
        
        escalation_rate = (escalated_conversations / total_conversations * 100) if total_conversations > 0 else 0
        
        return {
            "total_messages": total_messages,
            "avg_resolution_time": round(avg_resolution_time, 1),
            "escalation_rate": round(escalation_rate, 1)
        }
    
    async def get_conversations_timeline(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Récupère la timeline des conversations"""
        conversations = self.db.query(
            func.date(Conversation.created_at).label('date'),
            func.count(Conversation.id).label('count')
        ).filter(
            and_(
                Conversation.created_at >= start_date,
                Conversation.created_at <= end_date
            )
        ).group_by(
            func.date(Conversation.created_at)
        ).order_by('date').all()
        
        return [
            {
                "date": str(conv.date),
                "conversations": conv.count
            }
            for conv in conversations
        ]
    
    async def get_intent_distribution(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Récupère la distribution des intentions (simulation)"""
        # Simulation des données d'intention
        return [
            {"intent": "facturation", "count": 45, "percentage": 30.0},
            {"intent": "technique", "count": 35, "percentage": 23.3},
            {"intent": "forfait", "count": 25, "percentage": 16.7},
            {"intent": "resiliation", "count": 20, "percentage": 13.3},
            {"intent": "autre", "count": 25, "percentage": 16.7}
        ]
    
    async def get_ticket_status_distribution(self) -> List[Dict[str, Any]]:
        """Récupère la distribution des statuts de tickets"""
        statuses = self.db.query(
            Ticket.status,
            func.count(Ticket.id).label('count')
        ).group_by(Ticket.status).all()
        
        return [
            {
                "status": status.status,
                "count": status.count
            }
            for status in statuses
        ]
    
    async def get_hourly_activity(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Récupère l'activité par heure"""
        messages = self.db.query(
            func.extract('hour', Message.created_at).label('hour'),
            func.count(Message.id).label('count')
        ).filter(
            and_(
                Message.created_at >= start_date,
                Message.created_at <= end_date
            )
        ).group_by(
            func.extract('hour', Message.created_at)
        ).order_by('hour').all()
        
        return [
            {
                "hour": int(msg.hour),
                "messages": msg.count
            }
            for msg in messages
        ]
    
    async def get_satisfaction_gauge(self) -> Dict[str, Any]:
        """Récupère le gauge de satisfaction (simulation)"""
        return {
            "value": 4.2,
            "max": 5.0,
            "label": "Satisfaction Client"
        }
    
    async def get_analytics_data(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Récupère toutes les données d'analytics"""
        return {
            "kpis": await self.get_kpis(start_date, end_date),
            "performance": await self.get_performance_metrics(start_date, end_date),
            "conversations_timeline": await self.get_conversations_timeline(start_date, end_date),
            "intent_distribution": await self.get_intent_distribution(start_date, end_date),
            "ticket_status": await self.get_ticket_status_distribution(),
            "hourly_activity": await self.get_hourly_activity(start_date, end_date),
            "satisfaction_gauge": await self.get_satisfaction_gauge()
        }


