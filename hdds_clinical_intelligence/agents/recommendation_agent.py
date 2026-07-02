"""
Recommendation Agent

Generates clinician-review recommendation drafts based on active conditions,
abnormal lab findings, and current medications. All recommendations are
explicitly marked as drafts requiring clinician approval.
"""


class RecommendationAgent:
    """Produces recommendation drafts for clinician review."""

    def __init__(self):
        self.agent_name = "Recommendation Agent"
        self.version = "1.0.0"

    def run(self, patient_data: dict) -> dict:
        """
        Generate recommendation drafts.

        Args:
            patient_data: Full patient profile dictionary.

        Returns:
            Dictionary containing recommendation drafts.
        """
        history = patient_data.get("medical_history", [])
        medications = patient_data.get("medications", [])
        lab_results = patient_data.get("lab_results", [])

        active_conditions = [
            h["condition"] for h in history if h.get("status") == "Active"
        ]
        current_med_names = [m["name"].lower() for m in medications]

        recommendations = []

        # --- Diabetes-specific recommendations ---
        if "Type 2 diabetes mellitus" in active_conditions:
            hba1c_labs = [l for l in lab_results if l["test_name"] == "HbA1c"]
            if hba1c_labs:
                hba1c_val = hba1c_labs[0].get("value", 0)
                if isinstance(hba1c_val, (int, float)) and hba1c_val > 7.0:
                    recommendations.append({
                        "category": "Medication Review",
                        "priority": "High",
                        "recommendation": (
                            f"HbA1c is {hba1c_val}% (target < 7.0%). "
                            "Consider intensifying glycemic control — review current "
                            "Metformin dosage and assess need for additional anti-diabetic agent "
                            "(e.g., SGLT2 inhibitor or GLP-1 receptor agonist)."
                        ),
                        "status": "Draft — Requires Clinician Review",
                    })

            # Check for renal implications with diabetes
            egfr_labs = [l for l in lab_results if l["test_name"] == "eGFR"]
            if egfr_labs:
                egfr_val = egfr_labs[0].get("value", 100)
                if isinstance(egfr_val, (int, float)) and egfr_val < 60:
                    recommendations.append({
                        "category": "Nephrology Referral",
                        "priority": "High",
                        "recommendation": (
                            f"eGFR is {egfr_val} mL/min/1.73m² (below 60). "
                            "In context of diabetes, this suggests possible diabetic nephropathy. "
                            "Consider nephrology referral and assess for SGLT2 inhibitor "
                            "with renal protective benefits."
                        ),
                        "status": "Draft — Requires Clinician Review",
                    })

        # --- Hypertension-specific recommendations ---
        if "Hypertension" in active_conditions:
            bp_labs = [l for l in lab_results if l["test_name"] == "Blood Pressure"]
            if bp_labs:
                bp_status = bp_labs[0].get("status", "").lower()
                if bp_status in ("elevated", "high", "borderline high"):
                    recommendations.append({
                        "category": "Blood Pressure Management",
                        "priority": "Medium",
                        "recommendation": (
                            f"Blood Pressure is {bp_labs[0]['value']} mmHg ({bp_labs[0]['status']}). "
                            "Current antihypertensive may need dose adjustment. "
                            "Reinforce lifestyle modifications: sodium restriction, "
                            "regular exercise, and weight management."
                        ),
                        "status": "Draft — Requires Clinician Review",
                    })

        # --- Creatinine-specific recommendation ---
        creat_labs = [l for l in lab_results if l["test_name"] == "Creatinine"]
        if creat_labs:
            creat_status = creat_labs[0].get("status", "").lower()
            if creat_status not in ("normal", "within range", ""):
                recommendations.append({
                    "category": "Renal Function Monitoring",
                    "priority": "Medium",
                    "recommendation": (
                        f"Creatinine is {creat_labs[0]['value']} {creat_labs[0].get('unit', '')} "
                        f"({creat_labs[0]['status']}). "
                        "Recommend repeat renal panel in 1-3 months to monitor trend. "
                        "Review medication doses for renal adjustment if needed."
                    ),
                    "status": "Draft — Requires Clinician Review",
                })

        # --- Lifestyle recommendations (always included for chronic conditions) ---
        if active_conditions:
            recommendations.append({
                "category": "Lifestyle & Patient Education",
                "priority": "Standard",
                "recommendation": (
                    "Reinforce patient education on disease self-management, "
                    "medication adherence, dietary counseling, and regular physical activity. "
                    "Consider referral to diabetes educator if available."
                ),
                "status": "Draft — Requires Clinician Review",
            })

        return {
            "agent": self.agent_name,
            "version": self.version,
            "total_recommendations": len(recommendations),
            "recommendations": recommendations,
            "disclaimer": "All recommendations are drafts for clinician review only.",
        }
