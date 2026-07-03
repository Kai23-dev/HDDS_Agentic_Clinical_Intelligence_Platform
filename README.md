# HDDS Agentic Clinical Intelligence Platform

An enterprise-grade, AI-powered **Hospital Discharge Data Summary (HDDS)** platform designed to automate the extraction, analysis, and summarization of complex patient records. Built using a modern **Multi-Agent Architecture** and **Retrieval-Augmented Generation (RAG)**, this platform assists clinicians by reducing cognitive load, surfacing critical risks, and providing a secure, interactive interface.

---

## 🌟 Key Features

1. **Multi-Agent Architecture**: 
   - An **Orchestrator Agent** dynamically coordinates 6 specialized sub-agents (Clinical Summary, Risk Assessment, Early Detection, Recommendations, Evidence Validation, and Follow-up Actions).
2. **GTX RAG System (Unstructured Data Extraction)**:
   - Simulates advanced NLP extraction (like Azure Health NLP) to pull critical clinical context from messy, unstructured discharge summaries (Asclepius dataset).
3. **Structured Data Harmonization**:
   - Parses and ingests complex patient demographics, labs, and medications from the standard **Synthea** CSV datasets.
4. **Interactive Clinical Assistant (Chatbot)**:
   - A built-in, doctor-style Q&A chatbot that allows clinicians to ask natural language questions about the patient's record (e.g., "What is the patient's HbA1c history?").
5. **Enterprise Security (RBAC)**:
   - **User Authentication** and **Role-Based Access Control (RBAC)** implemented via JWT. Protects sensitive patient data and dynamically alters the UI based on user privileges (e.g., Doctor vs. System Admin).
6. **Human-in-the-Loop (HITL)**:
   - Clinicians maintain full oversight with interactive **Accept / Reject (✓/✕)** validation for AI-generated recommendations and summaries.
7. **Export to PDF**:
   - One-click printer-friendly exports for sharing reports or saving them to external EHR systems.

---

## 🛠️ Technology Stack

- **Backend:** Python, FastAPI (REST API, JWT Authentication)
- **Frontend:** React, Vite, Tailwind CSS, Lucide Icons
- **Data Ingestion:** Custom Python Parsers
- **Datasets:** Synthea (Structured), Asclepius Synthetic Clinical Notes (Unstructured)

---

## 🚀 Getting Started (Local Development)

Follow these instructions to clone and run the platform on your local machine (e.g., your office laptop).

### Prerequisites
- **Python 3.9+**
- **Node.js 18+** & **npm**
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/Kai23-dev/HDDS_Agentic_Clinical_Intelligence_Platform.git
cd HDDS_Agentic_Clinical_Intelligence_Platform
```

### 2. Set up the Backend (FastAPI)
Open a new terminal window:
```bash
# Navigate to the backend directory
cd hdds_clinical_intelligence

# (Optional but recommended) Create and activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies (ensure fastapi, uvicorn, pydantic are installed)
pip install fastapi uvicorn pydantic python-multipart

# Run the FastAPI server
python api.py
```
*The backend will start running at `http://127.0.0.1:8000`*

### 3. Set up the Frontend (React/Vite)
Open a second terminal window:
```bash
# Navigate to the frontend directory
cd hdds_clinical_intelligence/frontend

# Install Node modules
npm install

# Start the development server
npm run dev
```
*The frontend will start running at `http://localhost:5173`*

---

## 🔐 Test Accounts

To access the platform, use one of the following test accounts on the login screen to demonstrate the Role-Based Access Control:

- **Doctor Role:**
  - **Email:** `doctor@ey.com`
  - **Password:** `password123`
  - *Access:* Standard patient dashboard, AI insights, Chatbot.
  
- **Admin Role:**
  - **Email:** `admin@ey.com`
  - **Password:** `admin`
  - *Access:* Standard dashboard + Exclusive "Admin Settings" configuration.

---

## 📁 Project Structure

```text
HDDS_Agentic_Clinical_Intelligence_Platform/
└── hdds_clinical_intelligence/
    ├── agents/                     # The 6 Specialized AI Agents + Orchestrator & Chat Agent
    ├── data/                       # Raw and processed datasets (Synthea & Asclepius)
    ├── data_ingestion/             # Parsers for CSV and unstructured JSON notes
    ├── frontend/                   # React UI (Vite + Tailwind)
    ├── gtx_rag_system.py           # Retrieval-Augmented Generation mock logic
    ├── api.py                      # FastAPI Backend entry point
    └── outputs/                    # AI generated JSON insight files
```

---

## 🔮 Future Roadmap
- [ ] Upgrade mock GTX RAG to use real Vector Embeddings (e.g., Pinecone).
- [ ] Integrate actual LLM APIs (Azure OpenAI / Google Gemini) for the Chatbot.
- [ ] Implement FHIR-compatible data formatting for seamless EHR interoperability.
- [ ] Advanced Patient Comparison dashboard views.

---
*Disclaimer: This is a prototype application built for demonstration purposes. It uses synthetic patient data and rule-based simulated AI models to conserve resources. It is not intended for real clinical diagnosis.*
