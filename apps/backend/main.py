"""
Application FastAPI principale
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn

from .core.config import settings
from .core.database import create_tables
from .core.redis_client import redis_client
from .api.v1.routes import chat, tickets, analytics, monitoring


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    await redis_client.connect()
    create_tables()
    yield
    # Shutdown
    await redis_client.disconnect()


# Création de l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="API pour le chatbot SAV Free Mobile avec IA et intégration Mastodon",
    lifespan=lifespan
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de sécurité
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"]
)


# Routes de base
@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {
        "message": "Free Mobile Chatbot API",
        "version": settings.VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Vérification de santé de l'API"""
    try:
        # Vérifier Redis
        await redis_client.set_value("health_check", "ok", expire=10)
        redis_status = await redis_client.get_value("health_check") == "ok"
        
        return {
            "status": "healthy",
            "database": "connected",
            "redis": "connected" if redis_status else "disconnected",
            "version": settings.VERSION
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


# Inclusion des routes
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(tickets.router, prefix="/api/v1/tickets", tags=["tickets"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(monitoring.monitoring_router, prefix="/api/v1/monitoring", tags=["monitoring"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
