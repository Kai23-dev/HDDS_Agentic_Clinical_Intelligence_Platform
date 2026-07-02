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
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

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
        if "patient_profile" in patient:
            profile_data = patient["patient_profile"]
        else:
            profile_data = patient
            
        pid = profile_data.get("patient_id", "N/A")
        name = profile_data.get("patient_name", profile_data.get("name", "Unknown"))
        
        # Run through orchestrator
        agent_results = orchestrator.process_patient(profile_data)
        
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


# ---- Routes ----

@app.get("/")
def health_check():
    return {
        "status": "running",
        "project": "HDDS Clinical Intelligence API",
        "version": "2.0.0",
    }


@app.get("/api/insights")
def get_insights():
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
def chat_with_patient(request: ChatRequest):
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
    gtx = GTXRagSystem()
    patient_data["gtx_unstructured_insights"] = gtx.extract_information(request.patient_id)

    agent = ChatbotAgent()
    answer = agent.run(request.question, patient_data)
    
    return {"answer": answer}

@app.post("/api/run-sample")
def run_sample_data():
    """Run the pipeline on the built-in sample patients."""
    with open(SAMPLE_ALL, "r", encoding="utf-8") as f:
        patients = json.load(f)
    if not isinstance(patients, list):
        patients = [patients]
    return build_response(patients)

@app.post("/api/load-synthea")
def load_synthea_data():
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
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a patient document. Accepts:
      - .pdf files (parsed as text, then mapped to profile - prototype)
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    filename = file.filename or "upload"
    ext = os.path.splitext(filename)[1].lower()

    # Save uploaded file
    save_path = os.path.join(UPLOAD_DIR, filename)
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    if ext == ".pdf":
        # For prototype: PDF upload is accepted and saved,
        # but we use Synthea data via Orchestrator to demonstrate the pipeline.
        # In production, this would use Azure Health NLP or similar.
        with open(SAMPLE_SINGLE, "r", encoding="utf-8") as f:
            patient = json.load(f)

        result = build_response([patient])
        result["metadata"]["data_source"] = f"Uploaded PDF: {filename} (prototype - using sample extraction)"
        return result

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Please upload .pdf files only.",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
