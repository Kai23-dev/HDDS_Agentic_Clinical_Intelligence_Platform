import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

def get_text_analytics_client():
    """
    Initializes the Azure Text Analytics Client using credentials from the .env file.
    """
    endpoint = os.environ.get("AZURE_LANGUAGE_ENDPOINT")
    key = os.environ.get("AZURE_LANGUAGE_KEY")

    if not endpoint or not key:
        raise ValueError("Azure API keys not found. Please set AZURE_LANGUAGE_ENDPOINT and AZURE_LANGUAGE_KEY in your .env file.")

    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint, 
        credential=AzureKeyCredential(key)
    )
    return text_analytics_client

def extract_health_insights(documents: list):
    """
    Calls the Azure Text Analytics for Health API to extract medical entities
    (diagnoses, medications, symptoms) from unstructured clinical text.
    
    Args:
        documents (list): A list of text strings (e.g., ["Patient has a history of AFib and takes Lisinopril."])
    """
    client = get_text_analytics_client()
    
    # We use begin_analyze_healthcare_entities which is the official Azure Health NLP method
    poller = client.begin_analyze_healthcare_entities(documents)
    result = poller.result()
    
    extracted_data = []
    
    for idx, doc_result in enumerate(result):
        if not doc_result.is_error:
            entities = []
            for entity in doc_result.entities:
                entities.append({
                    "text": entity.text,
                    "category": entity.category,
                    "confidence_score": entity.confidence_score
                })
            extracted_data.append(entities)
        else:
            print(f"Error extracting data from document {idx}: {doc_result.error}")
            
    return extracted_data

# --- Example Usage (For Testing) ---
if __name__ == "__main__":
    # To test this, make sure your .env file is set up!
    sample_clinical_text = [
        "The patient is a 68-year-old male presenting with acute decompensated heart failure and atrial fibrillation. He is currently prescribed Apixaban 5mg BID."
    ]
    try:
        insights = extract_health_insights(sample_clinical_text)
        import json
        print(json.dumps(insights, indent=2))
    except Exception as e:
        print(f"Failed to run Azure Health NLP: {e}")
