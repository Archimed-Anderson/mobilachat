"""
Application FastAPI simplifiée sans base de données
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Modèles Pydantic
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    intent: str
    sentiment: str

class HealthResponse(BaseModel):
    status: str
    message: str

# Création de l'application
app = FastAPI(
    title="MobiliaChat API",
    description="API pour le chatbot Free Mobile",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérification de l'état de l'API"""
    return HealthResponse(
        status="healthy",
        message="API MobiliaChat fonctionne correctement"
    )

@app.get("/")
async def root():
    """Page d'accueil"""
    return {
        "message": "Bienvenue sur l'API MobiliaChat",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.post("/api/v1/chat/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """Endpoint de chat simplifié"""
    # Simulation d'une réponse IA
    response_text = f"Merci pour votre message : '{request.message}'. Comment puis-je vous aider avec votre forfait Free Mobile ?"
    
    return ChatResponse(
        response=response_text,
        conversation_id=request.conversation_id or "conv_123",
        intent="question",
        sentiment="neutral"
    )

@app.get("/api/v1/analytics")
async def get_analytics():
    """Endpoint d'analytics simplifié"""
    return {
        "total_conversations": 0,
        "total_messages": 0,
        "total_tickets": 0,
        "resolution_rate": 0.0,
        "avg_response_time": 0.0,
        "customer_satisfaction": 0.0
    }

@app.get("/api/v1/tickets")
async def get_tickets():
    """Endpoint des tickets simplifié"""
    return {
        "tickets": [],
        "total": 0
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
