#!/usr/bin/env python3
"""
Script de démarrage final pour Free Mobile Chatbot
"""
import sys
import time
import subprocess
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def start_backend():
    """Démarre le backend FastAPI"""
    print("Demarrage du Backend...")
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "apps.backend.main:app", 
            "--host", "127.0.0.1", 
            "--port", "8000",
            "--reload"
        ], cwd=project_root)
        print("OK - Backend demarre sur http://127.0.0.1:8000")
        return process
    except Exception as e:
        print(f"ERREUR demarrage backend: {e}")
        return None

def start_ai_engine():
    """Démarre l'AI Engine"""
    print("Demarrage de l'AI Engine...")
    try:
        process = subprocess.Popen([
            sys.executable, "apps/ai-engine/api.py"
        ], cwd=project_root)
        print("OK - AI Engine demarre sur http://127.0.0.1:8001")
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
            "--server.address", "127.0.0.1"
        ], cwd=project_root)
        print("OK - Frontend demarre sur http://127.0.0.1:8501")
        return process
    except Exception as e:
        print(f"ERREUR demarrage frontend: {e}")
        return None

def test_services():
    """Teste les services"""
    print("Test des services...")
    import httpx
    
    services = {
        "Backend": "http://127.0.0.1:8000/health",
        "AI Engine": "http://127.0.0.1:8001/health",
        "Frontend": "http://127.0.0.1:8501"
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

def main():
    """Fonction principale"""
    print("=" * 60)
    print("FREE MOBILE CHATBOT - DEMARRAGE FINAL")
    print("=" * 60)
    
    processes = []
    
    try:
        # Démarrage des services
        backend_process = start_backend()
        if backend_process:
            processes.append(("Backend", backend_process))
        
        time.sleep(3)
        
        ai_process = start_ai_engine()
        if ai_process:
            processes.append(("AI Engine", ai_process))
        
        time.sleep(3)
        
        frontend_process = start_frontend()
        if frontend_process:
            processes.append(("Frontend", frontend_process))
        
        time.sleep(5)
        
        # Test des services
        test_services()
        
        print("\n" + "=" * 60)
        print("SERVICES DEMARRES")
        print("=" * 60)
        print("Backend API:     http://127.0.0.1:8000")
        print("Documentation:   http://127.0.0.1:8000/docs")
        print("AI Engine:       http://127.0.0.1:8001")
        print("Frontend:        http://127.0.0.1:8501")
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
