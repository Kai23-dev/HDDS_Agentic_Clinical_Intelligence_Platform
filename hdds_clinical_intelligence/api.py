"""
HDDS Clinical Intelligence Platform - FastAPI Backend
=====================================================
Serves the AI agent pipeline results and handles file uploads.

Endpoints:
    GET  /                  Health check
    GET  /api/insights      Returns the latest generated insights
    POST /api/upload        Upload patient documents (PDF/JSON) and run pipeline
    POST /api/run-sample    Run pipeline on built-in sample data
"""

import json
import os
import sys
import shutil
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, Path
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables (API keys)
load_dotenv()

# Make sure agents are importable
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from agents.clinical_summary_agent import ClinicalSummaryAgent
from agents.risk_assessment_agent import RiskAssessmentAgent
from agents.early_detection_agent import EarlyDetectionAgent
from agents.recommendation_agent import RecommendationAgent
from agents.evidence_validation_agent import EvidenceValidationAgent
from agents.followup_action_agent import FollowupActionAgent


app = FastAPI(
    title="HDDS Clinical Intelligence API",
    description="Backend for the Hospital Discharge Data Summary platform",
    version="2.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs")
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "ai_medical_insights.json")
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads")
SAMPLE_SINGLE = os.path.join(PROJECT_ROOT, "data", "processed", "patient_profile.json")
SAMPLE_ALL = os.path.join(PROJECT_ROOT, "data", "processed", "all_patients.json")

RESPONSIBLE_AI_NOTE = (
    "This output is generated for prototype purposes only and is intended for "
    "clinician review. It is not a final diagnosis or treatment decision."
)


from agents.orchestrator_agent import OrchestratorAgent

def build_response(patients_data: list) -> dict:
    """Process a list of patients and build the final response via Orchestrator."""
    results = []
    orchestrator = OrchestratorAgent()
    
    for patient in patients_data:
        # Some sample data formats wrap the patient in "patient_profile"
        profile_data = patient.get("patient_profile", patient)
            
        pid = profile_data.get("patient_id", "N/A")
        name = profile_data.get("patient_name", profile_data.get("name", "Unknown"))
        
        # Run through orchestrator using the FULL patient object
        agent_results = orchestrator.process_patient(patient)
        
        results.append({
            "patient_id": pid,
            "patient_name": name,
            "agent_results": agent_results,
        })

    output = {
        "metadata": {
            "project": "HDDS Agentic Clinical Intelligence Platform",
            "version": "3.0.0-orchestrator",
            "generated_at": datetime.now().isoformat(),
            "data_source": "Synthea & Asclepius (GTX RAG)",
            "total_patients_processed": len(results),
            "responsible_ai_note": RESPONSIBLE_AI_NOTE,
        },
        "patients": results,
    }

    # Also save to file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return output


# ---- Security / Auth ----
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from pydantic import BaseModel

security = HTTPBearer()

from auth import hash_password, verify_password, create_access_token, decode_access_token

# Demo user store. Passwords are bcrypt-hashed at startup (never stored in plaintext).
# In production this becomes a real user database; the shape stays the same.
USERS = {
    "doctor@ey.com": {"password_hash": hash_password("password123"), "role": "doctor", "name": "Dr. Smith"},
    "admin@ey.com": {"password_hash": hash_password("admin"), "role": "admin", "name": "System Admin"},
}

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/login")
def login(request: LoginRequest):
    user = USERS.get(request.email)
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": request.email,
        "role": user["role"],
        "name": user["name"],
    })
    return {"access_token": token, "role": user["role"], "name": user["name"]}

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate the signed JWT and return its claims (dict). 401 if invalid/expired."""
    from jose import JWTError
    try:
        return decode_access_token(credentials.credentials)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ---- Routes ----

@app.get("/")
def health_check():
    return {
        "status": "running",
        "project": "HDDS Clinical Intelligence API",
        "version": "2.0.0",
    }

@app.get("/api/insights")
def get_insights(token: str = Depends(verify_token)):
    """Return the latest generated insights."""
    if not os.path.exists(OUTPUT_JSON):
        raise HTTPException(
            status_code=404,
            detail="No insights generated yet. Upload documents or run sample data first.",
        )
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

from pydantic import BaseModel
class ChatRequest(BaseModel):
    patient_id: str
    question: str

@app.post("/api/chat")
def chat_with_patient(request: ChatRequest, token: str = Depends(verify_token)):
    """Chat with a specific patient's data."""
    if not os.path.exists(OUTPUT_JSON):
        raise HTTPException(status_code=404, detail="No patient data loaded.")
        
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        insights_data = json.load(f)
        
    # Try to find the patient in the processed Synthea profiles or sample data
    from data_ingestion.synthea_parser import process_synthea_data
    from agents.chat_agent import ChatbotAgent
    
    profiles = []
    patients_file = os.path.join(PROJECT_ROOT, "data", "processed", "patient_profiles.json")
    if os.path.exists(patients_file):
        with open(patients_file, "r", encoding="utf-8") as f:
            profiles = json.load(f).get("patients", [])
            
    if not profiles:
        # Fallback to sample data
        if os.path.exists(SAMPLE_ALL):
            with open(SAMPLE_ALL, "r", encoding="utf-8") as f:
                data = json.load(f)
                profiles = data if isinstance(data, list) else [data]
                # Some sample data wraps patient inside "patient_profile"
                profiles = [p.get("patient_profile", p) for p in profiles]
        
    patient_data = next((p for p in profiles if p.get("patient_id") == request.patient_id), None)
    
    if not patient_data:
        # Fallback to single sample
        if os.path.exists(SAMPLE_SINGLE):
            with open(SAMPLE_SINGLE, "r", encoding="utf-8") as f:
                p = json.load(f)
                p = p.get("patient_profile", p)
                if p.get("patient_id") == request.patient_id:
                    patient_data = p

    if not patient_data:
        raise HTTPException(status_code=404, detail=f"Patient {request.patient_id} not found in loaded datasets.")
        
    # Inject GTX notes for the chat agent
    from gtx_rag_system import GTXRagSystem
    # Optional Azure NLP integration
    try:
        from extraction.azure_health_nlp import extract_clinical_entities
        azure_results = extract_clinical_entities(request.patient_id)
        if azure_results:
            patient_data["azure_nlp_insights"] = azure_results
    except Exception:
        pass

    gtx = GTXRagSystem()
    patient_data["gtx_unstructured_insights"] = gtx.extract_information(request.patient_id)

    agent = ChatbotAgent()
    answer = agent.run(request.question, patient_data)
    
    return {"answer": answer}

@app.get("/api/fhir/{patient_id}")
def get_fhir_data(patient_id: str, token: str = Depends(verify_token)):
    """Export patient data as a standard FHIR R4 Bundle."""
    if not os.path.exists(OUTPUT_JSON):
        raise HTTPException(status_code=404, detail="No patient data loaded.")
        
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        insights_data = json.load(f)
        
    # Find patient insights
    p_insights = next((p for p in insights_data.get("patients", []) if p["patient_id"] == patient_id), None)
    
    # Try to load raw profile
    patients_file = os.path.join(PROJECT_ROOT, "data", "processed", "patient_profiles.json")
    raw_profile = {}
    if os.path.exists(patients_file):
        with open(patients_file, "r", encoding="utf-8") as f:
            profiles = json.load(f).get("patients", [])
            raw_profile = next((p for p in profiles if p.get("patient_id") == patient_id), {})
            
    if not raw_profile and os.path.exists(SAMPLE_ALL):
        with open(SAMPLE_ALL, "r", encoding="utf-8") as f:
            data = json.load(f)
            profiles = data if isinstance(data, list) else [data]
            raw_profile = next((p.get("patient_profile", p) for p in profiles if p.get("patient_id") == patient_id or p.get("patient_profile", {}).get("patient_id") == patient_id), {})

    if not p_insights and not raw_profile:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found.")
        
    from data_ingestion.fhir_converter import convert_to_fhir_bundle
    fhir_bundle = convert_to_fhir_bundle(raw_profile, p_insights)
    
    return fhir_bundle

@app.post("/api/run-sample")
def run_sample_data(token: str = Depends(verify_token)):
    """Run the pipeline on the built-in sample patients."""
    with open(SAMPLE_ALL, "r", encoding="utf-8") as f:
        patients = json.load(f)
    if not isinstance(patients, list):
        patients = [patients]
    return build_response(patients)

@app.post("/api/load-synthea")
def load_synthea_data(token: str = Depends(verify_token)):
    """Run the pipeline on the parsed Synthea dataset."""
    from data_ingestion.synthea_parser import process_synthea_data
    output_path = process_synthea_data()
    with open(output_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    patients = data.get("patients", [])
    if not patients:
        raise HTTPException(status_code=400, detail="No patients found in Synthea data.")
    return build_response(patients)

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), token: str = Depends(verify_token)):
    """
    Upload a patient document. Accepts:
      - .pdf files (parsed as text, then mapped to profile)
      - .zip files (multi-modal bundle: ECG, Labs, Notes)
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    filename = file.filename or "upload"
    ext = os.path.splitext(filename)[1].lower()

    # Save uploaded file
    save_path = os.path.join(UPLOAD_DIR, filename)
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    if ext not in [".pdf", ".zip"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Please upload .pdf or .zip files.",
        )

    # Parse the ACTUAL uploaded content into a patient profile.
    from data_ingestion.document_parser import build_profile_from_file
    profile = build_profile_from_file(save_path, ext, filename)
    extraction = profile.pop("_extraction", {})

    if not extraction.get("found_entities"):
        # Nothing clinical could be extracted (e.g. scanned/empty PDF, no NLP).
        # Fall back to the sample profile but say so explicitly -- never pretend.
        with open(SAMPLE_SINGLE, "r", encoding="utf-8") as f:
            profile = json.load(f)
        result = build_response([profile])
        result["metadata"]["data_source"] = (
            f"Uploaded {filename}: no clinical entities extracted "
            f"({extraction.get('text_chars', 0)} chars read) -- showing sample profile for review."
        )
        result["metadata"]["extraction"] = extraction
        return result

    result = build_response([profile])
    data_type = "Multi-Modal ZIP Bundle" if ext == ".zip" else "PDF Document"
    result["metadata"]["data_source"] = (
        f"Uploaded {data_type}: {filename} (parsed via {extraction.get('source')})"
    )
    result["metadata"]["extraction"] = extraction
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
