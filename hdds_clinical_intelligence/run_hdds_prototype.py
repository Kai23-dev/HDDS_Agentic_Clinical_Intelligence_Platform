#!/usr/bin/env python3
"""
HDDS Clinical Intelligence Prototype — Runner Script

Loads synthetic patient data, runs all six agents in sequence,
and saves the combined AI medical insights to outputs/ai_medical_insights.json.

Supports both single-patient and multi-patient modes:
    python run_hdds_prototype.py                  # Default: single patient
    python run_hdds_prototype.py --all            # All patients from all_patients.json
    python run_hdds_prototype.py --patient SYNTH-002  # Specific patient by ID

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
SINGLE_PATIENT_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "patient_profile.json")
ALL_PATIENTS_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "all_patients.json")
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

    return data


def load_all_patients(filepath: str) -> list:
    """Load multiple patient profiles from JSON array file."""
    if not os.path.exists(filepath):
        print(f"ERROR: Multi-patient data file not found at: {filepath}")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        data = [data]

    return data


def run_all_agents(patient_data: dict) -> dict:
    """Run all six agents and collect their outputs."""

    agent_outputs = {}

    # Agent 1: Clinical Summary
    summary_agent = ClinicalSummaryAgent()
    agent_outputs["clinical_summary"] = summary_agent.run(patient_data)

    # Agent 2: Risk Assessment
    risk_agent = RiskAssessmentAgent()
    agent_outputs["risk_assessment"] = risk_agent.run(patient_data)

    # Agent 3: Early Detection
    detection_agent = EarlyDetectionAgent()
    agent_outputs["early_detection"] = detection_agent.run(patient_data)

    # Agent 4: Recommendations
    rec_agent = RecommendationAgent()
    agent_outputs["recommendations"] = rec_agent.run(patient_data)

    # Agent 5: Evidence Validation (needs outputs from other agents)
    validation_agent = EvidenceValidationAgent()
    agent_outputs["evidence_validation"] = validation_agent.run(patient_data, agent_outputs)

    # Agent 6: Follow-up Actions (needs all previous outputs)
    followup_agent = FollowupActionAgent()
    agent_outputs["followup_actions"] = followup_agent.run(patient_data, agent_outputs)

    return agent_outputs


def process_single_patient(patient_data: dict, patient_num: int = 1, total: int = 1) -> dict:
    """Process a single patient through the agent pipeline."""
    name = patient_data.get("patient_profile", {}).get("name", "Unknown")
    pid = patient_data.get("patient_profile", {}).get("patient_id", "N/A")

    print(f"  [{patient_num}/{total}] Processing: {name} ({pid})")

    print(f"         Running 6 agents...", end="")
    agent_outputs = run_all_agents(patient_data)
    print(" Done.")

    # Quick summary
    risk_level = agent_outputs.get("risk_assessment", {}).get("risk_level", "N/A")
    total_flags = agent_outputs.get("early_detection", {}).get("total_flags", 0)
    total_recs = agent_outputs.get("recommendations", {}).get("total_recommendations", 0)
    total_actions = agent_outputs.get("followup_actions", {}).get("total_actions", 0)
    validation = agent_outputs.get("evidence_validation", {}).get("validation_status", "N/A")

    print(f"         Risk: {risk_level} | Flags: {total_flags} | "
          f"Recs: {total_recs} | Actions: {total_actions} | Validation: {validation}")

    return {
        "patient_id": pid,
        "patient_name": name,
        "agent_results": agent_outputs,
    }


def save_output(results: dict, output_path: str) -> None:
    """Save the combined insights to a JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"  Output saved to: {output_path}")


def print_banner():
    """Print the application banner."""
    print()
    print("=" * 62)
    print("   HDDS Agentic Clinical Intelligence Platform")
    print("   Prototype Runner v2.0")
    print("=" * 62)
    print()


def print_usage():
    """Print usage information."""
    print("Usage:")
    print("  python run_hdds_prototype.py                    # Single patient (default)")
    print("  python run_hdds_prototype.py --all              # All patients")
    print("  python run_hdds_prototype.py --patient SYNTH-002  # Specific patient")
    print()


def main():
    """Main entry point."""
    print_banner()

    # Parse arguments
    args = sys.argv[1:]
    mode = "single"
    target_patient_id = None

    if "--all" in args:
        mode = "all"
    elif "--patient" in args:
        mode = "specific"
        idx = args.index("--patient")
        if idx + 1 < len(args):
            target_patient_id = args[idx + 1]
        else:
            print("ERROR: --patient requires a patient ID argument.")
            print_usage()
            sys.exit(1)
    elif "--help" in args or "-h" in args:
        print_usage()
        sys.exit(0)

    # Step 1: Load data
    print("[Step 1] Loading patient data...")

    if mode == "single":
        patient_data = load_patient_data(SINGLE_PATIENT_PATH)
        patients = [patient_data]
        print(f"  Loaded 1 patient from patient_profile.json")
    else:
        patients = load_all_patients(ALL_PATIENTS_PATH)
        print(f"  Loaded {len(patients)} patient(s) from all_patients.json")

        if mode == "specific":
            filtered = [
                p for p in patients
                if p.get("patient_profile", {}).get("patient_id") == target_patient_id
            ]
            if not filtered:
                print(f"  ERROR: Patient ID '{target_patient_id}' not found.")
                available = [p.get("patient_profile", {}).get("patient_id", "?") for p in patients]
                print(f"  Available IDs: {', '.join(available)}")
                sys.exit(1)
            patients = filtered
            print(f"  Filtered to patient: {target_patient_id}")

    print()

    # Step 2: Run agents
    print("[Step 2] Running agent pipeline...")
    all_results = []
    for i, patient in enumerate(patients):
        result = process_single_patient(patient, i + 1, len(patients))
        all_results.append(result)
    print()

    # Step 3: Build final output
    print("[Step 3] Saving output...")
    final_output = {
        "metadata": {
            "project": "HDDS Agentic Clinical Intelligence Platform",
            "version": "2.0.0-prototype",
            "generated_at": datetime.now().isoformat(),
            "data_source": "Synthetic sample data (not real patient data)",
            "total_patients_processed": len(all_results),
            "responsible_ai_note": RESPONSIBLE_AI_NOTE,
        },
        "patients": all_results,
    }

    save_output(final_output, OUTPUT_PATH)
    print()

    # Summary table
    print("-" * 62)
    print("  RESULTS SUMMARY")
    print("-" * 62)
    print(f"  {'Patient':<30} {'Risk':<8} {'Flags':<7} {'Recs':<6} {'Actions':<8}")
    print(f"  {'-' * 30} {'-' * 7} {'-' * 6} {'-' * 5} {'-' * 7}")

    for r in all_results:
        name = r["patient_name"][:28]
        ag = r["agent_results"]
        risk = ag.get("risk_assessment", {}).get("risk_level", "?")
        flags = ag.get("early_detection", {}).get("total_flags", 0)
        recs = ag.get("recommendations", {}).get("total_recommendations", 0)
        actions = ag.get("followup_actions", {}).get("total_actions", 0)
        print(f"  {name:<30} {risk:<8} {flags:<7} {recs:<6} {actions:<8}")

    print("-" * 62)
    print()
    print(f"  NOTE: {RESPONSIBLE_AI_NOTE}")
    print()

    # Dashboard hint
    dashboard_script = os.path.join(PROJECT_ROOT, "dashboard", "generate_dashboard.py")
    if os.path.exists(dashboard_script):
        print("  TIP: Generate the visual dashboard with:")
        print("       python dashboard/generate_dashboard.py")
        print()

    print("  Done.")


if __name__ == "__main__":
    main()
