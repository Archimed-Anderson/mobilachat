"""
Schémas Pydantic pour les analytics
"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class KPICard(BaseModel):
    title: str
    value: int
    change: float
    change_type: str  # positive, negative, neutral


class KPIMetrics(BaseModel):
    """Métriques KPI principales"""
    total_conversations: int
    total_messages: int
    total_tickets: int
    resolution_rate: float
    avg_response_time: float
    customer_satisfaction: float
    first_contact_resolution: float
    escalation_rate: float

class PerformanceMetrics(BaseModel):
    """Métriques de performance"""
    response_time_p95: float
    response_time_p99: float
    throughput_per_hour: float
    error_rate: float
    uptime_percentage: float
    memory_usage: float
    cpu_usage: float

class AISystemStats(BaseModel):
    """Statistiques du système IA"""
    total_queries: int
    successful_queries: int
    failed_queries: int
    avg_processing_time: float
    model_accuracy: float
    cache_hit_rate: float
    vector_store_size: int

class ConversationTimeline(BaseModel):
    """Timeline des conversations"""
    date: str
    conversations: int
    messages: int
    tickets: int

class IntentDistribution(BaseModel):
    """Distribution des intentions"""
    intent: str
    count: int
    percentage: float

class TicketStatus(BaseModel):
    """Statut des tickets"""
    status: str
    count: int
    percentage: float

class HourlyActivity(BaseModel):
    """Activité par heure"""
    hour: int
    conversations: int
    messages: int

class SatisfactionGauge(BaseModel):
    """Jauge de satisfaction"""
    score: float
    level: str
    color: str

class AnalyticsResponse(BaseModel):
    kpis: Dict[str, Any]
    performance: Dict[str, Any]
    conversations_timeline: List[Dict[str, Any]]
    intent_distribution: List[Dict[str, Any]]
    ticket_status: List[Dict[str, Any]]
    hourly_activity: List[Dict[str, Any]]
    satisfaction_gauge: Dict[str, Any]


