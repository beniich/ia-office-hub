import json
from .uno_bridge import OpenOfficeBridge
from .audit_service import AuditLogger

class AIAgent:
    def __init__(self):
        self.bridge = OpenOfficeBridge()
        self.logger = AuditLogger()

    def generate_financial_diagnostic(self, project_id, doc_id):
        """
        Flux complet : Lecture -> Analyse -> Diagnostic -> Plan PPT
        """
        try:
            # 1. COORDINATION : Récupération du fichier depuis la BDD
            # Simulation : on récupère le chemin du document via doc_id
            file_path = "budget_2024.ods" 
            
            # 2. EXTRACTION : Lecture des données via le pont OpenOffice
            raw_data = self.bridge.read_calc_range(file_path)
            
            # 3. CALCUL & DIAGNOSTIC : L'IA analyse les données
            # On simule ici l'appel au LLM (GPT-4/Llama 3) avec un prompt expert
            analysis_result = self._analyze_financials(raw_data)
            
            # 4. ORIENTATION PPT : Transformation du diagnostic en structure de slides
            ppt_structure = self._create_ppt_storyboard(analysis_result)
            
            # 5. PERSISTENCE & AUDIT (Conformité SOC 2) : On enregistre tout
            self._save_to_db(project_id, doc_id, analysis_result, ppt_structure)
            self.logger.log(project_id, "FINANCIAL_DIAGNOSTIC_GENERATE", "SUCCESS")
            
            # 6. EXÉCUTION : L'IA commande à OpenOffice de créer la présentation
            final_ppt_path = self.bridge.generate_document(
                "impress", 
                json.dumps(ppt_structure), 
                f"diag_financier_{project_id}.odp"
            )
            
            return {
                "status": "Success",
                "diagnostic": analysis_result,
                "ppt_plan": ppt_structure,
                "file_url": final_ppt_path
            }

        except Exception as e:
            self.logger.log(project_id, "FINANCIAL_DIAGNOSTIC_GENERATE", "FAILED")
            return {"status": "Error", "message": str(e)}

    def _analyze_financials(self, data):
        """
        C'est ici que le prompt LLM intervient.
        L'IA calcule les variances et pose un diagnostic.
        """
        # Simulation du raisonnement de l'IA
        diagnostic = "Le budget global présente un dépassement de 3%. "
        findings = []
        for item in data:
            diff = item['reel'] - item['prevu']
            findings.append(f"{item['poste']}: écart de {diff}€")
            
        return {
            "summary": diagnostic,
            "details": findings,
            "critical_alert": "Le poste Marketing est en surconsommation critique (+25%)."
        }

    def _create_ppt_storyboard(self, analysis):
        """
        Transforme un diagnostic en orientation de slides (Storyboarding).
        """
        return [
            {"slide": 1, "title": "Analyse Budgétaire Q3", "content": "Présentation des écarts et diagnostics"},
            {"slide": 2, "title": "État des Lieux", "content": analysis['summary']},
            {"slide": 3, "title": "Points Critiques", "content": analysis['critical_alert']},
            {"slide": 4, "title": "Recommandations", "content": "Réduire le budget Marketing du mois prochain pour compenser."}
        ]

    def _save_to_db(self, project_id, doc_id, analysis, plan):
        # Ici, on insère dans les tables ai_diagnostics et presentation_plans
        print(f"Saving diagnostic for project {project_id} to SQL...")

    def process_request(self, project_id, user_prompt):
        """Méthode de compatibilité avec l'ancien code."""
        return self.generate_financial_diagnostic(project_id, 999)
