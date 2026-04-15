"""
models.py — Modèles SQLAlchemy (Mapping Object-Relationnel)
===========================================================
Représente la structure de la base de données en Python.
Doit correspondre parfaitement à schema.sql.
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    
    documents = relationship("Document", back_populates="project")
    logs = relationship("AILog", back_populates="project")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    filename = Column(String)
    file_path = Column(String)  # Chemin vers le fichier chiffré
    file_type = Column(String)
    status = Column(String)
    
    project = relationship("Project", back_populates="documents")

class AILog(Base):
    __tablename__ = "ai_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    action_performed = Column(String)
    status = Column(String)
    timestamp = Column(DateTime, server_default=func.now())
    
    project = relationship("Project", back_populates="logs")

class AuditLog(Base):
    """
    Cadre de Gouvernance de la Donnée (ISO 27001 / SOC 2)
    Système de Preuve Numérique Immuable.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Identité & Localisation
    user_id = Column(String, index=True, nullable=False)
    organization_id = Column(String, index=True)
    ip_address = Column(String(45))
    user_agent = Column(String)
    request_id = Column(String, unique=True, index=True)
    session_id = Column(String)
    
    # Classification & Sévérité
    category = Column(String, index=True)      # AUTH, DATA_ACCESS, CONFIG_CHANGE, etc.
    severity = Column(String)                  # INFO, WARNING, ERROR, CRITICAL
    classification = Column(String)            # PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
    
    # Données de l'action
    action_name = Column(String, index=True)
    previous_value = Column(String)            # JSON string
    new_value = Column(String)                 # JSON string
    
    # Contrôle d'Intégrité (Anti-tamper)
    integrity_hash = Column(String, nullable=False)
    
    # Cycle de Vie
    created_at = Column(DateTime, server_default=func.now(), index=True)
    retention_until = Column(DateTime, nullable=False)