"""
Early Detection Agent

Flags abnormal lab results and identifies chronic disease monitoring
needs that may require early clinical intervention.
"""


# Mapping of conditions to recommended monitoring tests
CHRONIC_MONITORING_MAP = {
    "Type 2 diabetes mellitus": [
        {"test": "HbA1c", "frequency": "Every 3 months if uncontrolled, every 6 months if stable"},
        {"test": "Fasting Glucose", "frequency": "At each visit"},
        {"test": "eGFR", "frequency": "Annually (more frequently if abnormal)"},
        {"test": "Urine Albumin", "frequency": "Annually"},
        {"test": "Diabetic Eye Exam", "frequency": "Annually"},
        {"test": "Foot Exam", "frequency": "At each visit"},
    ],
    "Hypertension": [
        {"test": "Blood Pressure", "frequency": "At each visit"},
        {"test": "Creatinine", "frequency": "Annually"},
        {"test": "Electrolytes", "frequency": "Annually or as needed"},
        {"test": "Lipid Panel", "frequency": "Every 6-12 months"},
    ],
}


class EarlyDetectionAgent:
    """Identifies abnormal findings and chronic monitoring gaps."""

    def __init__(self):
        self.agent_name = "Early Detection Agent"
        self.version = "1.0.0"

    def run(self, patient_data: dict) -> dict:
        """
        Scan for abnormal labs and chronic disease monitoring needs.

        Args:
            patient_data: Full patient profile dictionary.

        Returns:
            Dictionary with flagged abnormals and monitoring recommendations.
        """
        history = patient_data.get("medical_history", [])
        lab_results = patient_data.get("lab_results", [])

        # --- Flag abnormal labs with clinical context ---
        flagged_results = []
        for lab in lab_results:
            status = lab.get("status", "").lower()
            if status not in ("normal", "within range", ""):
                severity = self._assess_severity(lab)
                flagged_results.append({
                    "test_name": lab["test_name"],
                    "value": lab["value"],
                    "unit": lab.get("unit", ""),
                    "reference_range": lab.get("reference_range", "N/A"),
                    "status": lab["status"],
                    "severity": severity,
                    "date": lab.get("date", "Unknown"),
                })

        # --- Identify chronic disease monitoring needs ---
        monitoring_needs = []
        active_conditions = [
            h["condition"] for h in history if h.get("status") == "Active"
        ]

        available_tests = {lab["test_name"] for lab in lab_results}

        for condition in active_conditions:
            if condition in CHRONIC_MONITORING_MAP:
                for monitor in CHRONIC_MONITORING_MAP[condition]:
                    monitoring_needs.append({
                        "condition": condition,
                        "recommended_test": monitor["test"],
                        "frequency": monitor["frequency"],
                        "recently_completed": monitor["test"] in available_tests,
                    })

        # --- Compile alerts ---
        alerts = []
        for flag in flagged_results:
            if flag["severity"] in ("Critical", "High"):
                alerts.append(
                    f"ALERT: {flag['test_name']} = {flag['value']} {flag['unit']} "
                    f"({flag['status']}) — requires clinical attention."
                )

        return {
            "agent": self.agent_name,
            "version": self.version,
            "flagged_abnormal_results": flagged_results,
            "chronic_monitoring_needs": monitoring_needs,
            "alerts": alerts,
            "total_flags": len(flagged_results),
        }

    def _assess_severity(self, lab: dict) -> str:
        """Simple rule-based severity classification."""
        status = lab.get("status", "").lower()
        test = lab.get("test_name", "").lower()

        # HbA1c severity thresholds
        if test == "hba1c":
            val = lab.get("value", 0)
            if isinstance(val, (int, float)):
                if val >= 10.0:
                    return "Critical"
                elif val >= 8.0:
                    return "High"
                elif val >= 6.5:
                    return "Moderate"

        # Creatinine severity
        if test == "creatinine":
            val = lab.get("value", 0)
            if isinstance(val, (int, float)):
                if val >= 2.0:
                    return "Critical"
                elif val >= 1.5:
                    return "High"
                elif val >= 1.3:
                    return "Moderate"

        # eGFR severity
        if test == "egfr":
            val = lab.get("value", 100)
            if isinstance(val, (int, float)):
                if val < 30:
                    return "Critical"
                elif val < 45:
                    return "High"
                elif val < 60:
                    return "Moderate"

        # General fallback
        if "elevated" in status or "high" in status:
            return "Moderate"
        if "low" in status:
            return "Moderate"

        return "Low"
