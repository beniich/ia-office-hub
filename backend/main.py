"""
main.py — Point d'entrée FastAPI (Enterprise Grade)
====================================================
- CORS configuré pour le frontend React
- Middleware de logging/audit sur chaque requête
- Gestion globale des erreurs (ne pas exposer les stack traces en prod)
- Documentation OpenAPI désactivée en production (SOC 2)
- Health check pour le monitoring Docker/Kubernetes
"""

import time
import uuid
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.router import api_router
from app.db.database import init_db

# ─────────────────────────────────────────────
# Logging structuré (SOC 2 CC7.2 — Monitoring)
# ─────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
logger = logging.getLogger("ai_office_hub")


# ─────────────────────────────────────────────
# Lifecycle : startup / shutdown
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialisation de la base de données au démarrage."""
    logger.info(f"[STARTUP] {settings.APP_NAME} v{settings.APP_VERSION} — ENV={settings.ENV}")
    await init_db()
    logger.info("[STARTUP] Base de données initialisée.")
    yield
    logger.info("[SHUTDOWN] Application arrêtée proprement.")


# ─────────────────────────────────────────────
# Création de l'application FastAPI
# ─────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Plateforme IA de gestion documentaire — ISO 27001 / SOC 2",
    # Désactiver la doc en production (ne pas exposer l'API publiquement)
    docs_url="/docs" if settings.ENV != "production" else None,
    redoc_url="/redoc" if settings.ENV != "production" else None,
    openapi_url="/openapi.json" if settings.ENV != "production" else None,
    lifespan=lifespan,
)


# ─────────────────────────────────────────────
# Middleware 1 : CORS
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Middleware 2 : Trusted Hosts (anti-Host Header Injection)
# ─────────────────────────────────────────────
if settings.ENV == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["ai-office-hub.com", "*.ai-office-hub.com"],
    )


# ─────────────────────────────────────────────
# Middleware 3 : Audit Trail (SOC 2 CC7.2)
# Logge chaque requête : method, path, IP, durée, status
# ─────────────────────────────────────────────
@app.middleware("http")
async def audit_trail_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.time()
    client_ip = request.client.host if request.client else "unknown"

    logger.info(
        f"[REQ {request_id}] {request.method} {request.url.path} | IP={client_ip}"
    )

    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error(f"[REQ {request_id}] UNHANDLED ERROR: {exc}")
        response = JSONResponse(
            status_code=500,
            content={"detail": "Erreur interne du serveur", "request_id": request_id},
        )

    duration_ms = round((time.time() - start) * 1000, 2)
    logger.info(
        f"[RES {request_id}] status={response.status_code} | duration={duration_ms}ms"
    )

    # Ajouter des headers de sécurité (OWASP)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    return response


# ─────────────────────────────────────────────
# Gestionnaire d'erreurs global
# ─────────────────────────────────────────────
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Ne jamais exposer le vrai message d'erreur en production
    message = str(exc) if settings.ENV != "production" else "Une erreur interne est survenue."
    logger.exception(f"Erreur non gérée sur {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": message, "timestamp": datetime.utcnow().isoformat()},
    )


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────
app.include_router(api_router, prefix=settings.API_PREFIX)


# ─────────────────────────────────────────────
# Health Check (pour Docker HEALTHCHECK & monitoring)
# ─────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    """Endpoint de santé pour le load balancer / Docker Compose."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENV,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/", tags=["System"])
async def root():
    return {"message": f"Bienvenue sur {settings.APP_NAME} API", "docs": "/docs"}
