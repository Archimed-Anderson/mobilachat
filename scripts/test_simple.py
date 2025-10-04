#!/usr/bin/env python3
"""
Script de test simple sans base de données
"""
import sys
import time
import httpx
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_redis():
    """Teste Redis"""
    try:
        print("Test de Redis...")
        import redis
        r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
        r.ping()
        print("OK - Redis fonctionne")
        return True
    except Exception as e:
        print(f"ERREUR - Redis : {e}")
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
        print(f"  Intent detecte : {intent}")
        
        # Test analyse de sentiment
        analyzer = SentimentAnalyzer()
        sentiment = analyzer.analyze_sentiment("Je suis tres satisfait du service")
        print(f"  Sentiment analyse : {sentiment}")
        
        print("OK - Modeles IA fonctionnent")
        return True
    except Exception as e:
        print(f"ERREUR - Modeles IA : {e}")
        return False

def test_ai_engine():
    """Teste l'AI Engine"""
    try:
        print("Test de l'AI Engine...")
        response = httpx.get("http://localhost:8001/health", timeout=5.0)
        if response.status_code == 200:
            print("OK - AI Engine fonctionne")
            return True
        else:
            print(f"ERREUR - AI Engine HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"ERREUR - AI Engine : {e}")
        return False

def test_backend():
    """Teste le backend FastAPI"""
    try:
        print("Test du Backend FastAPI...")
        response = httpx.get("http://localhost:8000/health", timeout=5.0)
        if response.status_code == 200:
            print("OK - Backend fonctionne")
            return True
        else:
            print(f"ERREUR - Backend HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"ERREUR - Backend : {e}")
        return False

def test_frontend():
    """Teste le frontend Streamlit"""
    try:
        print("Test du Frontend Streamlit...")
        response = httpx.get("http://localhost:8501", timeout=5.0)
        if response.status_code == 200:
            print("OK - Frontend fonctionne")
            return True
        else:
            print(f"ERREUR - Frontend HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"ERREUR - Frontend : {e}")
        return False

def main():
    """Fonction principale"""
    print("=" * 60)
    print("TEST SIMPLE DE L'APPLICATION")
    print("=" * 60)
    
    tests = [
        ("Redis", test_redis),
        ("Modeles IA", test_ai_models),
        ("AI Engine", test_ai_engine),
        ("Backend", test_backend),
        ("Frontend", test_frontend),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        result = test_func()
        results.append((name, result))
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("RESUME DES TESTS")
    print("=" * 60)
    
    success_count = 0
    for name, result in results:
        status = "OK" if result else "ERREUR"
        print(f"{name:20} : {status}")
        if result:
            success_count += 1
    
    print(f"\nTests reussis : {success_count}/{len(results)}")
    
    if success_count == len(results):
        print("\nTous les tests sont passes ! L'application est prete.")
    else:
        print(f"\n{len(results) - success_count} test(s) ont echoue.")

if __name__ == "__main__":
    main()
