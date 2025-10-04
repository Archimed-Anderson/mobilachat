"""
Configuration des tests pytest
"""
import pytest
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def test_env():
    """Configuration de l'environnement de test"""
    import os
    os.environ.update({
        "SECRET_KEY": "test-secret-key",
        "JWT_ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "DATABASE_URL": "sqlite:///./test.db",
        "REDIS_URL": "redis://localhost:6379",
        "DEBUG": "true"
    })
    return os.environ
