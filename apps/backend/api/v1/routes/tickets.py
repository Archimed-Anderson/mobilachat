"""
Routes API pour les tickets
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from ...core.database import get_db
from ...core.security import require_auth
from ...schemas.ticket import TicketCreate, TicketUpdate, TicketResponse, TicketListResponse
from ...services.ticket_service import TicketService
import uuid

router = APIRouter()


@router.get("/", response_model=TicketListResponse)
async def list_tickets(
    status: Optional[str] = Query(None, description="Filtrer par statut"),
    priority: Optional[str] = Query(None, description="Filtrer par priorité"),
    assigned_to: Optional[str] = Query(None, description="Filtrer par assigné"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(20, ge=1, le=100, description="Taille de page"),
    sort_by: str = Query("created_at", description="Champ de tri"),
    sort_order: str = Query("desc", description="Ordre de tri (asc/desc)"),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(require_auth)
):
    """Liste les tickets avec filtres et pagination"""
    ticket_service = TicketService(db)
    
    # Validation des paramètres
    valid_statuses = ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]
    valid_priorities = ["LOW", "MEDIUM", "HIGH", "URGENT"]
    valid_sort_fields = ["created_at", "updated_at", "priority", "status"]
    
    if status and status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Statut invalide. Valeurs autorisées: {valid_statuses}"
        )
    
    if priority and priority not in valid_priorities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Priorité invalide. Valeurs autorisées: {valid_priorities}"
        )
    
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Champ de tri invalide. Valeurs autorisées: {valid_sort_fields}"
        )
    
    if sort_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ordre de tri invalide. Valeurs autorisées: asc, desc"
        )
    
    return await ticket_service.list_tickets(
        status=status,
        priority=priority,
        assigned_to=assigned_to,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(require_auth)
):
    """Récupère un ticket par ID"""
    try:
        ticket_uuid = uuid.UUID(ticket_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de ticket invalide"
        )
    
    ticket_service = TicketService(db)
    ticket = await ticket_service.get_ticket(str(ticket_uuid))
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket non trouvé"
        )
    
    return ticket


@router.post("/", response_model=TicketResponse)
async def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(require_auth)
):
    """Crée un nouveau ticket"""
    ticket_service = TicketService(db)
    ticket = await ticket_service.create_ticket(ticket_data)
    
    return ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: str,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(require_auth)
):
    """Met à jour un ticket"""
    try:
        ticket_uuid = uuid.UUID(ticket_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de ticket invalide"
        )
    
    ticket_service = TicketService(db)
    ticket = await ticket_service.update_ticket(str(ticket_uuid), ticket_data)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket non trouvé"
        )
    
    return ticket


@router.post("/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: str,
    user_id: str = Query(..., description="ID de l'utilisateur à assigner"),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(require_auth)
):
    """Assigne un ticket à un utilisateur"""
    try:
        ticket_uuid = uuid.UUID(ticket_id)
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID invalide"
        )
    
    ticket_service = TicketService(db)
    ticket = await ticket_service.assign_ticket(str(ticket_uuid), str(user_uuid))
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket non trouvé"
        )
    
    return {"message": "Ticket assigné avec succès", "ticket": ticket}


@router.post("/{ticket_id}/resolve")
async def resolve_ticket(
    ticket_id: str,
    resolution_notes: str = Query(..., description="Notes de résolution"),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(require_auth)
):
    """Résout un ticket"""
    try:
        ticket_uuid = uuid.UUID(ticket_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de ticket invalide"
        )
    
    ticket_service = TicketService(db)
    ticket = await ticket_service.resolve_ticket(
        str(ticket_uuid), 
        resolution_notes, 
        current_user_id
    )
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket non trouvé"
        )
    
    return {"message": "Ticket résolu avec succès", "ticket": ticket}


