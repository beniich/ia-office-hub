"""
test_security.py — Tests de sécurité automatisés (SOC 2 / ISO 27001)
===================================================================
Ces tests vérifient que les mécanismes de chiffrement et d'authentification
fonctionnent correctement. Ils doivent passer avant chaque déploiement.
"""

import pytest
from datetime import timedelta
from fastapi import HTTPException
from app.core.security import (
    hash_password, verify_password, 
    encrypt_data, decrypt_data,
    create_access_token, decode_token,
    check_rate_limit, record_failed_attempt, clear_attempts
)

def test_password_hashing():
    """Vérifie que bcrypt génère des hashes différents et sécurisés."""
    pwd = "SuperSecretPassword123!"
    hashed = hash_password(pwd)
    
    assert pwd != hashed
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_aes_encryption():
    """Vérifie le chiffrement AES-256 Fernet."""
    secret_text = "Confidential Data PII: John Doe"
    encrypted = encrypt_data(secret_text)
    
    assert secret_text != encrypted
    
    decrypted = decrypt_data(encrypted)
    assert decrypted == secret_text

def test_jwt_generation_and_validation():
    """Vérifie la génération et la signature des JWT."""
    data = {"sub": "admin@ai-hub.com", "scopes": ["admin"], "user_id": 1}
    token = create_access_token(data, timedelta(minutes=5))
    
    assert len(token) > 50
    decoded = decode_token(token)
    
    assert decoded.username == "admin@ai-hub.com"
    assert "admin" in decoded.scopes
    assert decoded.user_id == 1

def test_rate_limiting_blocks_brute_force():
    """Vérifie que le mécanisme anti-brute force bloque après N essais."""
    ip = "192.168.1.100"
    clear_attempts(ip)
    
    # 5 tentatives échouées
    for _ in range(5):
        record_failed_attempt(ip)
        
    with pytest.raises(HTTPException) as exc_info:
        check_rate_limit(ip)
        
    assert exc_info.value.status_code == 429
    assert "Trop de tentatives" in exc_info.value.detail