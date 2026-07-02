#!/usr/bin/env python3
"""
HDDS Clinical Intelligence Prototype — Runner Script

Loads synthetic patient data, runs all six agents in sequence,
and saves the combined AI medical insights to outputs/ai_medical_insights.json.

Usage:
    python run_hdds_prototype.py

Dependencies:
    Python 3.8+ (standard library only — no external packages needed)
"""

import json
import os
import sys
from datetime import datetime

# Ensure the project root is on the path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from agents.clinical_summary_agent import ClinicalSummaryAgent
from agents.risk_assessment_agent import RiskAssessmentAgent
from agents.early_detection_agent import EarlyDetectionAgent
from agents.recommendation_agent import RecommendationAgent
from agents.evidence_validation_agent import EvidenceValidationAgent
from agents.followup_action_agent import FollowupActionAgent


# --- Configuration ---
INPUT_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "patient_profile.json")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "ai_medical_insights.json")

RESPONSIBLE_AI_NOTE = (
    "This output is generated for prototype purposes only and is intended for "
    "clinician review. It is not a final diagnosis or treatment decision."
)


def load_patient_data(filepath: str) -> dict:
    """Load patient profile from JSON file."""
    if not os.path.exists(filepath):
        print(f"ERROR: Patient data file not found at: {filepath}")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"  Loaded patient: {data.get('patient_profile', {}).get('name', 'Unknown')}")
    return data


def run_all_agents(patient_data: dict) -> dict:
    """Run all six agents and collect their outputs."""

    agent_outputs = {}

    # Agent 1: Clinical Summary
    print("  [1/6] Running Clinical Summary Agent...")
    summary_agent = ClinicalSummaryAgent()
    agent_outputs["clinical_summary"] = summary_agent.run(patient_data)

    # Agent 2: Risk Assessment
    print("  [2/6] Running Risk Assessment Agent...")
    risk_agent = RiskAssessmentAgent()
    agent_outputs["risk_assessment"] = risk_agent.run(patient_data)

    # Agent 3: Early Detection
    print("  [3/6] Running Early Detection Agent...")
    detection_agent = EarlyDetectionAgent()
    agent_outputs["early_detection"] = detection_agent.run(patient_data)

    # Agent 4: Recommendations
    print("  [4/6] Running Recommendation Agent...")
    rec_agent = RecommendationAgent()
    agent_outputs["recommendations"] = rec_agent.run(patient_data)

    # Agent 5: Evidence Validation (needs outputs from other agents)
    print("  [5/6] Running Evidence Validation Agent...")
    validation_agent = EvidenceValidationAgent()
    agent_outputs["evidence_validation"] = validation_agent.run(patient_data, agent_outputs)

    # Agent 6: Follow-up Actions (needs all previous outputs)
    print("  [6/6] Running Follow-up Action Agent...")
    followup_agent = FollowupActionAgent()
    agent_outputs["followup_actions"] = followup_agent.run(patient_data, agent_outputs)

    return agent_outputs


def save_output(agent_outputs: dict, output_path: str) -> None:
    """Save the combined insights to a JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    final_output = {
        "metadata": {
            "project": "HDDS Agentic Clinical Intelligence Platform",
            "version": "1.0.0-prototype",
            "generated_at": datetime.now().isoformat(),
            "data_source": "Synthetic sample data (not real patient data)",
            "responsible_ai_note": RESPONSIBLE_AI_NOTE,
        },
        "patient_id": agent_outputs.get("clinical_summary", {}).get("summary_text", "")[:50],
        "agent_results": agent_outputs,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)

    print(f"  Output saved to: {output_path}")


def main():
    """Main entry point."""
    print("=" * 60)
    print("  HDDS Agentic Clinical Intelligence Platform")
    print("  Prototype Runner v1.0")
    print("=" * 60)
    print()

    # Step 1: Load data
    print("[Step 1] Loading patient data...")
    patient_data = load_patient_data(INPUT_PATH)
    print()

    # Step 2: Run all agents
    print("[Step 2] Running all agents...")
    agent_outputs = run_all_agents(patient_data)
    print()

    # Step 3: Save output
    print("[Step 3] Saving output...")
    save_output(agent_outputs, OUTPUT_PATH)
    print()

    # Summary
    risk_level = agent_outputs.get("risk_assessment", {}).get("risk_level", "N/A")
    total_recs = agent_outputs.get("recommendations", {}).get("total_recommendations", 0)
    total_actions = agent_outputs.get("followup_actions", {}).get("total_actions", 0)
    total_flags = agent_outputs.get("early_detection", {}).get("total_flags", 0)
    validation_status = agent_outputs.get("evidence_validation", {}).get("validation_status", "N/A")

    print("-" * 60)
    print("  RESULTS SUMMARY")
    print("-" * 60)
    print(f"  Risk Level        : {risk_level}")
    print(f"  Abnormal Flags    : {total_flags}")
    print(f"  Recommendations   : {total_recs}")
    print(f"  Follow-up Actions : {total_actions}")
    print(f"  Validation Status : {validation_status}")
    print("-" * 60)
    print()
    print(f"  NOTE: {RESPONSIBLE_AI_NOTE}")
    print()
    print("  Done.")


if __name__ == "__main__":
    main()
