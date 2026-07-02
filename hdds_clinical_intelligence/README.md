# HDDS Agentic Clinical Intelligence Platform

A beginner-friendly clinical intelligence prototype that uses **synthetic healthcare data**, rule-based extraction/harmonization, and **AI agents** to generate clinician-reviewable medical insights.

> **⚠️ Responsible AI Note:** All outputs are generated for prototype purposes only and are intended for clinician review. This is not a final diagnosis or treatment decision.

---

## Project Objective

Build an HDDS-style clinical intelligence prototype that demonstrates how multi-agent AI pipelines can analyze patient data and produce structured, traceable medical insights — all using **synthetic/sample data only**.

No company data, client data, real patient data, internal GDX details, secrets, or tokens are used anywhere in this project.

---

## Current Prototype Scope

- **Data:** Synthetic patient profile (`patient_profile.json`) with conditions, medications, labs, procedures, and encounters.
- **Agents:** Six rule-based agents that process patient data and produce structured outputs.
- **Output:** Combined JSON file (`ai_medical_insights.json`) with all agent results.
- **Dependencies:** Python standard library + JSON only. No external packages required.

---

## Agent Flow

```
patient_profile.json
        │
        ▼
┌─────────────────────┐
│ 1. Clinical Summary │  → Summarizes history, meds, abnormal labs
└────────┬────────────┘
         │
┌────────▼────────────┐
│ 2. Risk Assessment  │  → Classifies risk as Low / Medium / High
└────────┬────────────┘
         │
┌────────▼────────────┐
│ 3. Early Detection  │  → Flags abnormal labs, monitoring gaps
└────────┬────────────┘
         │
┌────────▼──────────────┐
│ 4. Recommendation     │  → Generates clinician-review drafts
└────────┬──────────────┘
         │
┌────────▼──────────────────┐
│ 5. Evidence Validation    │  → Maps outputs back to source fields
└────────┬──────────────────┘
         │
┌────────▼──────────────┐
│ 6. Follow-up Action   │  → Suggests prioritized follow-up actions
└────────┬──────────────┘
         │
         ▼
  ai_medical_insights.json
```

---

## Folder Structure

```
hdds_clinical_intelligence/
├── agents/                        # Agent modules
│   ├── __init__.py
│   ├── clinical_summary_agent.py
│   ├── risk_assessment_agent.py
│   ├── early_detection_agent.py
│   ├── recommendation_agent.py
│   ├── evidence_validation_agent.py
│   └── followup_action_agent.py
├── data/
│   ├── raw/                       # Placeholder for future raw data
│   ├── processed/
│   │   └── patient_profile.json   # Synthetic sample patient
│   └── sample_notes/              # Placeholder for clinical notes
├── docs/
│   ├── architecture.md
│   ├── prototype_roadmap.md
│   └── responsible_ai_notes.md
├── extraction/
│   ├── azure_health_nlp_optional.md
│   ├── extraction_schema.json
│   └── gdx_extraction_reference.md
├── outputs/
│   └── ai_medical_insights.json   # Generated output
├── dashboard/                     # Placeholder for future dashboard
├── .gitignore
├── README.md
└── run_hdds_prototype.py          # Main runner script
```

---

## How to Run

```bash
cd hdds_clinical_intelligence
python run_hdds_prototype.py
```

Output will be saved to `outputs/ai_medical_insights.json`.

---

## Future Plan

- Replace sample JSON with **Synthea CSV extraction** for realistic synthetic patient populations
- Add NLP-based extraction using Azure Health NLP or similar services
- Build a Streamlit/Flask dashboard for visual insights
- Integrate with FHIR-compatible data formats
- Add more sophisticated ML-based agents alongside the rule-based ones

---

## Requirements

- Python 3.8 or higher
- No external packages — uses Python standard library only
