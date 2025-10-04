#!/usr/bin/env python3
"""
Script de configuration de la base de données
"""
import os
import sys
import subprocess
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def create_env_file():
    """Crée le fichier .env avec les credentials fournis"""
    env_content = """# Base de données PostgreSQL (utiliser Supabase)
USE_SUPABASE=true
SUPABASE_DB_URL=postgresql://postgres.Adan%4020102016@db.dgyjxlckgzuluxgnwnnz.supabase.co:5432/postgres

# Supabase
SUPABASE_URL=https://dgyjxlckgzuluxgnwnnz.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRneWp4bGNrZ3p1bHV4Z253bm56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk1NzkwNDksImV4cCI6MjA3NTE1NTA0OX0.Me_NIxx8rZR7459G5h2E2aWeoUipRo9gFYeRnuRvb64
SUPABASE_SERVICE_ROLE_KEY=sb_secret_opVHouTwBbv1mF8kq3PM6w_YSMsMDiS

# Mastodon
MASTODON_INSTANCE_URL=https://mastodon.social
MASTODON_CLIENT_ID=_KU2v_HHfbryK3G4OHEZFemWRaFXwSb2W9dvraZ7m54
MASTODON_CLIENT_SECRET=ItxCYDtILkNdMcAEFaln4hBUWa-bYrOibIWxqlrBh5w
MASTODON_ACCESS_TOKEN=QKoEtaWSFuZvPrxK4z7381x1rrS_7IFAfQH_P1Bt4Y

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Sécurité
SECRET_KEY=super-secret-key-for-mobiliachat-min-32-chars-2024
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# IA
LLM_MODEL_NAME=microsoft/DialoGPT-medium
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Debug
DEBUG=true
"""
    
    env_file = project_root / ".env"
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print(f"Fichier .env créé : {env_file}")

def test_database_connection():
    """Teste la connexion à la base de données"""
    try:
        from apps.backend.core.config import settings
        from apps.backend.core.database import engine
        
        print("Test de connexion à la base de données...")
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("OK - Connexion PostgreSQL reussie")
            return True
    except Exception as e:
        print(f"ERREUR - Connexion PostgreSQL : {e}")
        return False

def test_redis_connection():
    """Teste la connexion Redis"""
    try:
        import redis
        from apps.backend.core.config import settings
        
        print("Test de connexion Redis...")
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        r.ping()
        print("OK - Connexion Redis reussie")
        return True
    except Exception as e:
        print(f"ERREUR - Connexion Redis : {e}")
        return False

def create_tables():
    """Crée les tables dans la base de données"""
    try:
        from apps.backend.core.database import create_tables
        print("Création des tables...")
        create_tables()
        print("OK - Tables creees avec succes")
        return True
    except Exception as e:
        print(f"ERREUR - Creation des tables : {e}")
        return False

def main():
    """Fonction principale"""
    print("=" * 60)
    print("CONFIGURATION DE LA BASE DE DONNEES")
    print("=" * 60)
    
    # 1. Créer le fichier .env
    create_env_file()
    
    # 2. Tester les connexions
    db_ok = test_database_connection()
    redis_ok = test_redis_connection()
    
    if db_ok and redis_ok:
        # 3. Créer les tables
        create_tables()
        
        print("\n" + "=" * 60)
        print("CONFIGURATION TERMINEE")
        print("=" * 60)
        print("OK - Fichier .env cree")
        print("OK - Connexion PostgreSQL OK")
        print("OK - Connexion Redis OK")
        print("OK - Tables creees")
        print("\nVous pouvez maintenant démarrer l'application avec :")
        print("python scripts/start_final.py")
    else:
        print("\n" + "=" * 60)
        print("ERREURS DE CONFIGURATION")
        print("=" * 60)
        if not db_ok:
            print("ERREUR - PostgreSQL n'est pas accessible")
            print("  Verifiez que PostgreSQL est demarre et accessible")
        if not redis_ok:
            print("ERREUR - Redis n'est pas accessible")
            print("  Verifiez que Redis est demarre et accessible")

if __name__ == "__main__":
    main()
