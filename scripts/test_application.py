#!/usr/bin/env python3
"""
Script de test complet de l'application
"""
import sys
import time
import httpx
import subprocess
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_backend():
    """Teste le backend FastAPI"""
    try:
        print("Test du Backend FastAPI...")
        response = httpx.get("http://localhost:8000/health", timeout=5.0)
        if response.status_code == 200:
            print("✓ Backend OK")
            return True
        else:
            print(f"✗ Backend erreur HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Backend erreur : {e}")
        return False

def test_ai_engine():
    """Teste l'AI Engine"""
    try:
        print("Test de l'AI Engine...")
        response = httpx.get("http://localhost:8001/health", timeout=5.0)
        if response.status_code == 200:
            print("✓ AI Engine OK")
            return True
        else:
            print(f"✗ AI Engine erreur HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ AI Engine erreur : {e}")
        return False

def test_frontend():
    """Teste le frontend Streamlit"""
    try:
        print("Test du Frontend Streamlit...")
        response = httpx.get("http://localhost:8501", timeout=5.0)
        if response.status_code == 200:
            print("✓ Frontend OK")
            return True
        else:
            print(f"✗ Frontend erreur HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Frontend erreur : {e}")
        return False

def test_database():
    """Teste la base de données"""
    try:
        print("Test de la base de données...")
        from apps.backend.core.database import engine
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✓ Base de données OK")
            return True
    except Exception as e:
        print(f"✗ Base de données erreur : {e}")
        return False

def test_redis():
    """Teste Redis"""
    try:
        print("Test de Redis...")
        import redis
        from apps.backend.core.config import settings
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        r.ping()
        print("✓ Redis OK")
        return True
    except Exception as e:
        print(f"✗ Redis erreur : {e}")
        return False

def test_ai_models():
    """Teste les modèles IA"""
    try:
        print("Test des modèles IA...")
        from apps.ai_engine.models.intent_detector import IntentDetector
        from apps.ai_engine.models.sentiment_analyzer import SentimentAnalyzer
        
        # Test détection d'intention
        detector = IntentDetector()
        intent = detector.detect_intent("Bonjour, j'ai un problème avec mon forfait")
        print(f"  Intent détecté : {intent}")
        
        # Test analyse de sentiment
        analyzer = SentimentAnalyzer()
        sentiment = analyzer.analyze_sentiment("Je suis très satisfait du service")
        print(f"  Sentiment analysé : {sentiment}")
        
        print("✓ Modèles IA OK")
        return True
    except Exception as e:
        print(f"✗ Modèles IA erreur : {e}")
        return False

def test_api_endpoints():
    """Teste les endpoints API"""
    try:
        print("Test des endpoints API...")
        
        # Test endpoint chat
        response = httpx.post(
            "http://localhost:8000/api/v1/chat/message",
            json={
                "message": "Bonjour, j'ai une question sur mon forfait",
                "conversation_id": None
            },
            timeout=10.0
        )
        if response.status_code == 200:
            print("  ✓ Endpoint chat OK")
        else:
            print(f"  ✗ Endpoint chat erreur {response.status_code}")
        
        # Test endpoint analytics
        response = httpx.get("http://localhost:8000/api/v1/analytics", timeout=5.0)
        if response.status_code == 200:
            print("  ✓ Endpoint analytics OK")
        else:
            print(f"  ✗ Endpoint analytics erreur {response.status_code}")
        
        print("✓ Endpoints API OK")
        return True
    except Exception as e:
        print(f"✗ Endpoints API erreur : {e}")
        return False

def main():
    """Fonction principale"""
    print("=" * 60)
    print("TEST COMPLET DE L'APPLICATION")
    print("=" * 60)
    
    tests = [
        ("Base de données", test_database),
        ("Redis", test_redis),
        ("Backend", test_backend),
        ("AI Engine", test_ai_engine),
        ("Frontend", test_frontend),
        ("Modèles IA", test_ai_models),
        ("Endpoints API", test_api_endpoints),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        result = test_func()
        results.append((name, result))
        time.sleep(1)  # Pause entre les tests
    
    print("\n" + "=" * 60)
    print("RESUME DES TESTS")
    print("=" * 60)
    
    success_count = 0
    for name, result in results:
        status = "✓ OK" if result else "✗ ERREUR"
        print(f"{name:20} : {status}")
        if result:
            success_count += 1
    
    print(f"\nTests réussis : {success_count}/{len(results)}")
    
    if success_count == len(results):
        print("\n🎉 Tous les tests sont passés ! L'application est prête.")
    else:
        print(f"\n⚠️  {len(results) - success_count} test(s) ont échoué. Vérifiez la configuration.")

if __name__ == "__main__":
    main()
