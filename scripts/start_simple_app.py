#!/usr/bin/env python3
"""
Script de démarrage simplifié de l'application
"""
import sys
import os
import subprocess
import time
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def start_backend():
    """Démarre le backend FastAPI simplifié"""
    print("Demarrage du Backend...")
    try:
        process = subprocess.Popen([
            sys.executable, "apps/backend/main_simple.py"
        ], cwd=project_root)
        print("OK - Backend demarre sur http://localhost:8000")
        return process
    except Exception as e:
        print(f"ERREUR demarrage backend: {e}")
        return None

def start_ai_engine():
    """Démarre l'AI Engine simplifié"""
    print("Demarrage de l'AI Engine...")
    try:
        process = subprocess.Popen([
            sys.executable, "apps/ai-engine/api_simple.py"
        ], cwd=project_root)
        print("OK - AI Engine demarre sur http://localhost:8001")
        return process
    except Exception as e:
        print(f"ERREUR demarrage AI Engine: {e}")
        return None

def start_frontend():
    """Démarre le frontend Streamlit"""
    print("Demarrage du Frontend...")
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run",
            "apps/frontend/app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], cwd=project_root)
        print("OK - Frontend demarre sur http://localhost:8501")
        return process
    except Exception as e:
        print(f"ERREUR demarrage frontend: {e}")
        return None

def test_services():
    """Teste les services"""
    print("Test des services...")
    import httpx
    import time

    # Attendre que les services démarrent
    time.sleep(3)

    services = {
        "Backend": "http://localhost:8000/health",
        "AI Engine": "http://localhost:8001/health",
        "Frontend": "http://localhost:8501"
    }

    for name, url in services.items():
        try:
            response = httpx.get(url, timeout=5.0)
            if response.status_code == 200:
                print(f"OK - {name}: OK")
            else:
                print(f"WARNING - {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"ERREUR - {name}: {e}")

def test_chat_functionality():
    """Teste la fonctionnalité de chat"""
    print("\nTest de la fonctionnalite de chat...")
    import httpx
    
    try:
        # Test du backend
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
            print(f"OK - Backend chat: {data['response'][:50]}...")
        else:
            print(f"ERREUR - Backend chat: HTTP {response.status_code}")
    except Exception as e:
        print(f"ERREUR - Backend chat: {e}")
    
    try:
        # Test de l'AI Engine
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
            print(f"OK - AI Engine chat: {data['response'][:50]}...")
            print(f"  Intent: {data['intent']}, Sentiment: {data['sentiment']}")
        else:
            print(f"ERREUR - AI Engine chat: HTTP {response.status_code}")
    except Exception as e:
        print(f"ERREUR - AI Engine chat: {e}")

def main():
    """Fonction principale"""
    print("=" * 60)
    print("MOBILACHAT - DEMARRAGE SIMPLIFIE")
    print("=" * 60)

    processes = []

    try:
        # Démarrage du backend
        backend_process = start_backend()
        if backend_process:
            processes.append(("Backend", backend_process))
        time.sleep(3)

        # Démarrage de l'AI Engine
        ai_engine_process = start_ai_engine()
        if ai_engine_process:
            processes.append(("AI Engine", ai_engine_process))
        time.sleep(3)

        # Démarrage du frontend
        frontend_process = start_frontend()
        if frontend_process:
            processes.append(("Frontend", frontend_process))
        time.sleep(5)

        # Test des services
        test_services()
        
        # Test de la fonctionnalité de chat
        test_chat_functionality()

        print("\n" + "=" * 60)
        print("SERVICES DEMARRES")
        print("=" * 60)
        print("Backend API:     http://localhost:8000")
        print("Documentation:   http://localhost:8000/docs")
        print("AI Engine:       http://localhost:8001")
        print("AI Docs:         http://localhost:8001/docs")
        print("Frontend:        http://localhost:8501")
        print("=" * 60)
        print("Appuyez sur Ctrl+C pour arreter tous les services")
        print("=" * 60)

        # Attente
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nArret des services...")
        for name, process in processes:
            try:
                process.terminate()
                print(f"OK - {name} arrete")
            except:
                print(f"ERREUR arret {name}")

        print("OK - Tous les services arretes")

if __name__ == "__main__":
    main()
