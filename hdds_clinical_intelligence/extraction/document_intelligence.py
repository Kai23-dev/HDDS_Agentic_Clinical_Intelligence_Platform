"""
Azure Document Intelligence (OCR) wrapper.

Provides high-fidelity extraction of text and tables from scanned medical records,
faxes, and complex PDFs where pypdf fails (i.e. image-based PDFs).

Requires: AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT, AZURE_DOCUMENT_INTELLIGENCE_KEY
"""

import os
from typing import Optional

def is_configured() -> bool:
    return bool(os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT") and 
                os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY"))

def extract_text_from_scanned_document(file_path: str) -> Optional[str]:
    """
    Uses Azure Document Intelligence to OCR the file.
    Returns the extracted text, or None if Azure is not configured or fails.
    """
    if not is_configured():
        return None
        
    try:
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        
        endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
        
        client = DocumentIntelligenceClient(
            endpoint=endpoint, 
            credential=AzureKeyCredential(key)
        )
        
        with open(file_path, "rb") as f:
            poller = client.begin_analyze_document(
                "prebuilt-document", 
                analyze_request=f, 
                content_type="application/octet-stream"
            )
            
        result = poller.result()
        
        # Combine all extracted content into a single structured string
        return result.content
        
    except Exception as e:
        print(f"Azure Document Intelligence error: {e}")
        return None
