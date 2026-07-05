# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

HDDS Agentic Clinical Intelligence Platform — a clinician-facing prototype that runs synthetic
patient data through a pipeline of AI agents to produce reviewable medical insights. FastAPI
backend + React/Vite/Tailwind frontend. **All outputs are prototype-only, for clinician review,
never a final diagnosis.** Every generated insight carries this responsible-AI framing; preserve it.

> All commands below assume you are inside `hdds_clinical_intelligence/` (the project root that
> holds `api.py`). Running `uvicorn`/`api.py` from anywhere else fails with "Could not import module api".

## Commands

```bash
# Backend (Terminal 1) — serves on http://127.0.0.1:8000
python api.py                       # preferred; runs uvicorn with reload
uvicorn api:app --reload            # equivalent, must be run from this dir

# Frontend (Terminal 2) — serves on http://localhost:5173
cd frontend && npm install && npm run dev
npm run build                       # production build (vite)
npm run lint                        # oxlint

# One-command start (Git Bash / macOS / Linux): installs deps, runs pipeline, starts both servers
bash start.sh

# Standalone agent pipeline runner (writes outputs/ai_medical_insights.json)
python run_hdds_prototype.py            # single default patient
python run_hdds_prototype.py --all      # all sample patients
python run_hdds_prototype.py --patient SYNTH-002

# Regenerate processed data from raw sources
python data_ingestion/synthea_parser.py     # Synthea CSVs -> data/processed/patient_profiles.json
python data_ingestion/asclepius_ingest.py    # (re)build data/raw/asclepius_notes.json
```

There is no automated test suite. Verify changes by running the pipeline and exercising the API
endpoints (e.g. `POST /api/run-sample`) or the dashboard end-to-end.

## Environment

Copy `.env.example` to `.env`. All keys are **optional** — the system degrades gracefully to
rule-based/mock behavior when a key is absent:
- `AZURE_OPENAI_*` — primary LLM (chat agent) and the Azure RAG backend (embeddings + grounded
  synthesis). Use Azure OpenAI *deployment names*, not model names. This is the intended
  production path (deployed on Azure).
- `RAG_BACKEND` — `auto` (default: GDX → Azure → keyword), or force `gdx` / `azure` / `keyword`.
- `GEMINI_API_KEY` — chat-agent fallback if Azure OpenAI is not set (`gemini-2.5-flash`); otherwise keyword rules.
- `AZURE_LANGUAGE_ENDPOINT` / `AZURE_LANGUAGE_KEY` — enables Azure Health NLP entity extraction; otherwise skipped.

See `SETUP.md` for clone-and-run steps and `ROADMAP.md` for what remains before real clinical use.

## Architecture

The request flow is: **frontend → FastAPI (`api.py`) → `OrchestratorAgent` → sub-agents + GTX RAG → `outputs/ai_medical_insights.json` → frontend**.

- **`api.py`** — FastAPI app. Mock JWT auth: `POST /api/login` against the in-memory `MOCK_USERS`
  dict returns a `mock-jwt-token-...` string; all data endpoints require it via the `verify_token`
  dependency (it only checks the prefix). Key routes: `/api/run-sample`, `/api/load-synthea`,
  `/api/upload` (PDF/ZIP — currently maps any upload to the sample cardiology profile),
  `/api/insights`, `/api/chat`, `/api/fhir/{patient_id}`. `build_response()` is the shared entry
  that runs a patient list through the orchestrator and persists the result.

- **`agents/orchestrator_agent.py`** — `OrchestratorAgent.process_patient(patient_data)` is the
  central coordinator. It (1) pulls unstructured insights from the GTX RAG system, injects them
  into `patient_data["gtx_unstructured_insights"]`, then (2) calls the sub-agents in sequence and
  returns a dict keyed by agent output. **This is the real pipeline used by the API** — `agents/__init__.py`
  and the README still describe an older "6 rule-based agents" design; treat the orchestrator as source of truth.

- **Sub-agents** (`agents/*.py`) — each is a class with a `run()` method returning a plain dict.
  Most take `run(patient_data)`; **`EvidenceValidationAgent` and `FollowupActionAgent` take
  `run(patient_data, agent_outputs)`** because they depend on earlier agents' output. Agents are
  primarily rule/keyword-based over the patient dict. Current set: ClinicalSummary, RiskAssessment,
  EarlyDetection, Recommendation, MedicationPrescription, EvidenceValidation, FollowupAction.
  `chat_agent.py` is separate (invoked only by `/api/chat`, Gemini-backed).

- **`rag/` (pluggable RAG)** — one interface (`rag/base.py::BaseRAGSystem`), three backends selected
  by `rag/factory.py::get_rag_system()`: `gdx_rag.py` (EY GDX slot — plug in when provided),
  `azure_rag.py` (real embeddings + cosine retrieval + grounded LLM synthesis with citations; index
  cached at `data/processed/rag_vector_index.json`), and `keyword_rag.py` (offline fallback).
  `gtx_rag_system.py::GTXRagSystem` is now a thin **facade** over the factory, so the orchestrator,
  API, and chat agent get the selected backend automatically. All backends return the same contract:
  a string, or a dict with `source` / `raw_text_snippet` / `critical_findings` (+ optional `citations`).

- **`llm/azure_client.py`** — the single entry point for Azure OpenAI (`chat()`, `embed()`),
  env-configured and guarded by `is_configured()`. Never call the OpenAI SDK directly elsewhere.

- **`data_ingestion/`** — `synthea_parser.py` flattens Synthea CSVs (`data/raw/`) into
  `data/processed/patient_profiles.json`; `fhir_converter.py` builds a FHIR R4 bundle for the
  export endpoint; `asclepius_ingest.py` generates the mock notes.

### Patient data shape (important gotcha)

Two schemas coexist and code defensively handles both:
- Sample JSON (`data/processed/patient_profile.json`, `all_patients.json`) may wrap the record as
  `{"patient_profile": {...}}` — hence the recurring `patient.get("patient_profile", patient)` pattern.
- Synthea-parsed profiles (`patient_profiles.json`) are flat with `patient_id` / `patient_name` at top level.

Agents read fields like `medical_history` (list of `{condition, status, ...}`, filter on
`status == "Active"`), `medications`, `lab_results`, `encounters`. When adding an agent, follow the
existing dict-in/dict-out contract and register it in `OrchestratorAgent.__init__` and `process_patient`.

## Frontend

`frontend/src/App.jsx` is the stateful root; view components live in `frontend/src/components/`
(Login, Upload, Processing, Results, Header). It talks to the backend via axios at the hardcoded
`API_URL = 'http://127.0.0.1:8000'` and sends the bearer token from login on every request.
