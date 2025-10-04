#!/usr/bin/env python3
"""
Script de configuration Mastodon
"""
import os
import sys
from pathlib import Path
import requests
from urllib.parse import urljoin

# Ajout du chemin du projet
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from apps.social_monitor.config.mastodon_config import settings


def main():
    """Fonction principale de configuration"""
    print("🐘 Configuration Mastodon pour Free Mobile Social Monitor")
    print("=" * 60)
    
    # Vérification de la configuration existante
    if settings.is_configured():
        print("✅ Configuration Mastodon déjà présente")
        print(f"Instance: {settings.MASTODON_INSTANCE_URL}")
        print(f"Client ID: {settings.MASTODON_CLIENT_ID[:8]}...")
        
        if input("\nVoulez-vous reconfigurer ? (y/N): ").lower() != 'y':
            return
    
    # Configuration de l'instance
    print("\n📋 Configuration de l'instance Mastodon")
    instance_url = input(f"URL de l'instance [{settings.MASTODON_INSTANCE_URL}]: ").strip()
    if not instance_url:
        instance_url = settings.MASTODON_INSTANCE_URL
    
    # Vérification de l'instance
    if not verify_instance(instance_url):
        print("❌ Instance Mastodon invalide ou inaccessible")
        return
    
    # Création de l'application
    print("\n🔧 Création de l'application Mastodon...")
    app_credentials = create_mastodon_app(instance_url)
    
    if not app_credentials:
        print("❌ Échec de la création de l'application")
        return
    
    # Génération du token d'accès
    print("\n🔑 Génération du token d'accès...")
    access_token = generate_access_token(instance_url, app_credentials)
    
    if not access_token:
        print("❌ Échec de la génération du token")
        return
    
    # Mise à jour du fichier .env
    print("\n💾 Mise à jour de la configuration...")
    update_env_file(instance_url, app_credentials, access_token)
    
    print("\n✅ Configuration Mastodon terminée avec succès !")
    print("\n📝 Prochaines étapes :")
    print("1. Vérifiez la configuration dans le fichier .env")
    print("2. Lancez le social monitor : python apps/social-monitor/main.py")
    print("3. Testez la connexion avec les hashtags configurés")


def verify_instance(instance_url: str) -> bool:
    """Vérifie qu'une instance Mastodon est accessible"""
    try:
        # Test de l'API de l'instance
        api_url = urljoin(instance_url, "/api/v1/instance")
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Instance trouvée : {data.get('title', 'Mastodon')}")
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return False


def create_mastodon_app(instance_url: str) -> dict:
    """Crée une application Mastodon"""
    try:
        from mastodon import Mastodon
        
        # Nom de l'application
        app_name = "Free Mobile Social Monitor"
        app_website = "https://github.com/your-username/chatbot-free-mobile"
        
        # Création de l'application
        app_credentials = Mastodon.create_app(
            app_name,
            api_base_url=instance_url,
            website=app_website
        )
        
        print(f"✅ Application créée : {app_credentials[0]}")
        return {
            "client_id": app_credentials[0],
            "client_secret": app_credentials[1]
        }
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'application : {e}")
        return None


def generate_access_token(instance_url: str, app_credentials: dict) -> str:
    """Génère un token d'accès"""
    try:
        from mastodon import Mastodon
        
        # Création du client Mastodon
        mastodon = Mastodon(
            client_id=app_credentials["client_id"],
            client_secret=app_credentials["client_secret"],
            api_base_url=instance_url
        )
        
        # Demande des informations de connexion
        print("\n🔐 Connexion à votre compte Mastodon")
        email = input("Email : ").strip()
        password = input("Mot de passe : ").strip()
        
        # Génération du token
        access_token = mastodon.log_in(
            username=email,
            password=password,
            scopes=['read', 'write', 'follow', 'push']
        )
        
        print("✅ Token d'accès généré")
        return access_token
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération du token : {e}")
        return None


def update_env_file(instance_url: str, app_credentials: dict, access_token: str):
    """Met à jour le fichier .env"""
    env_file = Path(".env")
    
    # Lecture du fichier .env existant
    env_content = ""
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.read()
    
    # Mise à jour des variables Mastodon
    mastodon_vars = {
        "MASTODON_INSTANCE_URL": instance_url,
        "MASTODON_CLIENT_ID": app_credentials["client_id"],
        "MASTODON_CLIENT_SECRET": app_credentials["client_secret"],
        "MASTODON_ACCESS_TOKEN": access_token
    }
    
    # Mise à jour du contenu
    for var_name, var_value in mastodon_vars.items():
        if f"{var_name}=" in env_content:
            # Mise à jour de la variable existante
            import re
            pattern = rf"^{var_name}=.*$"
            replacement = f"{var_name}={var_value}"
            env_content = re.sub(pattern, replacement, env_content, flags=re.MULTILINE)
        else:
            # Ajout de la nouvelle variable
            env_content += f"\n{var_name}={var_value}\n"
    
    # Sauvegarde du fichier
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"✅ Fichier .env mis à jour")


if __name__ == "__main__":
    main()


