"""
Modèle ticket
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base


class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"))
    priority = Column(String(50), default="MEDIUM")  # LOW, MEDIUM, HIGH, URGENT
    status = Column(String(50), default="OPEN")  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    category = Column(String(100), nullable=True)  # facturation, technique, forfait
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    conversation = relationship("Conversation", back_populates="tickets")
    assigned_user = relationship("User", foreign_keys=[assigned_to])


