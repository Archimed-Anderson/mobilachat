"""
Configuration de la base de données
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Créer l'engine de base de données avec encodage UTF-8
database_url = str(settings.DATABASE_URL)
if "?" not in database_url:
    database_url += "?client_encoding=utf8"

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)

# Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()


def get_db():
    """Dependency pour obtenir la DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Crée toutes les tables"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Supprime toutes les tables"""
    Base.metadata.drop_all(bind=engine)


