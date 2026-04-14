"""
test_ai.py — Tests unitaires pour l'agent IA et de génération documentaire
==========================================================================
"""

from app.services.ai_service import AIAgent

def test_ai_agent_initialization():
    """Vérifie que l'agent IA s'initialise correctement (sans appel réseau réel)."""
    # En pratique, on utiliserait unittest.mock pour mocker OpenOfficeBridge et AuditLogger
    agent = AIAgent()
    assert agent is not None

def test_ai_agent_process_request():
    """Test rapide du flux (simulé) d'analyse IA."""
    agent = AIAgent()
    
    # Utilisation d'un project_id factice
    response = agent.process_request(project_id=999, user_prompt="Test")
    
    assert "diagnostic" in response
    assert "file" in response
    assert response["file"].endswith(".odp")