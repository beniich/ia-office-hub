"""
config.py — Configuration centralisée (12-Factor App / ISO 27001)
=================================================================
Toutes les valeurs sensibles viennent du fichier .env
JAMAIS codées en dur dans le code source.
"""

import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Paramètres de l'application chargés depuis les variables d'environnement.
    Pydantic valide automatiquement les types et lève une erreur si une variable est manquante.
    """

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "AI Office Hub"
    APP_VERSION: str = "1.0.0"
    ENV: str = "development"          # development | staging | production
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    # ── Sécurité JWT (ISO 27001 A.9) ─────────────────────────────
    SECRET_KEY: str                    # Obligatoire — min 32 chars
    ENCRYPTION_KEY: str                # Obligatoire — pour AES-256
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Base de données ───────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./database.db"
    # Pour PostgreSQL en production :
    # DATABASE_URL=postgresql://user:password@postgres:5432/ai_office_db

    # ── IA / LLM ─────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.3

    # ── OpenOffice / LibreOffice UNO ──────────────────────────────
    LIBREOFFICE_HOST: str = "localhost"
    LIBREOFFICE_PORT: int = 2002
    LIBREOFFICE_TIMEOUT: int = 30

    # ── Stockage fichiers ─────────────────────────────────────────
    UPLOAD_DIR: str = "/app/uploads"
    OUTPUT_DIR: str = "/app/output"
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list = [".docx", ".xlsx", ".pdf", ".csv", ".odt", ".odp", ".ods"]

    # ── CORS (Cross-Origin Resource Sharing) ─────────────────────
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",   # Frontend React dev
        "https://ai-office-hub.com",  # Production
    ]

    # ── Audit & Logs (SOC 2 CC7) ─────────────────────────────────
    LOG_LEVEL: str = "INFO"
    AUDIT_LOG_RETENTION_DAYS: int = 365   # SOC 2 exige 12 mois minimum
    AUDIT_LOG_RETENTION_YEARS: int = 7    # Pour la preuve numérique immuable
    AUDIT_SECRET_SALT: str    # Doit être défini dans .env
    LOG_TO_FILE: bool = True
    LOG_FILE_PATH: str = "/app/logs/audit.log"

    # ── Email (notifications d'alertes de sécurité) ──────────────
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SECURITY_ALERT_EMAIL: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Retourne une instance singleton des paramètres.
    @lru_cache garantit qu'on ne lit le .env qu'une seule fois.
    Usage : settings = get_settings()
    """
    return Settings()


# Instance globale
settings = get_settings()