"""
Follow-up Action Agent

Suggests clinician-review follow-up actions based on the combined
outputs from all previous agents. Prioritizes actions by urgency.
"""

from datetime import datetime


class FollowupActionAgent:
    """Generates prioritized follow-up actions for clinician review."""

    def __init__(self):
        self.agent_name = "Follow-up Action Agent"
        self.version = "1.0.0"

    def run(self, patient_data: dict, agent_outputs: dict) -> dict:
        """
        Generate follow-up actions from combined agent outputs.

        Args:
            patient_data: Full patient profile dictionary.
            agent_outputs: Dictionary of outputs from other agents.

        Returns:
            Dictionary containing prioritized follow-up actions.
        """
        actions = []
        today = datetime.now().strftime("%Y-%m-%d")

        # --- Actions from Risk Assessment ---
        risk = agent_outputs.get("risk_assessment", {})
        risk_level = risk.get("risk_level", "Unknown")

        if risk_level == "High":
            actions.append({
                "action": "Schedule urgent follow-up appointment within 1-2 weeks",
                "priority": "Urgent",
                "category": "Scheduling",
                "rationale": f"Patient risk level is {risk_level} (score: {risk.get('risk_score', 'N/A')})",
                "status": "Pending Clinician Review",
            })
        elif risk_level == "Medium":
            actions.append({
                "action": "Schedule follow-up appointment within 4-6 weeks",
                "priority": "Routine",
                "category": "Scheduling",
                "rationale": f"Patient risk level is {risk_level}",
                "status": "Pending Clinician Review",
            })

        # --- Actions from Early Detection alerts ---
        early_detection = agent_outputs.get("early_detection", {})
        for alert in early_detection.get("alerts", []):
            actions.append({
                "action": f"Review alert: {alert}",
                "priority": "High",
                "category": "Clinical Review",
                "rationale": "Flagged by Early Detection Agent",
                "status": "Pending Clinician Review",
            })

        # --- Actions from Recommendations ---
        recs = agent_outputs.get("recommendations", {})
        for rec in recs.get("recommendations", []):
            if rec.get("priority") == "High":
                actions.append({
                    "action": f"Act on recommendation: {rec['category']}",
                    "priority": "High",
                    "category": "Treatment",
                    "rationale": rec.get("recommendation", "")[:150],
                    "status": "Pending Clinician Review",
                })

        # --- Lab follow-up actions ---
        flagged = early_detection.get("flagged_abnormal_results", [])
        if flagged:
            actions.append({
                "action": f"Order repeat labs for {len(flagged)} abnormal result(s) in 1-3 months",
                "priority": "Medium",
                "category": "Lab Orders",
                "rationale": "Trending abnormal results requires monitoring.",
                "status": "Pending Clinician Review",
            })

        # --- Monitoring gap actions ---
        monitoring = early_detection.get("chronic_monitoring_needs", [])
        missing_tests = [
            m for m in monitoring if not m.get("recently_completed", False)
        ]
        if missing_tests:
            test_names = list(set(m["recommended_test"] for m in missing_tests))
            actions.append({
                "action": f"Order missing monitoring tests: {', '.join(test_names)}",
                "priority": "Medium",
                "category": "Preventive Care",
                "rationale": "Chronic disease monitoring gap identified.",
                "status": "Pending Clinician Review",
            })

        # --- Validation issues follow-up ---
        validation = agent_outputs.get("evidence_validation", {})
        if validation.get("validation_status") == "REVIEW NEEDED":
            actions.append({
                "action": "Review evidence validation issues before acting on insights",
                "priority": "High",
                "category": "Data Quality",
                "rationale": f"{validation.get('total_issues_found', 0)} validation issue(s) found.",
                "status": "Pending Clinician Review",
            })

        # --- Sort by priority ---
        priority_order = {"Urgent": 0, "High": 1, "Medium": 2, "Routine": 3}
        actions.sort(key=lambda a: priority_order.get(a["priority"], 99))

        return {
            "agent": self.agent_name,
            "version": self.version,
            "generated_date": today,
            "total_actions": len(actions),
            "follow_up_actions": actions,
            "disclaimer": "All follow-up actions require clinician review and approval before execution.",
        }
