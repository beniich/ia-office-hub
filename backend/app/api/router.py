"""
router.py — Agrégation de tous les routeurs FastAPI
====================================================
Chaque module fonctionnel a son propre router qui est enregistré ici.
"""

from fastapi import APIRouter

from app.api.endpoints.documents import router as documents_router
from app.api.endpoints.ai_agent import router as ai_router
from app.api.endpoints.auth import router as auth_router

api_router = APIRouter()

# Auth (login, token refresh, logout)
api_router.include_router(auth_router, prefix="/auth", tags=["Authentification"])

# Gestion documentaire
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])

# Agent IA (diagnostics, génération PPT)
api_router.include_router(ai_router, prefix="/ai", tags=["Agent IA"])