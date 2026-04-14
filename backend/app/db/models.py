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