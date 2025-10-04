#!/usr/bin/env python3
"""
Script de test simple pour vérifier les services
"""
import sys
import time
import subprocess
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_backend_import():
    """Test d'import du backend"""
    print("Test d'import du backend...")
    try:
        from apps.backend.main import app
        print("OK - Backend importe avec succes")
        return True
    except Exception as e:
        print(f"ERREUR - Import backend: {e}")
        return False

def test_ai_engine_import():
    """Test d'import de l'AI Engine"""
    print("Test d'import de l'AI Engine...")
    try:
        import sys
        sys.path.append('apps/ai-engine')
        from config.settings import settings
        from rag.vector_store import VectorStore
        print("OK - AI Engine importe avec succes")
        return True
    except Exception as e:
        print(f"ERREUR - Import AI Engine: {e}")
        return False

def test_frontend_import():
    """Test d'import du frontend"""
    print("Test d'import du frontend...")
    try:
        from apps.frontend.config.settings import settings
        print("OK - Frontend importe avec succes")
        return True
    except Exception as e:
        print(f"ERREUR - Import frontend: {e}")
        return False

def test_database_connection():
    """Test de connexion à la base de données"""
    print("Test de connexion a la base de données...")
    try:
        from apps.backend.core.database import engine
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("OK - Connexion base de données reussie")
            return True
    except Exception as e:
        print(f"ERREUR - Connexion base de données: {e}")
        return False

def start_backend_test():
    """Démarre le backend en mode test"""
    print("Demarrage du backend en mode test...")
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "apps.backend.main:app", 
            "--host", "127.0.0.1", 
            "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Attendre un peu
        time.sleep(3)
        
        # Vérifier si le processus tourne
        if process.poll() is None:
            print("OK - Backend demarre")
            process.terminate()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"ERREUR - Backend n'a pas demarre: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"ERREUR - Demarrage backend: {e}")
        return False

def main():
    """Fonction principale"""
    print("=" * 60)
    print("TEST DES SERVICES FREE MOBILE CHATBOT")
    print("=" * 60)
    
    tests = [
        ("Import Backend", test_backend_import),
        ("Import AI Engine", test_ai_engine_import),
        ("Import Frontend", test_frontend_import),
        ("Connexion DB", test_database_connection),
        ("Demarrage Backend", start_backend_test)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"ERREUR dans {name}: {e}")
            results.append((name, False))
        print()
    
    # Résumé
    print("=" * 60)
    print("RESULTATS DES TESTS")
    print("=" * 60)
    
    passed = 0
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status} - {name}")
        if result:
            passed += 1
    
    print(f"\nScore: {passed}/{len(results)} tests reussis")
    
    if passed == len(results):
        print("Tous les tests sont passes !")
        return True
    else:
        print("Certains tests ont echoue")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)