import pandas as pd
import json
import os

def parse_cardiology_from_synthea(csv_dir, output_file):
    """
    Parses massive Synthea CSV files to extract critical cardiovascular biomarkers
    and convert them into our platform's expected JSON RAG structure.
    """
    patients_path = os.path.join(csv_dir, 'patients.csv')
    observations_path = os.path.join(csv_dir, 'observations.csv')
    
    if not os.path.exists(patients_path) or not os.path.exists(observations_path):
        print("Error: Synthea CSV files not found. Please ensure they are downloaded.")
        return

    print("Loading Synthea CSVs (this may take a moment for large datasets)...")
    patients = pd.read_csv(patients_path)
    obs = pd.read_csv(observations_path)

    # LOINC Codes for critical heart failure / cardiac biomarkers
    hf_loinc_codes = {
        '33762-6': 'NT-proBNP',
        '42603-1': 'Troponin_I',
        '2160-0': 'Creatinine',
        '8867-4': 'Heart_Rate',
        '8480-6': 'Systolic_BP',
        '8462-4': 'Diastolic_BP'
    }

    # Filter observations to only include our target biomarkers
    filtered_obs = obs[obs['CODE'].isin(hf_loinc_codes.keys())].copy()
    filtered_obs['BIOMARKER'] = filtered_obs['CODE'].map(hf_loinc_codes)

    # We just want to grab one patient with comprehensive data for the prototype
    # Let's pivot to find a patient who actually has these labs
    pivoted_df = filtered_obs.pivot_table(
        index=['PATIENT', 'DATE'], 
        columns='BIOMARKER', 
        values='VALUE', 
        aggfunc='last'
    ).reset_index()

    # Find a patient row that has at least some cardiac data (e.g., Blood Pressure and Heart Rate)
    valid_patients = pivoted_df.dropna(subset=['Systolic_BP', 'Heart_Rate'])
    
    if valid_patients.empty:
        print("No patients with sufficient cardiac data found in the sample.")
        return
        
    # Take the first valid patient encounter
    target = valid_patients.iloc[0]
    patient_id = target['PATIENT']
    
    # Get demographics
    patient_demo = patients[patients['Id'] == patient_id].iloc[0]
    
    # Construct the JSON in our platform's exact format
    json_profile = {
        "patient_profile": {
            "patient_id": patient_id,
            "name": f"{patient_demo.get('FIRST', 'Unknown')} {patient_demo.get('LAST', 'Unknown')}",
            "gender": patient_demo.get('GENDER', 'Unknown'),
            "ethnicity": patient_demo.get('RACE', 'Unknown')
        },
        "vital_signs": {
            "blood_pressure": f"{target.get('Systolic_BP', '120')}/{target.get('Diastolic_BP', '80')}",
            "heart_rate": target.get('Heart_Rate', 80)
        },
        "lab_results": [],
        "medical_history": [],
        "medications": []
    }
    
    # Add labs if they exist
    if pd.notna(target.get('NT-proBNP')):
        json_profile["lab_results"].append({
            "test_name": "NT-proBNP",
            "value": target['NT-proBNP'],
            "unit": "pg/mL",
            "status": "High" if float(target['NT-proBNP']) > 125 else "Normal"
        })
        
    if pd.notna(target.get('Troponin_I')):
        json_profile["lab_results"].append({
            "test_name": "High-Sensitivity Troponin I",
            "value": target['Troponin_I'],
            "unit": "ng/L",
            "status": "High" if float(target['Troponin_I']) > 14 else "Normal"
        })

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(json_profile, f, indent=2)
        
    print(f"Successfully extracted real Synthea patient {patient_id} into {output_file}")

if __name__ == "__main__":
    csv_dir = "hdds_clinical_intelligence/data/raw/synthea_csv/csv"
    output_file = "hdds_clinical_intelligence/data/processed/synthea_extracted_cardiology.json"
    parse_cardiology_from_synthea(csv_dir, output_file)
