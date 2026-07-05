# Setup — running this on another machine (e.g. the company laptop)

This project is self-contained. After cloning it runs **offline** with rule-based
agents and a keyword RAG fallback; adding Azure credentials upgrades it to real
LLM chat and real embeddings-based RAG. No code changes are needed between machines.

## 1. Clone and enter the project

```bash
git clone https://github.com/Kai23-dev/HDDS_Agentic_Clinical_Intelligence_Platform.git
cd HDDS_Agentic_Clinical_Intelligence_Platform/hdds_clinical_intelligence
```

> Always run backend commands from `hdds_clinical_intelligence/` (the folder with `api.py`).

## 2. Python backend

```bash
python -m venv .venv
source .venv/Scripts/activate        # Git Bash on Windows
# .venv\Scripts\activate            # PowerShell
pip install -r requirements.txt
```

## 3. Configure environment

```bash
cp .env.example .env
```

Fill in `.env`. On the company laptop, set the **Azure OpenAI** block to enable the
real chat + RAG (see `.env.example` for each variable). Leave everything blank to
run fully offline.

## 4. Generate data + run

```bash
python data_ingestion/asclepius_ingest.py     # build mock clinical notes (RAG source)
python data_ingestion/synthea_parser.py       # (optional) build profiles from Synthea CSVs
python run_hdds_prototype.py --all             # generate outputs/ai_medical_insights.json

python api.py                                  # backend  -> http://127.0.0.1:8000
# in a second terminal:
cd frontend && npm install && npm run dev      # frontend -> http://localhost:5173
```

## 5. Verify which RAG backend is active

On startup the logs print the selected backend:

```
[RAG] Using backend: azure-rag          # Azure creds present
[RAG] Using backend: keyword-fallback   # no creds -> offline mode
[RAG] Using backend: ey-gdx-rag         # EY GDX wired in
```

## Azure deployment notes

- **Models:** create deployments in Azure OpenAI Studio and put the *deployment
  names* (not model names) in `AZURE_OPENAI_CHAT_DEPLOYMENT` /
  `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`.
- **Datasets in Azure:** raw notes/CSVs currently live under `data/`. To move them
  to Azure Blob Storage, add a small loader that pulls the blobs into `data/` at
  startup (or read them directly). This is tracked in `ROADMAP.md`.
- **Secrets:** never commit `.env`. On Azure App Service set these as Application
  Settings; ideally back them with Azure Key Vault.
- **The EY GDX RAG system:** when you receive it, wire it into `rag/gdx_rag.py`
  and set `RAG_BACKEND=gdx`. Nothing else needs to change — see that file's TODOs.
