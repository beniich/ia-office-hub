"""
ai_agent.py — Endpoints de l'agent IA (LangChain / OpenOffice)
==============================================================
POST /analyze  → Lance un diagnostic IA sur un projet
POST /generate → Génère un PPT d'orientation via OpenOffice
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from app.core.security import require_manager, TokenData
from app.services.ai_service import AIAgent
from app.services.audit_service import AuditLogger

router = APIRouter()
audit = AuditLogger()
ai_agent = AIAgent()

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