"""
auth.py — Endpoints d'authentification (JWT + RBAC)
====================================================
POST /api/v1/auth/token      → Login → retourne access_token + refresh_token
POST /api/v1/auth/refresh    → Renouvelle l'access token
POST /api/v1/auth/logout     → Invalide la session (audit log)
GET  /api/v1/auth/me         → Profil de l'utilisateur connecté
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import (
    verify_password, create_access_token, create_refresh_token,
    decode_token, get_current_user, TokenData,
    check_rate_limit, record_failed_attempt, clear_attempts,
)
from app.services.audit_service import AuditLogger

router = APIRouter()
audit = AuditLogger()

# ── Schémas de réponse ─────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


class RefreshRequest(BaseModel):
    refresh_token: str


# ── Base de données utilisateurs (à remplacer par la BDD en prod) ──
FAKE_USERS_DB = {
    "admin@ai-hub.com": {
        "user_id": 1,
        "username": "admin@ai-hub.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # 'secret'
        "scopes": ["admin"],
        "is_active": True,
    },
    "manager@ai-hub.com": {
        "user_id": 2,
        "username": "manager@ai-hub.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "scopes": ["manager"],
        "is_active": True,
    },
}


# ── POST /token ───────────────────────────────────────────────
@router.post("/token", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Login OAuth2 standard. Retourne un JWT access_token et un refresh_token.
    Protégé par rate limiting (SOC 2 CC6.1).
    """
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)

    user = FAKE_USERS_DB.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        record_failed_attempt(client_ip)
        audit.log(None, f"FAILED_LOGIN: {form_data.username} from {client_ip}", "FAILURE")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
        )

    if not user["is_active"]:
        raise HTTPException(status_code=400, detail="Compte désactivé")

    clear_attempts(client_ip)
    audit.log(user["user_id"], f"LOGIN_SUCCESS: {form_data.username}", "SUCCESS")

    access_token = create_access_token(
        data={
            "sub": user["username"],
            "scopes": user["scopes"],
            "user_id": user["user_id"],
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(user["user_id"])

    return Token(access_token=access_token, refresh_token=refresh_token)


# ── POST /refresh ─────────────────────────────────────────────
@router.post("/refresh", response_model=Token)
async def refresh_token(body: RefreshRequest):
    """Renouvelle l'access token à partir du refresh token."""
    token_data = decode_token(body.refresh_token)

    # Chercher l'utilisateur par user_id
    user = next(
        (u for u in FAKE_USERS_DB.values() if u["user_id"] == token_data.user_id),
        None,
    )
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    new_access_token = create_access_token(
        data={"sub": user["username"], "scopes": user["scopes"], "user_id": user["user_id"]}
    )
    new_refresh_token = create_refresh_token(user["user_id"])

    return Token(access_token=new_access_token, refresh_token=new_refresh_token)


# ── GET /me ───────────────────────────────────────────────────
@router.get("/me")
async def get_me(current_user: TokenData = Depends(get_current_user)):
    """Retourne le profil de l'utilisateur actuellement connecté."""
    user = FAKE_USERS_DB.get(current_user.username, {})
    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "roles": current_user.scopes,
        "is_active": user.get("is_active", False),
    }
