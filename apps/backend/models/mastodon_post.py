"""
Modèle post Mastodon
"""
from sqlalchemy import Column, String, DateTime, Text, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from ..core.database import Base


class MastodonPost(Base):
    __tablename__ = "mastodon_posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mastodon_id = Column(String(255), unique=True, nullable=False)
    author_username = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_complaint = Column(Boolean, default=False)
    sentiment_score = Column(Float, nullable=True)
    urgency = Column(String(50), nullable=True)  # LOW, MEDIUM, HIGH, URGENT
    context_token = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)


