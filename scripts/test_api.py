#!/usr/bin/env python3
"""
Script de test des API
"""
import httpx
import json

def test_backend_chat():
    """Teste l'API de chat du backend"""
    print("Test de l'API de chat du backend...")
    try:
        response = httpx.post(
            "http://localhost:8000/api/v1/chat/message",
            json={
                "message": "Bonjour, j'ai un problème avec mon forfait",
                "conversation_id": None
            },
            timeout=10.0
        )
        if response.status_code == 200:
            data = response.json()
            print(f"OK - Backend chat: {data['response']}")
            print(f"  Conversation ID: {data['conversation_id']}")
            print(f"  Intent: {data['intent']}")
            print(f"  Sentiment: {data['sentiment']}")
            return True
        else:
            print(f"ERREUR - Backend chat: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"ERREUR - Backend chat: {e}")
        return False

def test_ai_engine_chat():
    """Teste l'API de chat de l'AI Engine"""
    print("\nTest de l'API de chat de l'AI Engine...")
    try:
        response = httpx.post(
            "http://localhost:8001/api/v1/chat",
            json={
                "message": "Bonjour, j'ai un problème avec mon forfait",
                "context": {}
            },
            timeout=10.0
        )
        if response.status_code == 200:
            data = response.json()
            print(f"OK - AI Engine chat: {data['response']}")
            print(f"  Intent: {data['intent']}")
            print(f"  Sentiment: {data['sentiment']}")
            print(f"  Confidence: {data['confidence']}")
            return True
        else:
            print(f"ERREUR - AI Engine chat: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"ERREUR - AI Engine chat: {e}")
        return False

def test_ai_engine_intent():
    """Teste l'API de détection d'intention"""
    print("\nTest de l'API de détection d'intention...")
    try:
        response = httpx.post(
            "http://localhost:8001/api/v1/intent",
            json={
                "text": "Je veux changer mon forfait"
            },
            timeout=10.0
        )
        if response.status_code == 200:
            data = response.json()
            print(f"OK - Intent detection: {data['intent']} (confidence: {data['confidence']})")
            return True
        else:
            print(f"ERREUR - Intent detection: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"ERREUR - Intent detection: {e}")
        return False

def test_ai_engine_sentiment():
    """Teste l'API d'analyse de sentiment"""
    print("\nTest de l'API d'analyse de sentiment...")
    try:
        response = httpx.post(
            "http://localhost:8001/api/v1/sentiment",
            json={
                "text": "Je suis très satisfait du service"
            },
            timeout=10.0
        )
        if response.status_code == 200:
            data = response.json()
            print(f"OK - Sentiment analysis: {data['sentiment']} (confidence: {data['confidence']})")
            return True
        else:
            print(f"ERREUR - Sentiment analysis: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"ERREUR - Sentiment analysis: {e}")
        return False

def test_analytics():
    """Teste l'API d'analytics"""
    print("\nTest de l'API d'analytics...")
    try:
        response = httpx.get("http://localhost:8000/api/v1/analytics", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            print(f"OK - Analytics: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"ERREUR - Analytics: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"ERREUR - Analytics: {e}")
        return False

def main():
    """Fonction principale"""
    print("=" * 60)
    print("TEST DES API MOBILACHAT")
    print("=" * 60)
    
    tests = [
        ("Backend Chat", test_backend_chat),
        ("AI Engine Chat", test_ai_engine_chat),
        ("Intent Detection", test_ai_engine_intent),
        ("Sentiment Analysis", test_ai_engine_sentiment),
        ("Analytics", test_analytics),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
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
        print("\nTous les tests sont passes ! L'application fonctionne correctement.")
    else:
        print(f"\n{len(results) - success_count} test(s) ont echoue.")

if __name__ == "__main__":
    main()
