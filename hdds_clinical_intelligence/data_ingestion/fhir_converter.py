import uuid
import datetime

def convert_to_fhir_bundle(patient_data: dict, insights_data: dict = None) -> dict:
    """
    Converts internal HDDS patient JSON into an HL7 FHIR R4 Bundle.
    """
    
    # Extract raw data
    if "patient_profile" in patient_data:
        profile = patient_data["patient_profile"]
    else:
        profile = patient_data
        
    pid = profile.get("patient_id", str(uuid.uuid4()))
    name_str = profile.get("patient_name", profile.get("name", "Unknown"))
    
    # Parse name for FHIR
    name_parts = name_str.split(" ")
    family = name_parts[-1] if len(name_parts) > 1 else name_str
    given = name_parts[:-1] if len(name_parts) > 1 else [name_str]

    bundle = {
        "resourceType": "Bundle",
        "id": str(uuid.uuid4()),
        "type": "collection",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "entry": []
    }
    
    # 1. Patient Resource
    patient_resource = {
        "fullUrl": f"urn:uuid:{pid}",
        "resource": {
            "resourceType": "Patient",
            "id": pid,
            "name": [{"family": family, "given": given}],
            "gender": profile.get("gender", "unknown").lower(),
            "birthDate": profile.get("dob", "1900-01-01")
        }
    }
    bundle["entry"].append(patient_resource)

    # 2. Condition Resources (Active Conditions)
    if insights_data and "agent_results" in insights_data:
        ar = insights_data["agent_results"]
        
        # Add conditions
        conditions = ar.get("clinical_summary", {}).get("active_conditions", [])
        for cond in conditions:
            cond_id = str(uuid.uuid4())
            bundle["entry"].append({
                "fullUrl": f"urn:uuid:{cond_id}",
                "resource": {
                    "resourceType": "Condition",
                    "id": cond_id,
                    "clinicalStatus": {
                        "coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]
                    },
                    "code": {
                        "text": cond
                    },
                    "subject": {
                        "reference": f"urn:uuid:{pid}"
                    }
                }
            })
            
        # 3. MedicationRequest Resources
        meds = ar.get("clinical_summary", {}).get("current_medications", [])
        for med in meds:
            med_id = str(uuid.uuid4())
            bundle["entry"].append({
                "fullUrl": f"urn:uuid:{med_id}",
                "resource": {
                    "resourceType": "MedicationRequest",
                    "id": med_id,
                    "status": "active",
                    "intent": "order",
                    "medicationCodeableConcept": {
                        "text": med
                    },
                    "subject": {
                        "reference": f"urn:uuid:{pid}"
                    }
                }
            })
            
        # 4. Observation Resources (Abnormal Labs)
        labs = ar.get("early_detection", {}).get("flagged_abnormal_results", [])
        for lab in labs:
            lab_id = str(uuid.uuid4())
            bundle["entry"].append({
                "fullUrl": f"urn:uuid:{lab_id}",
                "resource": {
                    "resourceType": "Observation",
                    "id": lab_id,
                    "status": "final",
                    "code": {
                        "text": lab.get("test_name", "Unknown Test")
                    },
                    "subject": {
                        "reference": f"urn:uuid:{pid}"
                    },
                    "valueQuantity": {
                        "value": float(lab.get("value", 0)) if str(lab.get("value")).replace('.','',1).isdigit() else 0,
                        "unit": lab.get("unit", "")
                    },
                    "interpretation": [
                        {
                            "text": lab.get("status", "Abnormal")
                        }
                    ]
                }
            })

    return bundle
