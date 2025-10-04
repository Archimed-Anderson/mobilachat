"""
AI Engine simplifié
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

# Modèles Pydantic
class HealthResponse(BaseModel):
    status: str
    message: str

class IntentRequest(BaseModel):
    text: str

class IntentResponse(BaseModel):
    intent: str
    confidence: float

class SentimentRequest(BaseModel):
    text: str

class SentimentResponse(BaseModel):
    sentiment: str
    confidence: float

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    sentiment: str
    confidence: float

# Création de l'application
app = FastAPI(
    title="MobiliaChat AI Engine",
    description="Moteur IA pour le chatbot Free Mobile",
    version="1.0.0"
)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérification de l'état de l'AI Engine"""
    return HealthResponse(
        status="healthy",
        message="AI Engine MobiliaChat fonctionne correctement"
    )

@app.get("/")
async def root():
    """Page d'accueil"""
    return {
        "message": "Bienvenue sur l'AI Engine MobiliaChat",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.post("/api/v1/intent", response_model=IntentResponse)
async def detect_intent(request: IntentRequest):
    """Détection d'intention simplifiée"""
    text = request.text.lower()
    
    # Logique simple de détection d'intention
    if any(word in text for word in ["problème", "erreur", "bug", "ne marche pas"]):
        intent = "technical_issue"
        confidence = 0.8
    elif any(word in text for word in ["facture", "paiement", "prix", "coût"]):
        intent = "billing"
        confidence = 0.8
    elif any(word in text for word in ["forfait", "changer", "modifier", "upgrade"]):
        intent = "plan_change"
        confidence = 0.8
    elif any(word in text for word in ["résilier", "annuler", "arrêter"]):
        intent = "cancellation"
        confidence = 0.8
    else:
        intent = "general_inquiry"
        confidence = 0.6
    
    return IntentResponse(intent=intent, confidence=confidence)

@app.post("/api/v1/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    """Analyse de sentiment simplifiée"""
    text = request.text.lower()
    
    # Logique simple d'analyse de sentiment
    positive_words = ["merci", "bien", "parfait", "excellent", "satisfait", "content"]
    negative_words = ["problème", "erreur", "mauvais", "nul", "déçu", "frustré", "énervé"]
    
    positive_count = sum(1 for word in positive_words if word in text)
    negative_count = sum(1 for word in negative_words if word in text)
    
    if positive_count > negative_count:
        sentiment = "positive"
        confidence = 0.7
    elif negative_count > positive_count:
        sentiment = "negative"
        confidence = 0.7
    else:
        sentiment = "neutral"
        confidence = 0.5
    
    return SentimentResponse(sentiment=sentiment, confidence=confidence)

@app.post("/api/v1/chat", response_model=ChatResponse)
async def generate_response(request: ChatRequest):
    """Génération de réponse simplifiée"""
    message = request.message
    
    # Détection d'intention
    intent_response = await detect_intent(IntentRequest(text=message))
    intent = intent_response.intent
    
    # Analyse de sentiment
    sentiment_response = await analyze_sentiment(SentimentRequest(text=message))
    sentiment = sentiment_response.sentiment
    
    # Génération de réponse basée sur l'intention
    if intent == "technical_issue":
        response = "Je comprends que vous rencontrez un problème technique. Pouvez-vous me donner plus de détails sur ce qui ne fonctionne pas ?"
    elif intent == "billing":
        response = "Pour toute question concernant votre facture, je peux vous aider. Avez-vous un problème spécifique avec votre facturation ?"
    elif intent == "plan_change":
        response = "Vous souhaitez modifier votre forfait ? Je peux vous présenter les options disponibles. Quel type de forfait vous intéresse ?"
    elif intent == "cancellation":
        response = "Je comprends que vous souhaitez résilier votre abonnement. Avant de procéder, y a-t-il quelque chose que nous pouvons faire pour vous satisfaire ?"
    else:
        response = "Bonjour ! Comment puis-je vous aider avec votre forfait Free Mobile aujourd'hui ?"
    
    return ChatResponse(
        response=response,
        intent=intent,
        sentiment=sentiment,
        confidence=0.8
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
