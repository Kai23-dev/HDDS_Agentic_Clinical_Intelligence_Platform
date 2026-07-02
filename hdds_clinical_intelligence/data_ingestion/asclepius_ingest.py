import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')

def generate_asclepius_mock_data():
    """
    Generates synthetic discharge summaries mimicking the Asclepius dataset.
    This serves as the unstructured text for the GTX RAG system.
    """
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    
    # We map these to our two Synthea patients: pat-001 and pat-002
    notes = [
        {
            "note_id": "note-101",
            "patient_id": "pat-001",
            "note_type": "Discharge Summary",
            "text": "Patient is a 69-year-old male presenting with acute myocardial infarction. "
                    "He has a history of hypertension and Type 2 diabetes. "
                    "During the hospitalization, patient was started on Lisinopril and Metformin. "
                    "Vitals at discharge: BP 145/90, HR 82. "
                    "HbA1c was noted to be elevated at 8.5%. "
                    "Follow-up with cardiology in 2 weeks is highly recommended due to high risk of re-admission."
        },
        {
            "note_id": "note-102",
            "patient_id": "pat-002",
            "note_type": "Discharge Summary",
            "text": "Patient is a 84-year-old female admitted for diabetic ketoacidosis. "
                    "History of chronic kidney disease stage 3. "
                    "Treated with IV fluids and insulin infusion. Transitioned to Insulin Glargine prior to discharge. "
                    "Latest eGFR is 45 mL/min/1.73m2. "
                    "Patient requires strict glucose monitoring and nephrology follow-up."
        }
    ]
    
    # Save raw notes
    raw_path = os.path.join(RAW_DATA_DIR, 'asclepius_notes.json')
    with open(raw_path, 'w', encoding='utf-8') as f:
        json.dump(notes, f, indent=2)
        
    print(f"Generated {len(notes)} Asclepius mock clinical notes at {raw_path}")
    return raw_path

if __name__ == "__main__":
    generate_asclepius_mock_data()
