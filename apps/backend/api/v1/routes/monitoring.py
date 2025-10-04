"""
Routes de monitoring et analytics avancées
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
import logging

from apps.backend.core.database import get_db
from apps.backend.services.advanced_analytics_service import AdvancedAnalyticsService
from apps.backend.services.realtime_monitoring_service import RealtimeMonitoringService
from apps.backend.schemas.analytics import AnalyticsResponse

logger = logging.getLogger(__name__)

monitoring_router = APIRouter()


@monitoring_router.get("/realtime", response_model=dict)
async def get_realtime_metrics(db: Session = Depends(get_db)):
    """Récupère les métriques en temps réel"""
    try:
        monitoring_service = RealtimeMonitoringService(db)
        metrics = await monitoring_service.get_realtime_metrics()
        
        return {
            "status": "success",
            "data": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métriques temps réel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.get("/analytics/comprehensive", response_model=AnalyticsResponse)
async def get_comprehensive_analytics(
    start_date: Optional[str] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Récupère les analytics complètes"""
    try:
        # Conversion des dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        analytics_service = AdvancedAnalyticsService(db)
        analytics = analytics_service.get_comprehensive_analytics(start_dt, end_dt)
        
        return analytics
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.get("/health", response_model=dict)
async def get_system_health(db: Session = Depends(get_db)):
    """Récupère la santé du système"""
    try:
        monitoring_service = RealtimeMonitoringService(db)
        health = await monitoring_service.get_system_health()
        
        return {
            "status": "success",
            "data": health,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la santé: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.get("/alerts", response_model=dict)
async def get_alerts(
    limit: int = Query(50, description="Nombre maximum d'alertes à retourner"),
    db: Session = Depends(get_db)
):
    """Récupère les alertes récentes"""
    try:
        monitoring_service = RealtimeMonitoringService(db)
        alerts = await monitoring_service.get_alerts(limit)
        
        return {
            "status": "success",
            "data": alerts,
            "count": len(alerts),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des alertes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.get("/kpis", response_model=dict)
async def get_kpi_metrics(
    start_date: Optional[str] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Récupère les KPIs principaux"""
    try:
        # Conversion des dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        analytics_service = AdvancedAnalyticsService(db)
        kpis = analytics_service._calculate_kpi_metrics(start_dt, end_dt)
        
        return {
            "status": "success",
            "data": kpis.dict(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des KPIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.get("/performance", response_model=dict)
async def get_performance_metrics(
    start_date: Optional[str] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Récupère les métriques de performance"""
    try:
        # Conversion des dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        analytics_service = AdvancedAnalyticsService(db)
        performance = analytics_service._get_performance_metrics(start_dt, end_dt)
        
        return {
            "status": "success",
            "data": performance.dict(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métriques de performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.get("/ai-stats", response_model=dict)
async def get_ai_system_stats(db: Session = Depends(get_db)):
    """Récupère les statistiques du système IA"""
    try:
        analytics_service = AdvancedAnalyticsService(db)
        ai_stats = analytics_service.get_ai_system_stats()
        
        return {
            "status": "success",
            "data": ai_stats.dict(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stats IA: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.get("/dashboard", response_model=dict)
async def get_dashboard_data(
    start_date: Optional[str] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Récupère toutes les données du dashboard"""
    try:
        # Conversion des dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        analytics_service = AdvancedAnalyticsService(db)
        monitoring_service = RealtimeMonitoringService(db)
        
        # Récupération de toutes les données
        analytics = analytics_service.get_comprehensive_analytics(start_dt, end_dt)
        realtime_metrics = await monitoring_service.get_realtime_metrics()
        system_health = await monitoring_service.get_system_health()
        alerts = await monitoring_service.get_alerts(10)
        
        return {
            "status": "success",
            "data": {
                "analytics": analytics.dict(),
                "realtime": realtime_metrics,
                "health": system_health,
                "alerts": alerts
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données du dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.post("/monitoring/start", response_model=dict)
async def start_monitoring(db: Session = Depends(get_db)):
    """Démarre le monitoring en temps réel"""
    try:
        monitoring_service = RealtimeMonitoringService(db)
        
        if monitoring_service.monitoring_active:
            return {
                "status": "warning",
                "message": "Le monitoring est déjà actif",
                "timestamp": datetime.now().isoformat()
            }
        
        # Démarrage du monitoring en arrière-plan
        import asyncio
        asyncio.create_task(monitoring_service.start_monitoring())
        
        return {
            "status": "success",
            "message": "Monitoring démarré avec succès",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du démarrage du monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.post("/monitoring/stop", response_model=dict)
async def stop_monitoring(db: Session = Depends(get_db)):
    """Arrête le monitoring en temps réel"""
    try:
        monitoring_service = RealtimeMonitoringService(db)
        await monitoring_service.stop_monitoring()
        
        return {
            "status": "success",
            "message": "Monitoring arrêté avec succès",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'arrêt du monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@monitoring_router.get("/monitoring/status", response_model=dict)
async def get_monitoring_status(db: Session = Depends(get_db)):
    """Récupère le statut du monitoring"""
    try:
        monitoring_service = RealtimeMonitoringService(db)
        status = monitoring_service.get_monitoring_status()
        
        return {
            "status": "success",
            "data": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut: {e}")
        raise HTTPException(status_code=500, detail=str(e))


