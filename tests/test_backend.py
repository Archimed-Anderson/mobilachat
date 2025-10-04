"""
Tests pour le backend FastAPI
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from apps.backend.main_simple import app

client = TestClient(app)

def test_health_check():
    """Test du health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "message" in data

def test_root():
    """Test de la route racine"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data

def test_chat_message():
    """Test de l'endpoint de chat"""
    response = client.post(
        "/api/v1/chat/message",
        json={
            "message": "Bonjour, j'ai un problème",
            "conversation_id": None
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "conversation_id" in data
    assert "intent" in data
    assert "sentiment" in data

def test_analytics():
    """Test de l'endpoint analytics"""
    response = client.get("/api/v1/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "total_conversations" in data
    assert "total_messages" in data
    assert "total_tickets" in data

def test_tickets():
    """Test de l'endpoint tickets"""
    response = client.get("/api/v1/tickets")
    assert response.status_code == 200
    data = response.json()
    assert "tickets" in data
    assert "total" in data
