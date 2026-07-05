# Roadmap — from prototype to a tool a clinician can rely on

Honest status: the platform is a **well-structured prototype**. The architecture,
workflow, and responsible-AI framing are sound. The clinical *reasoning* is still
mostly rule-based placeholders. The gap below is what stands between a convincing
demo and a product a doctor can trust for treatment support.

## Done (this pass)

- [x] **Pluggable RAG** (`rag/`): swappable backends behind one interface —
      EY GDX slot → Azure RAG (real embeddings + grounded synthesis with citations)
      → keyword fallback. Selected via `RAG_BACKEND`.
- [x] **Azure OpenAI client** (`llm/azure_client.py`): chat + embeddings, env-guarded.
- [x] **Chat agent** now prefers Azure OpenAI, then Gemini, then rules.
- [x] **Reproducibility**: complete `requirements.txt`, full `.env.example`, `SETUP.md`.
- [x] **Bug**: age calculation now uses today's date correctly.

## Done (pass 2)

- [x] **Real authentication** (`auth.py`): signed JWTs with expiry (python-jose) +
      bcrypt-hashed passwords. `verify_token` now validates the signature/expiry
      instead of a string prefix. Frontend unchanged.
- [x] **Real upload parsing** (`data_ingestion/document_parser.py`): `/api/upload`
      now extracts text from the actual PDF/ZIP (pypdf), structures it into
      diagnoses + medications via Azure Health NLP (local keyword fallback), and
      runs the pipeline on it. Falls back to the sample only when nothing can be
      extracted — and says so explicitly instead of pretending.
- [x] **Azure Health NLP wired in** (`extraction/health_nlp.py`): shared helper used
      by the upload parser; activates automatically when AZURE_LANGUAGE_* are set.

## Tier 1 — required before ANY real patient data (safety / legal)

- [ ] **Audit logging.** Record every AI suggestion, who viewed it, and every
      clinician approval/override. Non-negotiable for clinical/regulatory use.
- [ ] **PHI handling.** Encryption at rest, no PHI in logs, and no PHI sent to an LLM
      without an appropriate agreement (BAA / data-residency review).

## Tier 2 — make the clinical output actually accurate

- [ ] **Extract labs + vitals from uploads** too (currently upload parsing captures
      diagnoses + medications; lab values are not yet pulled from free text).
- [ ] **Ground medication & recommendation logic** in a real source instead of
      `if/elif` string matching. Add drug-interaction, allergy, renal-dose, and
      contraindication checks (e.g. RxNorm + OpenFDA). A suggestion with no
      interaction check is unsafe.
- [ ] **Confidence + citation on every output.** The Azure RAG backend already
      returns citations; extend this to the rule-based agents and surface it in the UI.
- [ ] **Enforce human-in-the-loop in the UI.** Nothing is "final" until a clinician
      approves; record the approval.
- [ ] **Validation set + accuracy metrics.** A client will ask "how accurate is it?"
      Build a small clinician-labeled benchmark and report precision/recall per agent.

## Tier 3 — product hardening

- [ ] **Datasets in Azure Blob Storage** instead of the local `data/` folder.
- [ ] **Config over hardcoding** — frontend `API_URL` is hardcoded in `App.jsx`.
- [ ] **Automated tests** — unit tests on each agent's clinical logic; integration
      test on the pipeline. There is no test suite today.
- [ ] **Consolidate the two patient-data schemas** (`patient_profile`-wrapped vs flat).
