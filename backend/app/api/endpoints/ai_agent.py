"""
ai_agent.py — Endpoints de l'agent IA (LangChain / OpenOffice)
==============================================================
POST /analyze  → Lance un diagnostic IA sur un projet
POST /generate → Génère un PPT d'orientation via OpenOffice
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.core.security import require_manager, TokenData
from app.db.database import get_db
from app.services.ai_service import AIAgent
from app.services.audit_service import audit_engine, AuditCategory, AuditSeverity, AuditClassification
from app.services.audit_report_service import AuditReportService

router = APIRouter()
audit = audit_engine # Utilisation du nouveau moteur
ai_agent = AIAgent()
compliance_service = AuditReportService()

# ── Schémas (Pydantic) ────────────────────────────────────────

class AIRequest(BaseModel):
    project_id: int
    prompt: Optional[str] = "Générer un diagnostic complet et un plan d'action"

class AIResponse(BaseModel):
    status: str
    message: str
    diagnostic: Optional[str] = None
    file_url: Optional[str] = None

# ── Endpoints ─────────────────────────────────────────────────

@router.post("/analyze", response_model=AIResponse)
async def analyze_project(
    request: AIRequest,
    current_user: TokenData = Depends(require_manager)
):
    """
    [Manager/Admin] Lance une analyse IA sur les données d'un projet.
    Audit loggué pour SOC 2 CC7.
    """
    audit.log(request.project_id, f"AI_ANALYZE_REQUEST_BY: {current_user.username}", "SUCCESS")
    
    try:
        # Appel simulé au service IA
        result = ai_agent.process_request(request.project_id, request.prompt)
        
        return AIResponse(
            status="success",
            message="Analyse IA terminée avec succès.",
            diagnostic=result.get("diagnostic"),
            file_url=result.get("file")
        )
    except Exception as e:
        audit.log(request.project_id, f"AI_ANALYZE_ERROR: {str(e)}", "FAILURE")
        raise HTTPException(status_code=500, detail="L'agent IA a rencontré une erreur")


@router.post("/generate", response_model=AIResponse, status_code=202)
async def generate_presentation(
    request: AIRequest,
    background_tasks: BackgroundTasks,
    current_user: TokenData = Depends(require_manager)
):
    """
    [Manager/Admin] Génère un PPT de présentation en tâche de fond (async).
    Utilise le pont OpenOffice (PyUNO).
    """
    audit.log(request.project_id, f"AI_GENERATE_PPT_REQUEST_BY: {current_user.username}", "SUCCESS")
    
    def background_generation(project_id: int, prompt: str):
        try:
            ai_agent.process_request(project_id, prompt)
            audit.log(project_id, "AI_GENERATE_PPT_SUCCESS", "SUCCESS")
        except Exception as e:
            audit.log(project_id, f"AI_GENERATE_PPT_FAILED: {str(e)}", "FAILURE")

    # Lance la génération en tâche de fond pour ne pas bloquer le client
    background_tasks.add_task(background_generation, request.project_id, request.prompt)
    
    return AIResponse(
        status="processing",
        message="La génération du document a commencé en arrière-plan."
    )

@router.post("/diagnose-financials/{project_id}/{doc_id}")
async def run_diagnostic(project_id: int, doc_id: int):
    """
    Déclenche l'analyse financière et la génération du PPT.
    """
    result = ai_agent.generate_financial_diagnostic(project_id, doc_id)
    return result

@router.get("/compliance-pack/{project_id}")
async def download_compliance_pack(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_manager)
):
    """
    [Manager/Admin] Génère et télécharge le dossier de preuve numérique (ODT).
    L'action est elle-même logguée dans le système d'audit.
    """
    try:
        # 1. Génération du rapport
        file_path = compliance_service.generate_compliance_pack(db, project_id)
        
        # 2. Audit de l'action de téléchargement
        audit.capture_event(
            db=db,
            user_id=current_user.username,
            action_name="AUDIT_REPORT_DOWNLOADED",
            category=AuditCategory.COMPLIANCE,
            severity=AuditSeverity.INFO,
            classification=AuditClassification.CONFIDENTIAL,
            organization_id=str(project_id),
            ip_address=request.client.host,
            new_value={"report_path": file_path}
        )
        
        # 3. Retour du fichier
        return FileResponse(
            path=file_path,
            filename=f"Compliance_Pack_P{project_id}.odt",
            media_type="application/vnd.oasis.opendocument.text"
        )
        
    except Exception as e:
        audit.capture_event(
            db=db,
            user_id=current_user.username,
            action_name="AUDIT_REPORT_DOWNLOAD_FAILED",
            category=AuditCategory.SECURITY,
            severity=AuditSeverity.ERROR,
            organization_id=str(project_id),
            new_value={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Échec de la génération du rapport de conformité")