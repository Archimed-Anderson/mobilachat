"""
Schémas Pydantic pour les tickets
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class TicketCreate(BaseModel):
    conversation_id: UUID
    priority: str = Field(default="MEDIUM")
    category: Optional[str] = None
    assigned_to: Optional[UUID] = None


class TicketUpdate(BaseModel):
    priority: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    assigned_to: Optional[UUID] = None
    resolution_notes: Optional[str] = None


class TicketResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    priority: str
    status: str
    category: Optional[str]
    assigned_to: Optional[UUID]
    resolution_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    tickets: List[TicketResponse]
    total: int
    page: int
    size: int


