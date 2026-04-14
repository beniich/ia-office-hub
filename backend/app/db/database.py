"""
database.py — Gestion de la connexion BDD (SQLAlchemy)
======================================================
Configure SQLAlchemy avec SQLite (ou PostgreSQL en prod).
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# En production, on utiliserait postgresql:// et create_engine(..., pool_size=..., max_overflow=...)
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

async def init_db():
    """Crée les tables si elles n'existent pas (utile pour le dev)."""
    # Dans un vrai projet, on utiliserait Alembic pour les migrations
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency FastAPI pour fournir une session BDD."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()