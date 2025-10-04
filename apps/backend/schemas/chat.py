"""
Schémas Pydantic pour le chat
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    role: str = Field(default="user")


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[UUID] = None
    context_token: Optional[str] = None
    user_info: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    conversation_id: UUID
    message: MessageResponse
    response: MessageResponse
    needs_escalation: bool = False
    suggested_links: List[Dict[str, str]] = []


class ConversationCreate(BaseModel):
    source: str = Field(default="web")
    mastodon_user: Optional[str] = None
    mastodon_post_id: Optional[str] = None
    context_token: Optional[str] = None


class ConversationResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    source: str
    status: str
    mastodon_user: Optional[str]
    mastodon_post_id: Optional[str]
    context_token: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True


