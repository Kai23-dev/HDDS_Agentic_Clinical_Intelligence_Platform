import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
NOTES_PATH = os.path.join(RAW_DATA_DIR, 'asclepius_notes.json')

class GTXRagSystem:
    def __init__(self):
        self.notes_db = {}
        self._load_notes()

    def _load_notes(self):
        if not os.path.exists(NOTES_PATH):
            print("Warning: Asclepius notes not found. Run asclepius_ingest.py first.")
            return
        
        with open(NOTES_PATH, 'r', encoding='utf-8') as f:
            notes = json.load(f)
            for note in notes:
                # Index by patient_id for simple retrieval
                pid = note.get("patient_id")
                if pid not in self.notes_db:
                    self.notes_db[pid] = []
                self.notes_db[pid].append(note)

    def extract_information(self, patient_id, query_type="all"):
        """
        Simulates a RAG extraction over the unstructured Asclepius notes.
        In a real system, this would use embeddings and an LLM to answer the query.
        """
        patient_notes = self.notes_db.get(patient_id, [])
        if not patient_notes:
            return "No unstructured clinical notes available."

        # Combine all notes for the patient
        full_text = " ".join([n['text'] for n in patient_notes])
        
        # Simple keyword extraction logic for the prototype
        extracted = {
            "source": "asclepius_notes.json (GTX RAG)",
            "raw_text_snippet": full_text
        }
        
        if "cardiology" in full_text.lower() or "infarction" in full_text.lower():
            extracted["critical_findings"] = "High risk of cardiac event. Cardiology follow-up explicitly recommended in notes."
        elif "ketoacidosis" in full_text.lower() or "kidney" in full_text.lower():
            extracted["critical_findings"] = "Patient treated for DKA. Strict glucose monitoring and nephrology follow-up noted."
        else:
            extracted["critical_findings"] = "No critical unstructured findings extracted."
            
        return extracted
