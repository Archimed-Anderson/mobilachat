#!/usr/bin/env python3
"""
Script de configuration de la base de données
"""
import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def create_database():
    """Crée la base de données PostgreSQL"""
    print("Creation de la base de données...")
    
    # Configuration de connexion
    config = {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',  # Utilisateur admin
        'password': 'postgres'  # Mot de passe admin
    }
    
    try:
        # Connexion à PostgreSQL
        conn = psycopg2.connect(**config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Création de la base de données
        db_name = 'chatbot_free_mobile'
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"OK - Base de données '{db_name}' créée")
        else:
            print(f"OK - Base de données '{db_name}' existe déjà")
        
        # Création de l'utilisateur
        user_name = 'chatbot_user'
        user_password = 'Adan@20102016'
        
        cursor.execute(f"SELECT 1 FROM pg_roles WHERE rolname='{user_name}'")
        user_exists = cursor.fetchone()
        
        if not user_exists:
            cursor.execute(f"CREATE USER {user_name} WITH PASSWORD '{user_password}'")
            print(f"OK - Utilisateur '{user_name}' créé")
        else:
            print(f"OK - Utilisateur '{user_name}' existe déjà")
        
        # Attribution des privilèges
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {user_name}")
        print(f"OK - Privilèges accordés à '{user_name}'")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"ERREUR - Impossible de créer la base de données: {e}")
        return False

def test_connection():
    """Teste la connexion à la base de données"""
    print("Test de connexion...")
    
    config = {
        'host': 'localhost',
        'port': 5432,
        'user': 'chatbot_user',
        'password': 'Adan@20102016',
        'database': 'chatbot_free_mobile'
    }
    
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"OK - Connexion réussie: {version[0][:50]}...")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERREUR - Connexion échouée: {e}")
        return False

def create_tables():
    """Crée les tables via SQLAlchemy"""
    print("Creation des tables...")
    
    try:
        from apps.backend.core.database import engine, Base
        from apps.backend.models import user, conversation, ticket, mastodon_post
        
        # Création de toutes les tables
        Base.metadata.create_all(bind=engine)
        print("OK - Tables créées avec succès")
        return True
        
    except Exception as e:
        print(f"ERREUR - Impossible de créer les tables: {e}")
        return False

def main():
    """Fonction principale"""
    print("=" * 60)
    print("CONFIGURATION DE LA BASE DE DONNEES")
    print("=" * 60)
    
    # Étape 1: Création de la base de données
    if not create_database():
        print("ERREUR - Impossible de continuer sans base de données")
        return False
    
    # Étape 2: Test de connexion
    if not test_connection():
        print("ERREUR - Impossible de se connecter à la base de données")
        return False
    
    # Étape 3: Création des tables
    if not create_tables():
        print("ERREUR - Impossible de créer les tables")
        return False
    
    print("\n" + "=" * 60)
    print("CONFIGURATION TERMINEE AVEC SUCCES")
    print("=" * 60)
    print("Base de données: chatbot_free_mobile")
    print("Utilisateur: chatbot_user")
    print("Tables: users, conversations, messages, tickets, mastodon_posts")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)