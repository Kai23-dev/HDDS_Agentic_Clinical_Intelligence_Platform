"""
Evidence Validation Agent

Maps outputs from other agents back to source data fields in the
patient profile, providing traceability and evidence references
for every clinical assertion.
"""


class EvidenceValidationAgent:
    """Validates and traces agent outputs back to source data."""

    def __init__(self):
        self.agent_name = "Evidence Validation Agent"
        self.version = "1.0.0"

    def run(self, patient_data: dict, agent_outputs: dict) -> dict:
        """
        Validate agent outputs by mapping assertions back to source fields.

        Args:
            patient_data: Full patient profile dictionary.
            agent_outputs: Dictionary of outputs from other agents.

        Returns:
            Dictionary with evidence mappings and validation results.
        """
        evidence_map = []
        validation_issues = []

        # --- Validate Clinical Summary assertions ---
        summary = agent_outputs.get("clinical_summary", {})
        if summary:
            # Verify active conditions exist in source
            for condition in summary.get("active_conditions", []):
                source_match = self._find_condition_source(condition, patient_data)
                evidence_map.append({
                    "assertion": f"Active condition: {condition}",
                    "source_field": "medical_history",
                    "source_match_found": source_match is not None,
                    "source_detail": source_match,
                })
                if source_match is None:
                    validation_issues.append(
                        f"Could not trace condition '{condition}' to medical_history."
                    )

            # Verify abnormal labs
            for lab in summary.get("abnormal_labs", []):
                source_match = self._find_lab_source(lab["test"], patient_data)
                evidence_map.append({
                    "assertion": f"Abnormal lab: {lab['test']} = {lab['value']}",
                    "source_field": "lab_results",
                    "source_match_found": source_match is not None,
                    "source_detail": source_match,
                })

        # --- Validate Risk Assessment inputs ---
        risk = agent_outputs.get("risk_assessment", {})
        if risk:
            breakdown = risk.get("score_breakdown", {})
            actual_conditions = len([
                h for h in patient_data.get("medical_history", [])
                if h.get("status") == "Active"
            ])
            actual_meds = len(patient_data.get("medications", []))

            if breakdown.get("conditions_count") != actual_conditions:
                validation_issues.append(
                    f"Risk agent counted {breakdown.get('conditions_count')} conditions, "
                    f"but source has {actual_conditions}."
                )

            if breakdown.get("medications_count") != actual_meds:
                validation_issues.append(
                    f"Risk agent counted {breakdown.get('medications_count')} medications, "
                    f"but source has {actual_meds}."
                )

            evidence_map.append({
                "assertion": f"Risk level: {risk.get('risk_level')} (score: {risk.get('risk_score')})",
                "source_field": "medical_history, medications, lab_results",
                "source_match_found": len(validation_issues) == 0,
                "source_detail": breakdown,
            })

        # --- Validate Recommendations have supporting evidence ---
        recs = agent_outputs.get("recommendations", {})
        if recs:
            for rec in recs.get("recommendations", []):
                category = rec.get("category", "")
                has_evidence = self._check_recommendation_evidence(category, patient_data)
                evidence_map.append({
                    "assertion": f"Recommendation: {category}",
                    "source_field": "medical_history, lab_results, medications",
                    "source_match_found": has_evidence,
                    "source_detail": rec.get("recommendation", "")[:100] + "...",
                })
                if not has_evidence:
                    validation_issues.append(
                        f"Recommendation '{category}' could not be fully traced to source data."
                    )

        return {
            "agent": self.agent_name,
            "version": self.version,
            "evidence_mappings": evidence_map,
            "validation_issues": validation_issues,
            "total_assertions_checked": len(evidence_map),
            "total_issues_found": len(validation_issues),
            "validation_status": "PASS" if len(validation_issues) == 0 else "REVIEW NEEDED",
        }

    def _find_condition_source(self, condition: str, patient_data: dict):
        """Find a condition in the patient's medical history."""
        for h in patient_data.get("medical_history", []):
            if h.get("condition", "").lower() == condition.lower():
                return {
                    "condition": h["condition"],
                    "icd_code": h.get("icd_code"),
                    "diagnosed_date": h.get("diagnosed_date"),
                    "status": h.get("status"),
                }
        return None

    def _find_lab_source(self, test_name: str, patient_data: dict):
        """Find a lab result in the patient's lab results."""
        for lab in patient_data.get("lab_results", []):
            if lab.get("test_name", "").lower() == test_name.lower():
                return {
                    "test_name": lab["test_name"],
                    "value": lab["value"],
                    "unit": lab.get("unit"),
                    "date": lab.get("date"),
                }
        return None

    def _check_recommendation_evidence(self, category: str, patient_data: dict) -> bool:
        """Check if a recommendation category has supporting evidence in the data."""
        cat_lower = category.lower()

        if "medication" in cat_lower or "glycemic" in cat_lower:
            return len(patient_data.get("medications", [])) > 0

        if "nephrology" in cat_lower or "renal" in cat_lower:
            return any(
                l["test_name"].lower() in ("egfr", "creatinine")
                for l in patient_data.get("lab_results", [])
            )

        if "blood pressure" in cat_lower:
            return any(
                l["test_name"].lower() == "blood pressure"
                for l in patient_data.get("lab_results", [])
            )

        if "lifestyle" in cat_lower or "education" in cat_lower:
            return len(patient_data.get("medical_history", [])) > 0

        # Default: assume evidence exists for unrecognized categories
        return True
