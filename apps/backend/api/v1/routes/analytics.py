"""
Routes API pour les analytics
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ...core.database import get_db
from ...core.security import require_auth
from ...schemas.analytics import AnalyticsResponse
from ...services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/", response_model=AnalyticsResponse)
async def get_analytics(
    start_date: str = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: str = Query(None, description="Date de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(require_auth)
):
    """Récupère les données d'analytics"""
    # Dates par défaut (30 derniers jours)
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format de date invalide. Utilisez YYYY-MM-DD"
        )
    
    # Vérification que la date de fin est après la date de début
    if end_dt < start_dt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La date de fin doit être après la date de début"
        )
    
    # Limitation à 1 an maximum
    if (end_dt - start_dt).days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La période ne peut pas dépasser 1 an"
        )
    
    analytics_service = AnalyticsService(db)
    data = await analytics_service.get_analytics_data(start_dt, end_dt)
    
    return AnalyticsResponse(**data)


@router.get("/kpis")
async def get_kpis(
    start_date: str = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: str = Query(None, description="Date de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(require_auth)
):
    """Récupère les KPIs principaux"""
    # Dates par défaut (30 derniers jours)
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format de date invalide. Utilisez YYYY-MM-DD"
        )
    
    analytics_service = AnalyticsService(db)
    kpis = await analytics_service.get_kpis(start_dt, end_dt)
    
    return kpis


@router.get("/performance")
async def get_performance_metrics(
    start_date: str = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: str = Query(None, description="Date de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(require_auth)
):
    """Récupère les métriques de performance"""
    # Dates par défaut (30 derniers jours)
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format de date invalide. Utilisez YYYY-MM-DD"
        )
    
    analytics_service = AnalyticsService(db)
    performance = await analytics_service.get_performance_metrics(start_dt, end_dt)
    
    return performance


@router.get("/conversations-timeline")
async def get_conversations_timeline(
    start_date: str = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: str = Query(None, description="Date de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(require_auth)
):
    """Récupère la timeline des conversations"""
    # Dates par défaut (30 derniers jours)
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format de date invalide. Utilisez YYYY-MM-DD"
        )
    
    analytics_service = AnalyticsService(db)
    timeline = await analytics_service.get_conversations_timeline(start_dt, end_dt)
    
    return timeline


@router.get("/intent-distribution")
async def get_intent_distribution(
    start_date: str = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: str = Query(None, description="Date de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(require_auth)
):
    """Récupère la distribution des intentions"""
    # Dates par défaut (30 derniers jours)
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format de date invalide. Utilisez YYYY-MM-DD"
        )
    
    analytics_service = AnalyticsService(db)
    distribution = await analytics_service.get_intent_distribution(start_dt, end_dt)
    
    return distribution


