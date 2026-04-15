import hashlib
import hmac
import datetime
import json
from enum import Enum
from typing import Any, Optional
from sqlalchemy.orm import Session
from app.db.models import AuditLog
from app.core.config import settings

class AuditCategory(str, Enum):
    AUTH = "AUTH"
    DATA_ACCESS = "DATA_ACCESS"
    CONFIG_CHANGE = "CONFIG_CHANGE"
    SECURITY = "SECURITY"
    COMPLIANCE = "COMPLIANCE"
    AI_ACTION = "AI_ACTION"

class AuditSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AuditClassification(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"

class AuditEngine:
    """
    Moteur de capture de preuves numériques (Audit Trail).
    Conforme SOC 2 CC7.2 et ISO 27001.
    """
    def __init__(self):
        self.salt = settings.AUDIT_SECRET_SALT

    def _generate_integrity_hash(self, user_id: str, action: str, timestamp_str: str) -> str:
        """
        Génère un hash HMAC-SHA256 pour garantir l'immuabilité du log.
        """
        payload = f"{user_id}|{action}|{timestamp_str}|{self.salt}"
        return hmac.new(self.salt.encode(), payload.encode(), hashlib.sha256).hexdigest()

    def capture_event(
        self, 
        db: Session,
        user_id: str,
        action_name: str,
        category: AuditCategory = AuditCategory.DATA_ACCESS,
        severity: AuditSeverity = AuditSeverity.INFO,
        classification: AuditClassification = AuditClassification.INTERNAL,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        previous_value: Any = None,
        new_value: Any = None
    ):
        """
        Enregistre un événement d'audit avec calcul d'intégrité et date de rétention.
        """
        now = datetime.datetime.utcnow()
        # Rétention de 7 ans (Légal/Conformité)
        retention_until = now + datetime.timedelta(days=settings.AUDIT_LOG_RETENTION_YEARS * 365)
        
        timestamp_str = now.isoformat()
        integrity_hash = self._generate_integrity_hash(user_id, action_name, timestamp_str)

        # Préparation des valeurs JSON
        prev_json = json.dumps(previous_value) if previous_value is not None else None
        new_json = json.dumps(new_value) if new_value is not None else None

        audit_entry = AuditLog(
            user_id=user_id,
            organization_id=organization_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            session_id=session_id,
            category=category.value,
            severity=severity.value,
            classification=classification.value,
            action_name=action_name,
            previous_value=prev_json,
            new_value=new_json,
            integrity_hash=integrity_hash,
            created_at=now,
            retention_until=retention_until
        )

        db.add(audit_entry)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            # En production, on enverrait une alerte critique ici
            raise e

    def log(self, project_id: int, action: str, status: str):
        """
        Méthode de compatibilité pour l'ancien AuditLogger.
        Utilise une session temporaire ou globale.
        """
        from app.db.database import SessionLocal
        with SessionLocal() as db:
            self.capture_event(
                db=db,
                user_id="SYSTEM",
                action_name=f"{action} [{status}]",
                category=AuditCategory.AI_ACTION,
                organization_id=str(project_id)
            )

# Instance globale
audit_engine = AuditEngine()
# Alias pour compatibilité descendante
AuditLogger = AuditEngine
