"""
Clinical Summary Agent

Summarizes patient history, current medications, and abnormal lab results
into a concise clinical overview for clinician review.
"""


class ClinicalSummaryAgent:
    """Generates a clinical summary from patient profile data."""

    def __init__(self):
        self.agent_name = "Clinical Summary Agent"
        self.version = "1.0.0"

    def run(self, patient_data: dict) -> dict:
        """
        Analyze patient data and produce a clinical summary.

        Args:
            patient_data: Full patient profile dictionary.

        Returns:
            Dictionary containing the clinical summary output.
        """
        profile = patient_data.get("patient_profile", {})
        history = patient_data.get("medical_history", [])
        medications = patient_data.get("medications", [])
        lab_results = patient_data.get("lab_results", [])
        encounters = patient_data.get("encounters", [])
        
        med_list = [med.get("DESCRIPTION", "Unknown Medication") for med in medications]
        
        # Calculate Medication Complexity
        med_count = len(med_list)
        if med_count >= 5:
            med_complexity = "High - Polypharmacy Risk"
        elif med_count >= 3:
            med_complexity = "Moderate"
        else:
            med_complexity = "Low"

        # --- Build active conditions list ---
        active_conditions = [
            h["condition"] for h in history if h.get("status") == "Active"
        ]

        # --- Build medication summary ---
        med_summary = []
        for med in medications:
            med_summary.append(
                f"{med['name']} {med['dosage']} {med['frequency']}"
            )

        # --- Flag abnormal labs ---
        abnormal_labs = []
        for lab in lab_results:
            status = lab.get("status", "").lower()
            if status not in ("normal", "within range", ""):
                abnormal_labs.append({
                    "test": lab["test_name"],
                    "value": lab["value"],
                    "unit": lab.get("unit", ""),
                    "status": lab["status"],
                    "reference_range": lab.get("reference_range", "N/A"),
                })

        # --- Latest encounter note ---
        latest_encounter = None
        if encounters:
            sorted_enc = sorted(encounters, key=lambda e: e.get("date", ""), reverse=True)
            latest_encounter = {
                "date": sorted_enc[0].get("date"),
                "reason": sorted_enc[0].get("reason"),
                "provider": sorted_enc[0].get("provider"),
                "notes": sorted_enc[0].get("notes"),
            }

        # --- Compose summary ---
        summary_text = (
            f"{profile.get('name', 'Unknown')}, {profile.get('age', 'N/A')} y/o "
            f"{profile.get('gender', 'N/A')}, presents with "
            f"{', '.join(active_conditions) if active_conditions else 'no active conditions'}. "
            f"Currently on {', '.join(med_summary) if med_summary else 'no medications'}. "
            f"{len(abnormal_labs)} abnormal lab result(s) identified."
        )

        return {
            "agent": self.agent_name,
            "version": self.version,
            "summary_text": summary_text,
            "active_conditions": active_conditions,
            "current_medications": med_list,
            "medication_count": med_count,
            "medication_complexity": med_complexity,
            "abnormal_labs": abnormal_labs,
            "latest_encounter": latest_encounter,
        }
