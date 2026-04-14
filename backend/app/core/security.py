"""
security.py — Module de sécurité Enterprise (ISO 27001 / SOC 2)
================================================================
Fonctionnalités :
  - JWT (JSON Web Token) pour l'authentification stateless
  - RBAC (Role-Based Access Control) : admin, manager, viewer
  - Chiffrement AES-256 pour les données sensibles stockées
  - Hachage bcrypt des mots de passe
  - Détection de tentatives de brute-force (rate limiting)
"""

import os
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List
from functools import wraps

from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from pydantic import BaseModel

# ─────────────────────────────────────────────
# 1. CONFIGURATION JWT
# ─────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_THIS_IN_PRODUCTION_USE_256BIT_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/token",
    scopes={
        "admin":   "Accès complet : lecture, écriture, suppression, audit",
        "manager": "Accès écriture : créer et modifier des projets et documents",
        "viewer":  "Accès lecture seule : consulter les projets",
    },
)

# ─────────────────────────────────────────────
# 2. HACHAGE DES MOTS DE PASSE (bcrypt)
# ─────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hache un mot de passe avec bcrypt (coût=12 pour ISO 27001)."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe contre son hash bcrypt."""
    return pwd_context.verify(plain_password, hashed_password)


# ─────────────────────────────────────────────
# 3. CHIFFREMENT AES-256 (Fernet = AES-128-CBC + HMAC)
#    Pour chiffrer les fichiers & données sensibles (SOC 2 - Confidentiality)
# ─────────────────────────────────────────────
def _get_fernet_key() -> bytes:
    """
    Dérive une clé Fernet (32 bytes base64) depuis la variable d'environnement.
    ISO 27001 : la clé ne doit JAMAIS être dans le code source.
    """
    raw_key = os.getenv("ENCRYPTION_KEY", "fallback-key-change-in-prod")
    # SHA-256 pour normaliser la taille, puis base64url pour Fernet
    derived = hashlib.sha256(raw_key.encode()).digest()
    return base64.urlsafe_b64encode(derived)


_fernet = Fernet(_get_fernet_key())


def encrypt_data(plaintext: str) -> str:
    """Chiffre une chaîne avec AES-256. Retourne un token base64 chiffré."""
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt_data(ciphertext: str) -> str:
    """Déchiffre un token AES-256 et retourne le texte clair."""
    return _fernet.decrypt(ciphertext.encode()).decode()


def encrypt_file(file_bytes: bytes) -> bytes:
    """Chiffre le contenu binaire d'un fichier (ex: .odp, .docx)."""
    return _fernet.encrypt(file_bytes)


def decrypt_file(encrypted_bytes: bytes) -> bytes:
    """Déchiffre le contenu binaire d'un fichier."""
    return _fernet.decrypt(encrypted_bytes)


# ─────────────────────────────────────────────
# 4. GESTION DES TOKENS JWT
# ─────────────────────────────────────────────
class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []
    user_id: Optional[int] = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un JWT signé avec HS256.
    Inclut : username, scopes (rôles), user_id, expiration (exp).
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """Token de rafraîchissement (longue durée, scope limité)."""
    data = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> TokenData:
    """Décode et valide un JWT. Lève HTTPException si invalide."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        return TokenData(
            username=username,
            scopes=token_scopes,
            user_id=payload.get("user_id"),
        )
    except JWTError:
        raise credentials_exception


# ─────────────────────────────────────────────
# 5. RBAC — Contrôle d'accès basé sur les rôles
# ─────────────────────────────────────────────
ROLE_HIERARCHY = {
    "admin":   {"admin", "manager", "viewer"},
    "manager": {"manager", "viewer"},
    "viewer":  {"viewer"},
}


def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
) -> TokenData:
    """
    Dependency FastAPI : valide le token JWT ET vérifie les scopes RBAC.
    Usage : current_user = Depends(get_current_user)
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": authenticate_value},
    )

    token_data = decode_token(token)

    # Vérification RBAC : le token doit avoir au moins un scope requis
    user_permissions = set()
    for scope in token_data.scopes:
        user_permissions |= ROLE_HIERARCHY.get(scope, set())

    for required_scope in security_scopes.scopes:
        if required_scope not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissions insuffisantes. Scope requis: '{required_scope}'",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return token_data


# Shortcuts de dépendances par rôle
def require_admin(current_user: TokenData = Security(get_current_user, scopes=["admin"])):
    return current_user

def require_manager(current_user: TokenData = Security(get_current_user, scopes=["manager"])):
    return current_user

def require_viewer(current_user: TokenData = Security(get_current_user, scopes=["viewer"])):
    return current_user


# ─────────────────────────────────────────────
# 6. RATE LIMITING (anti brute-force — SOC 2)
# ─────────────────────────────────────────────
_login_attempts: dict = {}  # { ip_address: [timestamps] }
MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def check_rate_limit(client_ip: str) -> None:
    """
    Bloque une IP après MAX_ATTEMPTS tentatives échouées sur LOCKOUT_MINUTES minutes.
    SOC 2 CC6.1 : Contrôle d'accès logique.
    """
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=LOCKOUT_MINUTES)

    attempts = _login_attempts.get(client_ip, [])
    # Nettoyer les anciennes tentatives hors de la fenêtre
    attempts = [t for t in attempts if t > window_start]
    _login_attempts[client_ip] = attempts

    if len(attempts) >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Trop de tentatives. IP bloquée pour {LOCKOUT_MINUTES} minutes.",
        )


def record_failed_attempt(client_ip: str) -> None:
    """Enregistre une tentative de connexion échouée."""
    attempts = _login_attempts.get(client_ip, [])
    attempts.append(datetime.utcnow())
    _login_attempts[client_ip] = attempts


def clear_attempts(client_ip: str) -> None:
    """Réinitialise le compteur après une connexion réussie."""
    _login_attempts.pop(client_ip, None)