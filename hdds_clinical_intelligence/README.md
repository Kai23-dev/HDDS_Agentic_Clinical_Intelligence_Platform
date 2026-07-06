# HDDS Agentic Clinical Intelligence Platform

This is a production-ready, enterprise-grade AI architecture designed to parse, analyze, and generate actionable insights from unstructured clinical patient data. 

> **Responsible-AI note:** synthetic data only; every output is for clinician review, not a final diagnosis or treatment decision.

---

## 🏗️ Enterprise Architecture (Production Ready)

The application has been fully upgraded to a **Single-Container Cloud Deployment** model, utilizing the Microsoft Azure Foundry.

### Core Upgrades
1. **Dockerized Deployment**: The React frontend and FastAPI backend have been unified into a single, highly-efficient `Dockerfile`. This eliminates CORS issues and allows for immediate deployment to **Azure Container Apps**.
2. **Azure AI Search (Vector RAG)**: Replaced local keyword search with state-of-the-art Azure AI Search. Clinical guidelines are mapped to an enterprise-grade vector database, guaranteeing grounded, hallucination-free AI responses.
3. **Azure Blob Storage**: Replaced local file storage with Azure Blob Storage. Uploaded patient documents (PDFs, ZIPs), transcripts, and JSON outputs are now securely synchronized and encrypted at rest in the cloud.
4. **Microsoft AI Integrations**:
    - **Azure Document Intelligence (OCR):** For extracting text from scanned medical PDFs.
    - **Azure Text Analytics for Health:** For deep clinical Named Entity Recognition (NER).
    - **Azure AI Speech:** For real-time doctor dictation and transcription.
    - **Azure OpenAI (GPT-4o):** For secure, HIPAA-compliant intelligence generation.

---

## 🚀 How to Run (Local or Cloud)

### Option 1: The Docker Way (Recommended)
This requires zero dependencies other than Docker Desktop.
```bash
# Build the unified image
docker build -t hdds-app .

# Run the container (maps to localhost:8000)
docker run -p 8000:8000 --env-file .env hdds-app
```
Access the EY Dashboard at: `http://localhost:8000/`

### Option 2: The Developer Way
If you want to run the React dev server and Python backend separately:

**Terminal 1 (Backend):**
```bash
pip install -r requirements.txt
python api.py
```
**Terminal 2 (Frontend):**
```bash
cd frontend
npm install
npm run dev
```

---

## 🧠 The Agentic Pipeline

```text
Upload/Dictation ─► FastAPI ─► OrchestratorAgent ─► RAG Database (Azure AI Search)
                                       │
                                       ▼
                       [7 Sequential Clinical Sub-Agents]
                                       │
                                       ▼
                       outputs/ai_medical_insights.json ─► Azure Blob Storage
```

- **`api.py`** — The unified server. Serves the React Dashboard AND the backend routes (`/api/upload`, `/api/chat`, etc.).
- **`agents/orchestrator_agent.py`** — The brain. Pulls unstructured insights from Azure AI Search and triggers the 7 sub-agents.
- **`rag/azure_search_rag.py`** — The connection to the enterprise Vector Database.

---

## 🔑 Environment Configuration

Copy `.env.example` to `.env` and fill in your Azure credentials. 

**Graceful Degradation:** The platform is designed to be indestructible. If a key is missing (e.g. you don't provide a Speech dictation key), the platform will gracefully disable that specific feature rather than crashing, ensuring the core dashboard always remains functional.
