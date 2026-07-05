# HDDS Clinical Intelligence — Application

This is the application package. For the project overview see the
[root README](../README.md). For setup and architecture see
[`SETUP.md`](SETUP.md), [`ROADMAP.md`](ROADMAP.md), and [`CLAUDE.md`](CLAUDE.md).

> **Responsible-AI note:** synthetic data only; every output is for clinician review,
> not a final diagnosis or treatment decision.

---

## Run it

```bash
# from this directory (hdds_clinical_intelligence/)
pip install -r requirements.txt
cp .env.example .env                 # all keys optional; runs offline without them

python data_ingestion/asclepius_ingest.py    # build clinical notes (RAG source)
python api.py                                 # backend  -> http://127.0.0.1:8000

cd frontend && npm install && npm run dev     # frontend -> http://localhost:5173
```

Standalone pipeline (no server), writes `outputs/ai_medical_insights.json`:

```bash
python run_hdds_prototype.py --all            # all sample patients
python run_hdds_prototype.py --patient SYNTH-002
```

> Backend commands must run from this folder (where `api.py` lives), or uvicorn fails
> with "Could not import module api".

---

## How it fits together

```
frontend ─► FastAPI (api.py) ─► OrchestratorAgent ─► RAG backend + 7 sub-agents
                                        │
                                        ▼
                         outputs/ai_medical_insights.json ─► frontend
```

- **`api.py`** — FastAPI app. Routes: `/api/login`, `/api/run-sample`, `/api/load-synthea`,
  `/api/upload`, `/api/insights`, `/api/chat`, `/api/fhir/{patient_id}`. `build_response()`
  runs a patient list through the orchestrator and persists the result.
- **`agents/orchestrator_agent.py`** — the real pipeline. Pulls unstructured insights from the
  RAG system, injects them into the patient dict, then runs the 7 sub-agents in sequence.
- **`agents/*.py`** — each sub-agent is a class with `run()` returning a plain dict.
  `EvidenceValidationAgent` and `FollowupActionAgent` also take the prior agents' outputs.
- **`rag/`** — pluggable RAG (see below). `gtx_rag_system.py` is a thin facade over it.
- **`llm/azure_client.py`** — single Azure OpenAI entry point (chat + embeddings).
- **`data_ingestion/`** — Synthea CSV parser, FHIR R4 converter, notes generator.

---

## RAG backends

Selected at runtime by `rag/factory.py` via the `RAG_BACKEND` env var:

| Backend | File | When used |
|---|---|---|
| **EY GDX** | `rag/gdx_rag.py` | plug in when EY provides it (`RAG_BACKEND=gdx`) |
| **Azure RAG** | `rag/azure_rag.py` | real embeddings + retrieval + cited synthesis (needs `AZURE_OPENAI_*`) |
| **Keyword** | `rag/keyword_rag.py` | offline fallback, no keys |

`auto` (default) tries them in that order. All backends implement `rag/base.py::BaseRAGSystem`
and return the same contract, so nothing downstream changes when you swap them.

---

## Environment

Copy `.env.example` to `.env`. Every key is optional. See [`SETUP.md`](SETUP.md) for details on
`AZURE_OPENAI_*`, `RAG_BACKEND`, `GEMINI_API_KEY`, and the Azure Health NLP keys.

## Sample patients

| ID | Name | Profile |
|----|------|---------|
| SYNTH-001 | John Doe | Type 2 Diabetes, Hypertension |
| SYNTH-002 | Maria Garcia | CHF, AFib, CKD Stage 3 |
| SYNTH-003 | Emily Chen | Asthma, Iron Deficiency Anemia |

## Testing

No automated suite yet (tracked in [`ROADMAP.md`](ROADMAP.md)). Verify changes by running the
pipeline and exercising the API endpoints or the dashboard end-to-end.
