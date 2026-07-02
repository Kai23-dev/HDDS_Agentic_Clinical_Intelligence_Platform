"""
Risk Assessment Agent

Classifies overall patient risk as Low / Medium / High based on
the number of active conditions, medications, and abnormal lab results.
"""


class RiskAssessmentAgent:
    """Rule-based risk stratification agent."""

    def __init__(self):
        self.agent_name = "Risk Assessment Agent"
        self.version = "1.0.0"

    def run(self, patient_data: dict) -> dict:
        """
        Evaluate patient risk level.

        Args:
            patient_data: Full patient profile dictionary.

        Returns:
            Dictionary with risk level, score breakdown, and rationale.
        """
        history = patient_data.get("medical_history", [])
        medications = patient_data.get("medications", [])
        lab_results = patient_data.get("lab_results", [])

        # --- Count risk factors ---
        active_conditions = [
            h for h in history if h.get("status") == "Active"
        ]
        num_conditions = len(active_conditions)

        num_medications = len(medications)

        abnormal_labs = [
            lab for lab in lab_results
            if lab.get("status", "").lower() not in ("normal", "within range", "")
        ]
        num_abnormal = len(abnormal_labs)

        # --- Calculate risk score ---
        # Each factor contributes points:
        #   conditions: 2 pts each
        #   medications: 1 pt each
        #   abnormal labs: 2 pts each
        risk_score = (num_conditions * 2) + (num_medications * 1) + (num_abnormal * 2)

        # --- Classify ---
        if risk_score <= 4:
            risk_level = "Low"
        elif risk_score <= 8:
            risk_level = "Medium"
        else:
            risk_level = "High"

        # --- Build rationale ---
        rationale_parts = []
        if num_conditions > 0:
            conditions_list = [c["condition"] for c in active_conditions]
            rationale_parts.append(
                f"{num_conditions} active condition(s): {', '.join(conditions_list)}"
            )
        if num_medications > 0:
            rationale_parts.append(f"{num_medications} active medication(s)")
        if num_abnormal > 0:
            lab_names = [lab["test_name"] for lab in abnormal_labs]
            rationale_parts.append(
                f"{num_abnormal} abnormal lab(s): {', '.join(lab_names)}"
            )

        return {
            "agent": self.agent_name,
            "version": self.version,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "score_breakdown": {
                "conditions_count": num_conditions,
                "conditions_points": num_conditions * 2,
                "medications_count": num_medications,
                "medications_points": num_medications * 1,
                "abnormal_labs_count": num_abnormal,
                "abnormal_labs_points": num_abnormal * 2,
            },
            "rationale": "; ".join(rationale_parts) if rationale_parts else "No significant risk factors identified.",
        }
