from agents.clinical_summary_agent import ClinicalSummaryAgent
from agents.risk_assessment_agent import RiskAssessmentAgent
from agents.early_detection_agent import EarlyDetectionAgent
from agents.recommendation_agent import RecommendationAgent
from agents.evidence_validation_agent import EvidenceValidationAgent
from agents.followup_action_agent import FollowupActionAgent
from agents.medication_prescription_agent import MedicationPrescriptionAgent
from gtx_rag_system import GTXRagSystem

class OrchestratorAgent:
    """
    Central hub that coordinates the GTX RAG system for unstructured data
    and delegates to the 6 specialized sub-agents.
    """
    def __init__(self):
        self.gtx_rag = GTXRagSystem()
        self.clinical_summary_agent = ClinicalSummaryAgent()
        self.risk_assessment_agent = RiskAssessmentAgent()
        self.early_detection_agent = EarlyDetectionAgent()
        self.recommendation_agent = RecommendationAgent()
        self.evidence_validation_agent = EvidenceValidationAgent()
        self.followup_action_agent = FollowupActionAgent()
        self.medication_prescription_agent = MedicationPrescriptionAgent()

    def process_patient(self, patient_data: dict) -> dict:
        """
        Runs the full orchestration flow for a single patient.
        """
        patient_id = patient_data.get("patient_id")
        
        # 1. RAG Extraction: Get unstructured insights from Asclepius notes via GTX
        unstructured_insights = self.gtx_rag.extract_information(patient_id)
        
        # 2. Merge unstructured insights into patient_data context for sub-agents
        # Sub-agents can read this new context if they are programmed to do so,
        # but for prototype purposes, we inject it into the root data.
        patient_data["gtx_unstructured_insights"] = unstructured_insights
        
        # 3. Delegate to sub-agents sequentially (or in parallel in a real system)
        outputs = {}
        outputs["clinical_summary"] = self.clinical_summary_agent.run(patient_data)
        
        # Append the unstructured critical findings to the summary for visibility
        if isinstance(unstructured_insights, dict) and "critical_findings" in unstructured_insights:
            outputs["clinical_summary"]["summary_text"] += (
                f"\n\n[GTX RAG Extraction]: {unstructured_insights['critical_findings']}"
            )

        outputs["risk_assessment"] = self.risk_assessment_agent.run(patient_data)
        outputs["early_detection"] = self.early_detection_agent.run(patient_data)
        outputs["recommendations"] = self.recommendation_agent.run(patient_data)
        outputs["medication_prescription"] = self.medication_prescription_agent.run(patient_data)
        outputs["evidence_validation"] = self.evidence_validation_agent.run(patient_data, outputs)
        outputs["followup_actions"] = self.followup_action_agent.run(patient_data, outputs)

        # Add orchestrator metadata so the user knows it's the Orchestrator Agent
        outputs["orchestrator_metadata"] = {
            "agent_name": "Orchestrator Agent",
            "version": "1.0.0",
            "description": "Central coordinator that delegates to sub-agents."
        }

        return outputs
