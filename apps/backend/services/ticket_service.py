"""
Service de gestion des tickets
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from ..models.ticket import Ticket
from ..models.conversation import Conversation
from ..schemas.ticket import TicketCreate, TicketUpdate, TicketResponse, TicketListResponse
import uuid


class TicketService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_ticket(self, ticket_data: TicketCreate) -> Ticket:
        """Crée un nouveau ticket"""
        ticket = Ticket(
            conversation_id=ticket_data.conversation_id,
            priority=ticket_data.priority,
            category=ticket_data.category,
            assigned_to=ticket_data.assigned_to
        )
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        
        return ticket
    
    async def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Récupère un ticket par ID"""
        return self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    async def update_ticket(self, ticket_id: str, ticket_data: TicketUpdate) -> Optional[Ticket]:
        """Met à jour un ticket"""
        ticket = await self.get_ticket(ticket_id)
        if not ticket:
            return None
        
        for field, value in ticket_data.dict(exclude_unset=True).items():
            setattr(ticket, field, value)
        
        self.db.commit()
        self.db.refresh(ticket)
        
        return ticket
    
    async def list_tickets(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> TicketListResponse:
        """Liste les tickets avec filtres et pagination"""
        query = self.db.query(Ticket)
        
        # Filtres
        if status:
            query = query.filter(Ticket.status == status)
        if priority:
            query = query.filter(Ticket.priority == priority)
        if assigned_to:
            query = query.filter(Ticket.assigned_to == assigned_to)
        
        # Tri
        if sort_order == "desc":
            query = query.order_by(desc(getattr(Ticket, sort_by)))
        else:
            query = query.order_by(asc(getattr(Ticket, sort_by)))
        
        # Pagination
        total = query.count()
        tickets = query.offset((page - 1) * size).limit(size).all()
        
        return TicketListResponse(
            tickets=[TicketResponse.from_orm(ticket) for ticket in tickets],
            total=total,
            page=page,
            size=size
        )
    
    async def get_tickets_by_conversation(self, conversation_id: str) -> List[Ticket]:
        """Récupère les tickets d'une conversation"""
        return self.db.query(Ticket).filter(
            Ticket.conversation_id == conversation_id
        ).all()
    
    async def assign_ticket(self, ticket_id: str, user_id: str) -> Optional[Ticket]:
        """Assigne un ticket à un utilisateur"""
        ticket = await self.get_ticket(ticket_id)
        if not ticket:
            return None
        
        ticket.assigned_to = user_id
        ticket.status = "IN_PROGRESS"
        self.db.commit()
        self.db.refresh(ticket)
        
        return ticket
    
    async def resolve_ticket(
        self, 
        ticket_id: str, 
        resolution_notes: str,
        user_id: str
    ) -> Optional[Ticket]:
        """Résout un ticket"""
        ticket = await self.get_ticket(ticket_id)
        if not ticket:
            return None
        
        ticket.status = "RESOLVED"
        ticket.resolution_notes = resolution_notes
        ticket.assigned_to = user_id
        self.db.commit()
        self.db.refresh(ticket)
        
        return ticket


