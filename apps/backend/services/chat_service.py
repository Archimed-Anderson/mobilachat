"""
Service de gestion du chat
"""
import httpx
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from ..models.conversation import Conversation, Message
from ..models.user import User
from ..schemas.chat import ChatRequest, ChatResponse, MessageCreate
from ..core.config import settings
from ..core.redis_client import redis_client
import json
import uuid


class ChatService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_or_create_conversation(
        self, 
        user_id: Optional[str] = None,
        context_token: Optional[str] = None,
        source: str = "web"
    ) -> Conversation:
        """Récupère ou crée une conversation"""
        if context_token:
            # Chercher par token de contexte
            conversation = self.db.query(Conversation).filter(
                Conversation.context_token == context_token
            ).first()
            if conversation:
                return conversation
        
        if user_id:
            # Chercher la dernière conversation active de l'utilisateur
            conversation = self.db.query(Conversation).filter(
                Conversation.user_id == user_id,
                Conversation.status == "active"
            ).order_by(Conversation.created_at.desc()).first()
            if conversation:
                return conversation
        
        # Créer une nouvelle conversation
        conversation = Conversation(
            user_id=user_id,
            context_token=context_token or str(uuid.uuid4()),
            source=source
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        return conversation
    
    async def _get_or_create_user(self, user_info: Dict[str, Any]) -> Optional[User]:
        """Récupère ou crée un utilisateur à partir des infos de contact"""
        if not user_info or "phone_number" not in user_info:
            return None
        
        # Chercher par numéro de téléphone
        user = self.db.query(User).filter(
            User.phone_number == user_info["phone_number"]
        ).first()
        
        if user:
            return user
        
        # Créer un nouvel utilisateur
        user = User(
            username=f"user_{user_info['phone_number']}",
            email=user_info.get("email", f"user_{user_info['phone_number']}@free-mobile.local"),
            hashed_password="",  # Pas de mot de passe pour les utilisateurs anonymes
            full_name=user_info.get("name"),
            phone_number=user_info["phone_number"]
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def save_message(
        self, 
        conversation_id: str, 
        content: str, 
        role: str = "user",
        metadata: Optional[Dict] = None
    ) -> Message:
        """Sauvegarde un message"""
        message = Message(
            conversation_id=conversation_id,
            content=content,
            role=role,
            metadata=json.dumps(metadata) if metadata else None
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    async def get_conversation_messages(self, conversation_id: str) -> list[Message]:
        """Récupère les messages d'une conversation"""
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).all()
    
    async def get_ai_response(
        self, 
        message: str, 
        conversation_id: str,
        context_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Appelle le moteur IA pour générer une réponse"""
        try:
            async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT) as client:
                response = await client.post(
                    f"{settings.AI_ENGINE_URL}/api/generate",
                    json={
                        "message": message,
                        "conversation_id": str(conversation_id),
                        "context_token": context_token
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {
                "response": "Désolé, je rencontre un problème technique. Veuillez réessayer plus tard.",
                "needs_escalation": True,
                "suggested_links": []
            }
    
    async def process_chat_request(self, request: ChatRequest) -> ChatResponse:
        """Traite une requête de chat complète"""
        # Récupérer ou créer l'utilisateur
        user = None
        if request.user_info:
            user = await self._get_or_create_user(request.user_info)
        
        # Récupérer ou créer la conversation
        conversation = await self.get_or_create_conversation(
            user_id=str(user.id) if user else None,
            context_token=request.context_token,
            source="web"
        )
        
        # Sauvegarder le message utilisateur
        user_message = await self.save_message(
            conversation_id=str(conversation.id),
            content=request.message,
            role="user"
        )
        
        # Obtenir la réponse IA
        ai_response = await self.get_ai_response(
            message=request.message,
            conversation_id=str(conversation.id),
            context_token=conversation.context_token
        )
        
        # Sauvegarder la réponse IA
        assistant_message = await self.save_message(
            conversation_id=str(conversation.id),
            content=ai_response["response"],
            role="assistant",
            metadata={
                "needs_escalation": ai_response.get("needs_escalation", False),
                "suggested_links": ai_response.get("suggested_links", [])
            }
        )
        
        # Mettre à jour le statut de la conversation si escalade
        if ai_response.get("needs_escalation"):
            conversation.status = "escalated"
            self.db.commit()
        
        return ChatResponse(
            conversation_id=conversation.id,
            message=user_message,
            response=assistant_message,
            needs_escalation=ai_response.get("needs_escalation", False),
            suggested_links=ai_response.get("suggested_links", [])
        )


