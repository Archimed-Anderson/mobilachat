"""
Tests simples pour l'application
"""
import pytest
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test des imports principaux"""
    try:
        from apps.backend.main_simple import app as backend_app
        assert backend_app is not None
    except ImportError as e:
        pytest.fail(f"Backend import failed: {e}")
    
    try:
        from apps.ai_engine.api_simple import app as ai_app
        assert ai_app is not None
    except ImportError as e:
        pytest.fail(f"AI Engine import failed: {e}")

def test_backend_health():
    """Test du health check du backend"""
    from fastapi.testclient import TestClient
    from apps.backend.main_simple import app
    
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_ai_engine_health():
    """Test du health check de l'AI Engine"""
    from fastapi.testclient import TestClient
    from apps.ai_engine.api_simple import app
    
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_backend_chat():
    """Test de l'endpoint de chat du backend"""
    from fastapi.testclient import TestClient
    from apps.backend.main_simple import app
    
    client = TestClient(app)
    response = client.post(
        "/api/v1/chat/message",
        json={
            "message": "Test message",
            "conversation_id": None
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "conversation_id" in data

def test_ai_engine_chat():
    """Test de l'endpoint de chat de l'AI Engine"""
    from fastapi.testclient import TestClient
    from apps.ai_engine.api_simple import app
    
    client = TestClient(app)
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Test message",
            "context": {}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "intent" in data
    assert "sentiment" in data

def test_ai_engine_intent():
    """Test de la détection d'intention"""
    from fastapi.testclient import TestClient
    from apps.ai_engine.api_simple import app
    
    client = TestClient(app)
    response = client.post(
        "/api/v1/intent",
        json={"text": "Je veux changer mon forfait"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "intent" in data
    assert "confidence" in data

def test_ai_engine_sentiment():
    """Test de l'analyse de sentiment"""
    from fastapi.testclient import TestClient
    from apps.ai_engine.api_simple import app
    
    client = TestClient(app)
    response = client.post(
        "/api/v1/sentiment",
        json={"text": "Je suis satisfait"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "sentiment" in data
    assert "confidence" in data
