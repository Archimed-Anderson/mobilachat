"""
Modèles conversation et message
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    source = Column(String(50), default="web")  # web, mastodon
    status = Column(String(50), default="active")  # active, closed, escalated
    mastodon_user = Column(String(255), nullable=True)
    mastodon_post_id = Column(String(255), nullable=True)
    context_token = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="conversation", cascade="all, delete-orphan")
    user = relationship("User", back_populates="conversations")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"))
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_metadata = Column(Text, nullable=True)  # JSON stocké en texte
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    conversation = relationship("Conversation", back_populates="messages")


