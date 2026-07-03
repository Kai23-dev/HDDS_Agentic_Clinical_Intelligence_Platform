"""
Medication Prescription Agent

Suggests first-line medications based on the patient's active diagnoses.
Crucially enforces that all prescriptions require clinician approval.
"""

class MedicationPrescriptionAgent:
    """Produces medication prescription suggestions for clinician approval."""

    def __init__(self):
        self.agent_name = "Medication Prescription Agent"
        self.version = "1.0.0"

    def run(self, patient_data: dict) -> dict:
        """
        Generate medication suggestions based on active conditions.

        Args:
            patient_data: Full patient profile dictionary.

        Returns:
            Dictionary containing prescription suggestions and a strict doctor approval warning.
        """
        history = patient_data.get("medical_history", [])
        active_conditions = [h["condition"] for h in history if h.get("status") == "Active"]

        prescriptions = []

        for condition in active_conditions:
            cond_lower = condition.lower()
            if "diabetes" in cond_lower:
                prescriptions.append({
                    "diagnosis": condition,
                    "suggested_medication": "Metformin",
                    "dosage_guideline": "500 mg orally twice a day with meals (Starting dose)",
                    "rationale": "First-line pharmacotherapy for Type 2 Diabetes Mellitus."
                })
            elif "hypertension" in cond_lower:
                prescriptions.append({
                    "diagnosis": condition,
                    "suggested_medication": "Lisinopril (ACE Inhibitor) or Amlodipine (Calcium Channel Blocker)",
                    "dosage_guideline": "Lisinopril 10 mg orally once daily OR Amlodipine 5 mg orally once daily",
                    "rationale": "Standard first-line antihypertensive therapy."
                })
            elif "myocardial infarction" in cond_lower or "heart failure" in cond_lower:
                prescriptions.append({
                    "diagnosis": condition,
                    "suggested_medication": "Aspirin & Beta-Blocker (e.g., Metoprolol)",
                    "dosage_guideline": "Aspirin 81 mg daily; Metoprolol 25 mg daily",
                    "rationale": "Secondary prevention and mortality reduction post-MI or for heart failure."
                })
            elif "asthma" in cond_lower:
                prescriptions.append({
                    "diagnosis": condition,
                    "suggested_medication": "Albuterol inhaler (SABA) & Inhaled Corticosteroid (ICS)",
                    "dosage_guideline": "Albuterol 2 puffs q4-6h PRN; Fluticasone 1-2 puffs BID",
                    "rationale": "Standard rescue and controller therapy for asthma."
                })
            else:
                prescriptions.append({
                    "diagnosis": condition,
                    "suggested_medication": "Condition-specific standard of care",
                    "dosage_guideline": "Determine based on patient factors",
                    "rationale": "Refer to clinical guidelines for appropriate pharmacotherapy."
                })

        return {
            "agent": self.agent_name,
            "version": self.version,
            "total_suggestions": len(prescriptions),
            "prescriptions": prescriptions,
            "doctor_approval_required": True,
            "warning": "CRITICAL: The medications listed above are AI-generated suggestions based on clinical guidelines. They MUST be verified, approved, and formally prescribed by a licensed clinician before the patient takes them."
        }
