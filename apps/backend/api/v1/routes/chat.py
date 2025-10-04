"""
Routes API pour le chat
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...core.redis_client import redis_client
from ...core.security import check_rate_limit
from ...schemas.chat import ChatRequest, ChatResponse, ConversationResponse
from ...services.chat_service import ChatService
import uuid

router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Envoie un message au chatbot et récupère la réponse"""
    # Vérification du rate limiting
    rate_limit_key = f"chat:{request.context_token or 'anonymous'}"
    if not await check_rate_limit(redis_client, rate_limit_key, 20):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de requêtes. Veuillez patienter."
        )
    
    # Traitement du message
    chat_service = ChatService(db)
    response = await chat_service.process_chat_request(request)
    
    return response


@router.get("/conversation/{conversation_id}/messages", response_model=List[dict])
async def get_conversation_messages(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Récupère les messages d'une conversation"""
    try:
        conv_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de conversation invalide"
        )
    
    chat_service = ChatService(db)
    messages = await chat_service.get_conversation_messages(str(conv_uuid))
    
    return [
        {
            "id": str(msg.id),
            "conversation_id": str(msg.conversation_id),
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        }
        for msg in messages
    ]


@router.get("/conversation/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Récupère une conversation avec ses messages"""
    try:
        conv_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de conversation invalide"
        )
    
    chat_service = ChatService(db)
    conversation = await chat_service.get_or_create_conversation()
    
    if not conversation or str(conversation.id) != conversation_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation non trouvée"
        )
    
    messages = await chat_service.get_conversation_messages(conversation_id)
    
    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        source=conversation.source,
        status=conversation.status,
        mastodon_user=conversation.mastodon_user,
        mastodon_post_id=conversation.mastodon_post_id,
        context_token=conversation.context_token,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            {
                "id": msg.id,
                "conversation_id": msg.conversation_id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at
            }
            for msg in messages
        ]
    )


