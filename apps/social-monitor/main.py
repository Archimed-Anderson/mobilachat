"""
Application principale du social monitor
"""
import asyncio
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path

# Ajout du chemin du projet
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from .config.mastodon_config import settings
from .collectors.mastodon_collector import MastodonCollector
from .utils.api_client import api_client

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('social_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class SocialMonitorApp:
    def __init__(self):
        self.collector = MastodonCollector()
        self.is_running = False
        self.shutdown_event = asyncio.Event()
    
    async def start(self):
        """Démarre l'application"""
        try:
            logger.info("🚀 Démarrage du Social Monitor Free Mobile")
            
            # Initialisation du collecteur
            if not await self.collector.initialize():
                logger.error("❌ Échec de l'initialisation du collecteur")
                return False
            
            # Test de connexion aux services
            await self._test_services()
            
            # Configuration des signaux d'arrêt
            self._setup_signal_handlers()
            
            # Démarrage de la surveillance
            self.is_running = True
            await self.collector.start_monitoring()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du démarrage: {e}")
            return False
    
    async def stop(self):
        """Arrête l'application"""
        try:
            logger.info("🛑 Arrêt du Social Monitor...")
            
            self.is_running = False
            await self.collector.stop_monitoring()
            
            logger.info("✅ Social Monitor arrêté")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'arrêt: {e}")
    
    async def _test_services(self):
        """Teste la connexion aux services"""
        logger.info("🔍 Test des services...")
        
        # Test du collecteur Mastodon
        if not await self.collector.test_connection():
            raise Exception("Connexion Mastodon échouée")
        
        # Test des APIs
        try:
            health = await api_client.health_check()
            if health["overall"] != "healthy":
                logger.warning("⚠️ Certains services ne sont pas disponibles")
            else:
                logger.info("✅ Tous les services sont disponibles")
        except Exception as e:
            logger.warning(f"⚠️ Impossible de vérifier la santé des services: {e}")
    
    def _setup_signal_handlers(self):
        """Configure les gestionnaires de signaux"""
        def signal_handler(signum, frame):
            logger.info(f"Signal {signum} reçu, arrêt en cours...")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def get_status(self) -> dict:
        """Retourne le statut de l'application"""
        return {
            "is_running": self.is_running,
            "collector_stats": self.collector.get_stats(),
            "timestamp": datetime.now().isoformat()
        }
    
    async def run_forever(self):
        """Exécute l'application en boucle"""
        try:
            while self.is_running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Interruption clavier détectée")
        finally:
            await self.stop()


async def main():
    """Fonction principale"""
    app = SocialMonitorApp()
    
    try:
        # Démarrage de l'application
        if await app.start():
            logger.info("✅ Social Monitor démarré avec succès")
            
            # Exécution en boucle
            await app.run_forever()
        else:
            logger.error("❌ Échec du démarrage")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        sys.exit(1)


def run():
    """Point d'entrée pour l'exécution"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()


