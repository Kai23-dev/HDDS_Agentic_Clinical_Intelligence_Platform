import os

def extract_clinical_entities(patient_id: str):
    """
    Wrapper for Azure Text Analytics for Health.
    If credentials are provided, connects to Azure to extract clinical entities.
    Otherwise, returns None to gracefully fall back to the mock GTX system.
    """
    endpoint = os.getenv("AZURE_LANGUAGE_ENDPOINT")
    key = os.getenv("AZURE_LANGUAGE_KEY")
    
    if not endpoint or not key:
        return None
        
    try:
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.textanalytics import TextAnalyticsClient
        
        # We would typically fetch the real unstructured notes here from a database
        # For prototype, we just pass a mock note snippet based on the Asclepius dataset
        document = [
            "Patient presented with a history of Type 2 Diabetes and Hypertension. "
            "Currently prescribed Metformin 500mg daily. Last HbA1c was 8.1%."
        ]
        
        client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        poller = client.begin_analyze_healthcare_entities(document)
        result = poller.result()
        
        extracted_data = []
        for doc in result:
            if not doc.is_error:
                for entity in doc.entities:
                    extracted_data.append({
                        "text": entity.text,
                        "category": entity.category,
                        "confidence_score": entity.confidence_score
                    })
                    
        return extracted_data
    except Exception as e:
        print(f"Azure Health NLP Error: {e}")
        return None
