"""
Real upload parsing: turn an uploaded PDF/ZIP into a patient profile.

Pipeline:
  1. Extract raw text from the file (PDF via pypdf; ZIP by reading its text/PDF
     members).
  2. Structure it into diagnoses + medications using Azure Text Analytics for
     Health (extraction/health_nlp.py). If Azure is unavailable, fall back to a
     lightweight local keyword extractor so the feature still works offline.
  3. Assemble a patient-profile dict in the shape the orchestrator expects.

This replaces the old behavior where /api/upload ignored the file contents.
"""

import io
import os
import zipfile
import hashlib

from extraction.health_nlp import extract_entities_from_text

# Minimal local knowledge base used ONLY when Azure Health NLP is not configured.
_LOCAL_CONDITIONS = [
    "atrial fibrillation", "heart failure", "myocardial infarction", "hypertension",
    "type 2 diabetes", "diabetes", "chronic kidney disease", "acute kidney injury",
    "asthma", "copd", "anemia", "stroke", "pneumonia", "sepsis", "hyperlipidemia",
]
_LOCAL_MEDS = [
    "metformin", "lisinopril", "atorvastatin", "aspirin", "apixaban", "metoprolol",
    "amlodipine", "albuterol", "insulin", "warfarin", "furosemide", "losartan",
    "clopidogrel", "rivaroxaban", "carvedilol",
]


# ---------- text extraction ----------
def extract_text(file_path: str, ext: str) -> str:
    ext = ext.lower()
    if ext == ".pdf":
        return _pdf_bytes_to_text(open(file_path, "rb").read(), file_path)
    if ext == ".zip":
        return _zip_to_text(file_path)
    if ext in (".txt", ".md", ".csv", ".json"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""


def _pdf_bytes_to_text(data: bytes, file_path: str = None) -> str:
    text = ""
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
    except ImportError:
        pass
    except Exception as e:
        print(f"pypdf parse error: {e}")
        
    # If pypdf extracts less than 50 characters, it's likely a scanned image/fax
    # Fall back to Azure Document Intelligence (OCR)
    if len(text.strip()) < 50 and file_path:
        from extraction.document_intelligence import extract_text_from_scanned_document
        print("Scanned document detected. Falling back to Azure Document Intelligence OCR...")
        ocr_text = extract_text_from_scanned_document(file_path)
        if ocr_text:
            return ocr_text
            
    return text


def _zip_to_text(file_path: str) -> str:
    parts = []
    try:
        with zipfile.ZipFile(file_path) as z:
            for name in z.namelist():
                low = name.lower()
                if low.endswith("/"):
                    continue
                try:
                    raw = z.read(name)
                except Exception:
                    continue
                    
                file_text = ""
                if low.endswith(".pdf"):
                    # We pass None for file_path because it's a byte stream inside zip
                    file_text = _pdf_bytes_to_text(raw)
                elif low.endswith((".txt", ".md", ".csv", ".json")):
                    file_text = raw.decode("utf-8", errors="ignore")
                    
                if file_text:
                    parts.append(file_text)
                    
                # If this file looks like a radiology report, run Health Insights
                if "xray" in low or "x-ray" in low or "ct" in low or "radiology" in low:
                    from extraction.radiology_insights import analyze_radiology_report
                    insights = analyze_radiology_report(file_text)
                    if insights and insights.get("findings"):
                        # We inject the structured findings directly into the extracted text
                        findings_str = ", ".join([f"{f['finding']} (Confidence: {f['confidence']})" for f in insights["findings"]])
                        parts.append(f"\n[RADIOLOGY INSIGHTS DETECTED: {findings_str}]\n")
                        
    except Exception as e:
        print(f"ZIP parse error: {e}")
    return "\n\n".join(p for p in parts if p)


# ---------- structuring ----------
def _dedupe_titlecase(items):
    seen, out = set(), []
    for it in items:
        key = it.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(it.strip().title())
    return out


def _structure_with_azure(text):
    entities = extract_entities_from_text(text)
    if entities is None:
        return None  # signal: Azure unavailable, caller should use local fallback
    conditions, meds, age, gender = [], [], None, None
    for e in entities:
        cat = (e.get("category") or "").lower()
        val = e.get("text", "")
        if cat in ("diagnosis", "symptomorsign"):
            conditions.append(val)
        elif cat == "medicationname":
            meds.append(val)
        elif cat == "age":
            age = val
        elif cat == "gender":
            gender = val
    return _dedupe_titlecase(conditions), _dedupe_titlecase(meds), age, gender


def _structure_locally(text):
    low = text.lower()
    conditions = [c for c in _LOCAL_CONDITIONS if c in low]
    meds = [m for m in _LOCAL_MEDS if m in low]
    return _dedupe_titlecase(conditions), _dedupe_titlecase(meds), None, None


# ---------- profile assembly ----------
def build_profile_from_file(file_path: str, ext: str, filename: str) -> dict:
    """
    Parse the file and return a profile dict plus extraction metadata:
        {..profile.., "_extraction": {"source", "text_chars", "found_entities"}}
    `found_entities` is False when nothing clinical could be extracted.
    """
    text = extract_text(file_path, ext)

    structured = _structure_with_azure(text)
    if structured is None:
        conditions, meds, age, gender = _structure_locally(text)
        source = "Local keyword extraction (Azure Health NLP not configured)"
    else:
        conditions, meds, age, gender = structured
        source = "Azure Text Analytics for Health"

    pid = "UPLOAD-" + hashlib.sha1((filename + text[:200]).encode("utf-8")).hexdigest()[:8].upper()
    name = os.path.splitext(filename)[0][:60] or "Uploaded Patient"

    profile = {
        "patient_id": pid,
        "patient_name": name,
        "patient_profile": {
            "patient_id": pid,
            "name": name,
            "age": age or "N/A",
            "gender": gender or "N/A",
        },
        "medical_history": [{"condition": c, "status": "Active"} for c in conditions],
        "medications": [
            {"name": m, "dosage": "", "frequency": "", "DESCRIPTION": m} for m in meds
        ],
        "lab_results": [],
        "encounters": [],
        "clinical_text": text[:6000],
        "_extraction": {
            "source": source,
            "text_chars": len(text),
            "found_entities": bool(conditions or meds),
        },
    }
    return profile
