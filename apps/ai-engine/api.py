"""
API FastAPI pour le moteur IA
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import uvicorn

import sys
import os
sys.path.append(os.path.dirname(__file__))
from config.settings import settings
from rag.vector_store import vector_store
from rag.document_processor import DocumentProcessor
from models.response_generator import ResponseGenerator

# Configuration du logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Moteur IA pour le chatbot Free Mobile avec RAG"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation des composants
response_generator = ResponseGenerator()
document_processor = DocumentProcessor()


# Modèles Pydantic
class GenerateRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    context_token: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = None


class GenerateResponse(BaseModel):
    response: str
    intent: Dict[str, Any]
    sentiment: Dict[str, Any]
    needs_escalation: bool
    suggested_links: List[Dict[str, str]]
    context_used: bool
    confidence: float


class IngestRequest(BaseModel):
    reset_collection: bool = False
    process_conversations: bool = True


class IngestResponse(BaseModel):
    success: bool
    documents_processed: int
    message: str


class StatsResponse(BaseModel):
    vector_store_stats: Dict[str, Any]
    model_info: Dict[str, Any]
    system_status: str


# Routes
@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {
        "message": "Free Mobile AI Engine",
        "version": settings.VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Vérification de santé du moteur IA"""
    try:
        # Vérifier le vector store
        vector_stats = vector_store.get_stats()
        
        # Vérifier le générateur de réponse
        generator_status = "ok" if response_generator.llm_pipeline else "fallback"
        
        return {
            "status": "healthy",
            "vector_store": "connected" if vector_stats else "disconnected",
            "llm_model": generator_status,
            "version": settings.VERSION
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_response(request: GenerateRequest):
    """Génère une réponse IA basée sur le message"""
    try:
        logger.info(f"Génération de réponse pour: {request.message[:50]}...")
        
        # Génération de la réponse
        result = response_generator.generate_response(
            message=request.message,
            conversation_id=request.conversation_id or "unknown",
            context_token=request.context_token
        )
        
        # Calcul de la confiance globale
        confidence = (
            result["intent"].get("confidence", 0.5) + 
            result["sentiment"].get("confidence", 0.5)
        ) / 2
        
        return GenerateResponse(
            response=result["response"],
            intent=result["intent"],
            sentiment=result["sentiment"],
            needs_escalation=result["needs_escalation"],
            suggested_links=result["suggested_links"],
            context_used=result["context_used"],
            confidence=confidence
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de génération: {str(e)}")


@app.post("/api/ingest-documents", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest, background_tasks: BackgroundTasks):
    """Ingère les documents dans la base vectorielle"""
    try:
        documents_processed = 0
        
        # Réinitialisation de la collection si demandée
        if request.reset_collection:
            logger.info("Réinitialisation de la collection...")
            vector_store.reset_collection()
        
        # Traitement des documents
        logger.info("Traitement des documents...")
        documents = document_processor.process_all_documents()
        
        if documents:
            # Ajout des documents au vector store
            success = vector_store.add_documents(documents)
            if success:
                documents_processed = len(documents)
                logger.info(f"{documents_processed} documents ingérés avec succès")
            else:
                raise Exception("Erreur lors de l'ajout des documents")
        
        # Traitement des conversations si demandé
        if request.process_conversations:
            logger.info("Traitement des conversations...")
            conv_documents = document_processor.process_conversations()
            
            if conv_documents:
                success = vector_store.add_documents(conv_documents)
                if success:
                    documents_processed += len(conv_documents)
                    logger.info(f"{len(conv_documents)} conversations ingérées")
        
        return IngestResponse(
            success=True,
            documents_processed=documents_processed,
            message=f"{documents_processed} documents traités avec succès"
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'ingestion: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur d'ingestion: {str(e)}")


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Récupère les statistiques du moteur IA"""
    try:
        # Statistiques du vector store
        vector_stats = vector_store.get_stats()
        
        # Informations sur le modèle
        model_info = {
            "llm_model": settings.LLM_MODEL_NAME,
            "embedding_model": settings.EMBEDDING_MODEL,
            "device": settings.LLM_DEVICE,
            "max_tokens": settings.LLM_MAX_TOKENS,
            "temperature": settings.LLM_TEMPERATURE,
            "rag_top_k": settings.RAG_TOP_K,
            "similarity_threshold": settings.RAG_SIMILARITY_THRESHOLD
        }
        
        # Statut du système
        system_status = "healthy"
        if not vector_stats:
            system_status = "vector_store_error"
        if not response_generator.llm_pipeline:
            system_status = "llm_fallback"
        
        return StatsResponse(
            vector_store_stats=vector_stats,
            model_info=model_info,
            system_status=system_status
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stats: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de stats: {str(e)}")


@app.delete("/api/reset-vector-store")
async def reset_vector_store():
    """Remet à zéro la base vectorielle"""
    try:
        success = vector_store.reset_collection()
        
        if success:
            return {"message": "Base vectorielle réinitialisée avec succès"}
        else:
            raise HTTPException(status_code=500, detail="Erreur lors de la réinitialisation")
            
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de réinitialisation: {str(e)}")


@app.get("/api/search")
async def search_documents(query: str, top_k: Optional[int] = None):
    """Recherche des documents dans la base vectorielle"""
    try:
        results = vector_store.search(query, top_k=top_k)
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de recherche: {str(e)}")


@app.get("/api/intents")
async def get_supported_intents():
    """Retourne les intentions supportées"""
    try:
        intents = response_generator.intent_detector.get_supported_intents()
        
        return {
            "intents": intents,
            "count": len(intents)
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des intentions: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur d'intentions: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )


