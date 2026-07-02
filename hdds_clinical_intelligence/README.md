# HDDS Agentic Clinical Intelligence Platform

A beginner-friendly clinical intelligence prototype that uses **synthetic healthcare data**, rule-based extraction/harmonization, and **AI agents** to generate clinician-reviewable medical insights.

> **⚠️ Responsible AI Note:** All outputs are generated for prototype purposes only and are intended for clinician review. This is not a final diagnosis or treatment decision.

---

## Project Objective

Build an HDDS-style clinical intelligence prototype that demonstrates how multi-agent AI pipelines can analyze patient data and produce structured, traceable medical insights — all using **synthetic/sample data only**.

No company data, client data, real patient data, internal GDX details, secrets, or tokens are used anywhere in this project.

---

## Current Prototype Scope

- **Data:** 3 synthetic patient profiles covering different clinical scenarios (diabetes, heart failure, anemia)
- **Agents:** Six rule-based agents that process patient data and produce structured outputs
- **Output:** Combined JSON file (`ai_medical_insights.json`) with all agent results
- **Backend (API):** FastAPI server that serves the generated insights
- **Frontend (UI):** React 18 + Vite + Tailwind CSS dashboard

---

## Sample Patients

| ID | Name | Age | Conditions | Expected Risk |
|----|------|-----|------------|---------------|
| SYNTH-001 | John Doe | 58/M | Type 2 Diabetes, Hypertension | High |
| SYNTH-002 | Maria Garcia | 72/F | CHF, AFib, CKD Stage 3, Osteoarthritis | High |
| SYNTH-003 | Emily Chen | 34/F | Asthma, Iron Deficiency Anemia | Low |

---

## How to Run

### 1. Run the AI Agent Pipeline
Generate the insights JSON file (requires standard Python 3.8+).

```bash
cd hdds_clinical_intelligence
python run_hdds_prototype.py --all
```

### 2. Start the FastAPI Backend
Serve the insights via REST API on `localhost:8000`.

```bash
cd hdds_clinical_intelligence
pip install fastapi uvicorn
uvicorn api:app --reload
```

### 3. Start the React Frontend
Run the Vite development server for the dashboard on `localhost:5173`.

```bash
cd hdds_clinical_intelligence/frontend
npm install
npm run dev
```

Then open `http://localhost:5173` in your browser.

---

## Folder Structure

```
hdds_clinical_intelligence/
├── agents/                        # AI Agent logic
├── api.py                         # FastAPI server
├── data/                          # Synthetic patient JSON data
├── docs/                          # Architecture & design docs
├── extraction/                    # Schema definitions
├── frontend/                      # React + Vite application
│   ├── src/
│   │   ├── App.jsx                # Main dashboard UI
│   │   └── index.css              # Tailwind + custom CSS
│   ├── package.json
│   └── tailwind.config.js
├── outputs/                       # Generated insights JSON
├── run_hdds_prototype.py          # Main AI runner script
└── README.md
```
