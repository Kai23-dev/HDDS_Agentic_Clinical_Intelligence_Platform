# HDDS Agentic Clinical Intelligence Platform

A full-stack clinical intelligence prototype that uses **synthetic healthcare data**, rule-based extraction/harmonization, and **AI agents** to generate clinician-reviewable medical insights — served through a **FastAPI** backend and visualized on a **React + Tailwind CSS** dashboard.

> **Responsible AI Note:** All outputs are generated for prototype/demo purposes only and are intended for clinician review. This is not a final diagnosis or treatment decision.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **AI Agents** | Python 3.8+ (standard library) |
| **Backend API** | FastAPI + Uvicorn |
| **Frontend UI** | React 18 + Vite + Tailwind CSS |
| **Data** | Synthetic JSON (no real patient data) |

---

## Quick Start (Clone & Run)

### Prerequisites
- Python 3.8+ installed
- Node.js 18+ and npm installed
- Git installed

### Step-by-step

```bash
# 1. Clone the repo
git clone https://github.com/Kai23-dev/HDDS_Agentic_Clinical_Intelligence_Platform.git
cd HDDS_Agentic_Clinical_Intelligence_Platform/hdds_clinical_intelligence

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run the AI agent pipeline to generate insights
python run_hdds_prototype.py --all

# 4. Start the FastAPI backend (Terminal 1)
#    IMPORTANT: Run this from the hdds_clinical_intelligence/ folder
python api.py

# 5. Start the React frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

Then open **http://localhost:5173** in your browser.

### One-command start (Git Bash / macOS / Linux)

```bash
cd hdds_clinical_intelligence
bash start.sh
```

---

## Project Structure

```
HDDS_Agentic_Clinical_Intelligence_Platform/
|-- README.md                          # Root overview
|-- hdds_clinical_intelligence/        # Main project folder
    |-- api.py                         # FastAPI backend server
    |-- run_hdds_prototype.py          # AI agent pipeline runner
    |-- requirements.txt               # Python dependencies
    |-- start.sh                       # One-command startup script
    |
    |-- agents/                        # 6 AI agent modules
    |   |-- __init__.py
    |   |-- clinical_summary_agent.py
    |   |-- risk_assessment_agent.py
    |   |-- early_detection_agent.py
    |   |-- recommendation_agent.py
    |   |-- evidence_validation_agent.py
    |   |-- followup_action_agent.py
    |
    |-- data/
    |   |-- processed/
    |   |   |-- patient_profile.json   # Single patient (default)
    |   |   |-- all_patients.json      # All 3 synthetic patients
    |   |-- raw/                       # For future raw data
    |   |-- sample_notes/              # For future clinical notes
    |
    |-- frontend/                      # React + Vite + Tailwind CSS
    |   |-- src/
    |   |   |-- App.jsx                # Main dashboard component
    |   |   |-- index.css              # Tailwind + custom styles
    |   |   |-- main.jsx               # React entry point
    |   |-- package.json
    |   |-- tailwind.config.js
    |   |-- vite.config.js
    |
    |-- outputs/                       # Generated AI insights
    |   |-- ai_medical_insights.json
    |
    |-- docs/                          # Design documentation
    |   |-- architecture.md
    |   |-- prototype_roadmap.md
    |   |-- responsible_ai_notes.md
    |
    |-- extraction/                    # Schema & reference docs
        |-- extraction_schema.json
        |-- azure_health_nlp_optional.md
        |-- gdx_extraction_reference.md
```

---

## Agent Pipeline

The runner executes 6 agents sequentially on each patient profile:

```
Patient JSON --> [1] Clinical Summary
             --> [2] Risk Assessment (Low / Medium / High)
             --> [3] Early Detection (flag abnormal labs)
             --> [4] Recommendations (clinician-review drafts)
             --> [5] Evidence Validation (trace assertions to source)
             --> [6] Follow-up Actions (prioritized next steps)
             --> ai_medical_insights.json --> FastAPI --> React Dashboard
```

### Runner CLI options

```bash
python run_hdds_prototype.py              # Single default patient
python run_hdds_prototype.py --all        # All 3 patients
python run_hdds_prototype.py --patient SYNTH-002   # Specific patient
```

---

## Sample Patients

| ID | Name | Age | Conditions | Expected Risk |
|----|------|-----|------------|---------------|
| SYNTH-001 | John Doe | 58/M | Type 2 Diabetes, Hypertension | High |
| SYNTH-002 | Maria Garcia | 72/F | CHF, AFib, CKD Stage 3, Osteoarthritis | High |
| SYNTH-003 | Emily Chen | 34/F | Asthma, Iron Deficiency Anemia | Low |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/insights` | Returns full AI insights JSON |

---

## Troubleshooting

### "Could not import module api"
You are running `uvicorn` from the **wrong directory**. Make sure you are inside `hdds_clinical_intelligence/` (where `api.py` lives), not the root folder or `frontend/`.

```bash
cd hdds_clinical_intelligence
uvicorn api:app --reload
```

Or simply use:
```bash
python api.py
```

### Frontend shows "Connection Error"
The FastAPI backend is not running. Start it first in a separate terminal (see Quick Start above).

### "Insights JSON not found"
You haven't generated the insights yet. Run the pipeline first:
```bash
python run_hdds_prototype.py --all
```

---

## Future Roadmap

- [ ] Synthea CSV extraction for realistic patient populations
- [ ] NLP-based clinical note extraction (Azure Health NLP)
- [ ] FHIR-compatible data formats
- [ ] User authentication & role-based access
- [ ] Patient comparison view on the dashboard
- [ ] Export to PDF report generation

---

## Requirements

- Python 3.8+
- Node.js 18+ / npm
- No database needed — all data is JSON-based
