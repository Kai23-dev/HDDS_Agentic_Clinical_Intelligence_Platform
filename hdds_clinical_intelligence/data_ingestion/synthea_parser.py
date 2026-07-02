import os
import csv
import json

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')

def read_csv(filename):
    path = os.path.join(RAW_DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def calculate_age(birthdate_str):
    # Simple age calc
    try:
        birth_year = int(birthdate_str.split('-')[0])
        return 2024 - birth_year
    except:
        return 0

def process_synthea_data():
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    
    patients = read_csv('patients.csv')
    conditions = read_csv('conditions.csv')
    medications = read_csv('medications.csv')
    observations = read_csv('observations.csv')
    
    processed_profiles = []
    
    for pat in patients:
        pat_id = pat['Id']
        name = f"{pat.get('FIRST', '')} {pat.get('LAST', '')}".strip()
        
        # 1. Medical History
        pat_conditions = [c for c in conditions if c['PATIENT'] == pat_id]
        medical_history = []
        for c in pat_conditions:
            medical_history.append({
                "condition": c['DESCRIPTION'],
                "status": "Active" if not c.get('STOP') else "Resolved",
                "diagnosis_date": c.get('START', ''),
                "source": "conditions.csv"
            })
            
        # 2. Medications
        pat_meds = [m for m in medications if m['PATIENT'] == pat_id]
        med_list = []
        for m in pat_meds:
            med_list.append({
                "name": m['DESCRIPTION'],
                "dosage": "",
                "frequency": "",
                "status": "Active" if not m.get('STOP') else "Discontinued",
                "prescribed_date": m.get('START', ''),
                "reason": m.get('REASONDESCRIPTION', ''),
                "source": "medications.csv"
            })
            
        # 3. Lab Results
        pat_obs = [o for o in observations if o['PATIENT'] == pat_id]
        lab_results = []
        for o in pat_obs:
            lab_results.append({
                "test_name": o['DESCRIPTION'],
                "value": o['VALUE'],
                "unit": o.get('UNITS', ''),
                "date": o.get('DATE', ''),
                "source": "observations.csv"
            })
            
        profile = {
            "patient_id": pat_id,
            "patient_name": name,
            "demographics": {
                "age": calculate_age(pat.get('BIRTHDATE', '')),
                "gender": pat.get('GENDER', ''),
                "source": "patients.csv"
            },
            "medical_history": medical_history,
            "medications": med_list,
            "lab_results": lab_results
        }
        processed_profiles.append(profile)
        
    # Write output
    output_path = os.path.join(PROCESSED_DATA_DIR, 'patient_profiles.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({"patients": processed_profiles}, f, indent=2)
        
    print(f"Successfully processed {len(processed_profiles)} patients from Synthea CSVs.")
    return output_path

if __name__ == "__main__":
    process_synthea_data()
