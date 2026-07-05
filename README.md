# HDDS Agentic Clinical Intelligence Platform

An AI-powered **Hospital Discharge Data Summary (HDDS)** platform that runs patient
records through a pipeline of coordinated AI agents to produce **clinician-reviewable**
medical insights. Built on a **multi-agent architecture** with a **pluggable RAG system**,
it reduces clinician cognitive load, surfaces critical risks, and keeps a human in the loop.

> ⚠️ **Responsible-AI note.** This is a prototype using **synthetic** patient data. Every
> output is decision support for **clinician review — never a final diagnosis or treatment
> decision.** See [`hdds_clinical_intelligence/ROADMAP.md`](hdds_clinical_intelligence/ROADMAP.md)
> for what must be completed before any real clinical use.

---

## 🌟 Key Features

| Feature | What it does |
|---|---|
| **Orchestrator + 7 sub-agents** | An `OrchestratorAgent` coordinates Clinical Summary, Risk Assessment, Early Detection, Recommendations, **Medication Prescription**, Evidence Validation, and Follow-up Actions. |
| **Pluggable RAG** | One interface, three swappable backends: **EY GDX** (drop-in slot) → **Azure RAG** (real embeddings + retrieval + cited synthesis) → **keyword fallback** (offline). Selected via `RAG_BACKEND`. |
| **Azure OpenAI integration** | Central client for chat + embeddings; the intended production path on Azure. Degrades to Gemini, then rule-based, when unset. |
| **Structured data ingestion** | Parses demographics, labs, and medications from **Synthea** CSV datasets. |
| **Clinical chat assistant** | Natural-language Q&A grounded in a single patient's record. |
| **Human-in-the-loop** | Clinicians accept/reject AI suggestions; medication suggestions are flagged as requiring approval. |
| **FHIR export** | Exports a patient as a FHIR R4 bundle for EHR interoperability. |

---

## 🏗️ Architecture

```
Frontend (React/Vite/Tailwind)
        │  axios + bearer token
        ▼
FastAPI  (api.py)
        │
        ▼
OrchestratorAgent ──► RAG backend (GDX │ Azure │ keyword)  ── injects unstructured insights
        │
        ├─► ClinicalSummary   ├─► Recommendation        ├─► EvidenceValidation
        ├─► RiskAssessment     ├─► MedicationPrescription └─► FollowupAction
        └─► EarlyDetection
        │
        ▼
outputs/ai_medical_insights.json ──► Frontend dashboard
```

The RAG layer is fully swappable behind `rag.factory.get_rag_system()`, so the EY GDX
system can be plugged in without touching the orchestrator, API, or chat agent.

---

## 🛠️ Technology Stack

- **Backend:** Python, FastAPI, Uvicorn
- **AI/LLM:** Azure OpenAI (chat + embeddings), Google Gemini (fallback), rule-based agents
- **Frontend:** React 18, Vite, Tailwind CSS, Lucide Icons
- **Data:** Synthea (structured CSVs), Asclepius synthetic clinical notes (unstructured)

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/Kai23-dev/HDDS_Agentic_Clinical_Intelligence_Platform.git
cd HDDS_Agentic_Clinical_Intelligence_Platform/hdds_clinical_intelligence

# 2. Backend
python -m venv .venv && source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
cp .env.example .env                                    # fill in keys (all optional)
python api.py                                           # http://127.0.0.1:8000

# 3. Frontend (second terminal)
cd frontend && npm install && npm run dev               # http://localhost:5173
```

📖 **Full setup, environment variables, and Azure deployment notes:**
[`hdds_clinical_intelligence/SETUP.md`](hdds_clinical_intelligence/SETUP.md)

With **no keys set** the platform runs fully offline (rule-based agents + keyword RAG).
Adding Azure OpenAI credentials upgrades it to real LLM chat and embeddings-based RAG —
no code changes needed.

---

## 🔐 Test Accounts (prototype auth)

| Role | Email | Password |
|------|-------|----------|
| Doctor | `doctor@ey.com` | `password123` |
| Admin | `admin@ey.com` | `admin` |

> These are **mock** credentials for demo only. Production-grade authentication (signed
> JWTs, hashed passwords, expiry) is tracked as Tier-1 work in the roadmap.

---

## 📁 Repository Structure

```text
HDDS_Agentic_Clinical_Intelligence_Platform/
├── README.md                        # this file (project overview)
└── hdds_clinical_intelligence/      # the application
    ├── api.py                       # FastAPI backend entry point
    ├── run_hdds_prototype.py        # standalone pipeline runner (CLI)
    ├── agents/                      # orchestrator + 7 sub-agents + chat agent
    ├── rag/                         # pluggable RAG (base, factory, gdx, azure, keyword)
    ├── llm/                         # Azure OpenAI client wrapper
    ├── data/                        # raw + processed synthetic datasets
    ├── data_ingestion/              # Synthea parser, FHIR converter, notes generator
    ├── frontend/                    # React + Vite + Tailwind UI
    ├── outputs/                     # generated AI insight JSON
    ├── SETUP.md                     # install & Azure deployment guide
    ├── ROADMAP.md                   # path to real clinical use (Tier 1–3)
    └── CLAUDE.md                    # architecture guide for contributors
```

---

## 📚 Documentation

- **[SETUP.md](hdds_clinical_intelligence/SETUP.md)** — clone-and-run on any machine + Azure deployment.
- **[ROADMAP.md](hdds_clinical_intelligence/ROADMAP.md)** — honest gap analysis and prioritized work.
- **[CLAUDE.md](hdds_clinical_intelligence/CLAUDE.md)** — architecture and conventions for contributors.

---

*Disclaimer: Prototype built for demonstration on synthetic data. Not intended for real
clinical diagnosis or treatment decisions.*
