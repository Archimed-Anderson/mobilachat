"""
Tests pour l'AI Engine
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from apps.ai_engine.api_simple import app

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

def test_intent_detection():
    """Test de la détection d'intention"""
    response = client.post(
        "/api/v1/intent",
        json={"text": "Je veux changer mon forfait"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "intent" in data
    assert "confidence" in data
    assert data["intent"] == "plan_change"

def test_sentiment_analysis():
    """Test de l'analyse de sentiment"""
    response = client.post(
        "/api/v1/sentiment",
        json={"text": "Je suis satisfait du service"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "sentiment" in data
    assert "confidence" in data
    assert data["sentiment"] == "positive"

def test_chat():
    """Test de l'endpoint de chat"""
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Bonjour, j'ai un problème",
            "context": {}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "intent" in data
    assert "sentiment" in data
    assert "confidence" in data
