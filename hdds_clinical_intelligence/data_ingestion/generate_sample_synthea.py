import os
import csv
from datetime import datetime

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')

def ensure_dir():
    if not os.path.exists(RAW_DATA_DIR):
        os.makedirs(RAW_DATA_DIR)

def write_csv(filename, fieldnames, rows):
    path = os.path.join(RAW_DATA_DIR, filename)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {filename}")

def generate_synthea_data():
    ensure_dir()
    
    # Patients
    patients = [
        {
            "Id": "pat-001", "BIRTHDATE": "1955-03-12", "FIRST": "John", "LAST": "Smith",
            "GENDER": "M", "RACE": "white", "ETHNICITY": "nonhispanic", "CITY": "Boston"
        },
        {
            "Id": "pat-002", "BIRTHDATE": "1940-11-20", "FIRST": "Maria", "LAST": "Garcia",
            "GENDER": "F", "RACE": "white", "ETHNICITY": "hispanic", "CITY": "Cambridge"
        }
    ]
    write_csv('patients.csv', list(patients[0].keys()), patients)
    
    # Encounters
    encounters = [
        {"Id": "enc-001", "PATIENT": "pat-001", "START": "2023-10-01", "ENCOUNTERCLASS": "inpatient", "REASONDESCRIPTION": "Acute myocardial infarction"},
        {"Id": "enc-002", "PATIENT": "pat-002", "START": "2023-10-10", "ENCOUNTERCLASS": "inpatient", "REASONDESCRIPTION": "Diabetic ketoacidosis"}
    ]
    write_csv('encounters.csv', list(encounters[0].keys()), encounters)
    
    # Conditions
    conditions = [
        {"START": "2015-01-10", "PATIENT": "pat-001", "ENCOUNTER": "enc-001", "DESCRIPTION": "Hypertension"},
        {"START": "2018-05-22", "PATIENT": "pat-001", "ENCOUNTER": "enc-001", "DESCRIPTION": "Type 2 Diabetes Mellitus"},
        {"START": "2020-03-15", "PATIENT": "pat-002", "ENCOUNTER": "enc-002", "DESCRIPTION": "Chronic Kidney Disease"}
    ]
    write_csv('conditions.csv', list(conditions[0].keys()), conditions)
    
    # Medications
    medications = [
        {"START": "2023-10-01", "PATIENT": "pat-001", "ENCOUNTER": "enc-001", "DESCRIPTION": "Metformin 500mg", "REASONDESCRIPTION": "Type 2 Diabetes Mellitus"},
        {"START": "2023-10-01", "PATIENT": "pat-001", "ENCOUNTER": "enc-001", "DESCRIPTION": "Lisinopril 10mg", "REASONDESCRIPTION": "Hypertension"},
        {"START": "2023-10-10", "PATIENT": "pat-002", "ENCOUNTER": "enc-002", "DESCRIPTION": "Insulin Glargine 100u/mL", "REASONDESCRIPTION": "Diabetes"}
    ]
    write_csv('medications.csv', list(medications[0].keys()), medications)
    
    # Observations
    observations = [
        {"DATE": "2023-10-02", "PATIENT": "pat-001", "ENCOUNTER": "enc-001", "DESCRIPTION": "Hemoglobin A1c", "VALUE": "8.5", "UNITS": "%"},
        {"DATE": "2023-10-02", "PATIENT": "pat-001", "ENCOUNTER": "enc-001", "DESCRIPTION": "Systolic Blood Pressure", "VALUE": "145", "UNITS": "mmHg"},
        {"DATE": "2023-10-11", "PATIENT": "pat-002", "ENCOUNTER": "enc-002", "DESCRIPTION": "eGFR", "VALUE": "45", "UNITS": "mL/min/1.73m2"}
    ]
    write_csv('observations.csv', list(observations[0].keys()), observations)

    # Procedures
    procedures = [
        {"DATE": "2023-10-01", "PATIENT": "pat-001", "ENCOUNTER": "enc-001", "DESCRIPTION": "Electrocardiogram"},
        {"DATE": "2023-10-10", "PATIENT": "pat-002", "ENCOUNTER": "enc-002", "DESCRIPTION": "Dialysis Access Placement"}
    ]
    write_csv('procedures.csv', list(procedures[0].keys()), procedures)

if __name__ == "__main__":
    generate_synthea_data()
