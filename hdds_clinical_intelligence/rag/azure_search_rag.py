"""
Azure AI Search RAG backend.

This provides an enterprise-grade retrieval-augmented generation pipeline using
a true Vector Database (Azure AI Search) instead of local flat files.

    1. Splits patient clinical notes into chunks.
    2. Embeds chunks with Azure OpenAI embeddings.
    3. Uploads documents to an Azure AI Search index.
    4. On a query, embeds the query and performs a Vector Search.
    5. Synthesizes an answer with the Azure OpenAI chat model.

Requires: AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY, AZURE_SEARCH_INDEX_NAME
"""

import os
import hashlib
from typing import List, Dict, Any

from rag.base import BaseRAGSystem
from rag.notes_loader import load_notes_by_patient
from llm import azure_client

try:
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchIndex,
        SimpleField,
        SearchableField,
        SearchField,
        SearchFieldDataType,
        VectorSearch,
        HnswAlgorithmConfiguration,
        VectorSearchProfile,
    )
    AZURE_SEARCH_AVAILABLE = True
except ImportError:
    AZURE_SEARCH_AVAILABLE = False

CHUNK_CHARS = 700

def _chunk(text: str) -> List[str]:
    text = text.strip()
    if len(text) <= CHUNK_CHARS:
        return [text] if text else []
    return [text[i:i + CHUNK_CHARS] for i in range(0, len(text), CHUNK_CHARS)]

def is_configured() -> bool:
    return bool(
        AZURE_SEARCH_AVAILABLE and
        os.getenv("AZURE_SEARCH_ENDPOINT") and
        os.getenv("AZURE_SEARCH_KEY") and
        os.getenv("AZURE_SEARCH_INDEX_NAME")
    )

class AzureSearchRAGSystem(BaseRAGSystem):
    name = "azure_search"

    def __init__(self):
        if not is_configured():
            raise RuntimeError("Azure AI Search is not configured properly.")
            
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.key = os.getenv("AZURE_SEARCH_KEY")
        self.index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "hdds-clinical-index")
        self.credential = AzureKeyCredential(self.key)
        
        self.search_client = SearchClient(endpoint=self.endpoint, index_name=self.index_name, credential=self.credential)
        self.index_client = SearchIndexClient(endpoint=self.endpoint, credential=self.credential)
        
        self.notes_db = load_notes_by_patient()
        self._ensure_index_exists()

    def _ensure_index_exists(self):
        """Create the Azure Search index if it doesn't already exist."""
        try:
            self.index_client.get_index(self.index_name)
        except Exception as e:
            if "404" in str(e):
                print(f"Creating Azure AI Search index: {self.index_name}")
                fields = [
                    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                    SimpleField(name="patient_id", type=SearchFieldDataType.String, filterable=True),
                    SimpleField(name="source_type", type=SearchFieldDataType.String, filterable=True),
                    SimpleField(name="source_file", type=SearchFieldDataType.String),
                    SimpleField(name="section", type=SearchFieldDataType.String),
                    SearchableField(name="content", type=SearchFieldDataType.String),
                    SearchField(name="embedding", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                                searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile")
                ]
                
                vector_search = VectorSearch(
                    algorithms=[HnswAlgorithmConfiguration(name="myHnsw")],
                    profiles=[VectorSearchProfile(name="myHnswProfile", algorithm_configuration_name="myHnsw")]
                )
                
                index = SearchIndex(name=self.index_name, fields=fields, vector_search=vector_search)
                self.index_client.create_index(index)
            else:
                print(f"Error checking index: {e}")

    def _ensure_embedded(self, patient_id: str):
        """Index chunks for a patient. In production, this would be an async background task."""
        # Check if patient already exists in the index
        try:
            results = self.search_client.search(search_text="*", filter=f"patient_id eq '{patient_id}'", top=1)
            if any(results):
                return  # Already indexed
        except Exception as e:
            print(f"Search error during check: {e}")
            return
            
        print(f"Indexing clinical notes for patient {patient_id} into Azure AI Search...")
        docs_to_upload = []
        for note in self.notes_db.get(patient_id, []):
            for piece in _chunk(note.get("text", "")):
                doc_id = hashlib.sha256(f"{patient_id}_{piece}".encode("utf-8")).hexdigest()
                try:
                    vec = azure_client.embed([piece])[0]
                    docs_to_upload.append({
                        "id": doc_id,
                        "patient_id": patient_id,
                        "source_type": "clinical_note",
                        "source_file": "asclepius_notes.json",
                        "section": "general",
                        "content": piece,
                        "embedding": vec
                    })
                except Exception as e:
                    print(f"Embedding error: {e}")
                    
        if docs_to_upload:
            try:
                self.search_client.upload_documents(documents=docs_to_upload)
                print(f"Successfully uploaded {len(docs_to_upload)} chunks to Azure Search.")
            except Exception as e:
                print(f"Upload error: {e}")

    def retrieve(self, patient_id: str, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        self._ensure_embedded(patient_id)
        try:
            q_vec = azure_client.embed([query])[0]
            from azure.search.documents.models import VectorizedQuery
            vector_query = VectorizedQuery(vector=q_vec, k_nearest_neighbors=top_k, fields="embedding")
            
            results = self.search_client.search(
                search_text=None,
                vector_queries=[vector_query],
                filter=f"patient_id eq '{patient_id}'",
                top=top_k
            )
            
            scored = []
            for result in results:
                scored.append({
                    "text": result["content"],
                    "score": result["@search.score"],
                    "source": result["source_file"]
                })
            return scored
        except Exception as e:
            print(f"Retrieve error: {e}")
            return []

    def extract_information(self, patient_id: str, query_type: str = "all") -> Any:
        notes = self.notes_db.get(patient_id, [])
        if not notes:
            return "No unstructured clinical notes available."

        query = ("Summarize the most critical clinical findings, risks, and any "
                 "recommended follow-up for this patient.")
        top = self.retrieve(patient_id, query, top_k=4)
        full_text = " ".join(n["text"] for n in notes)

        if not top:
            return {
                "source": f"asclepius_notes.json ({self.name})",
                "raw_text_snippet": full_text[:500] + "...",
                "critical_findings": "No critical findings extracted.",
                "citations": [],
                "backend": self.name,
            }

        context = "\n\n".join(f"[{i+1}] {c['text']}" for i, c in enumerate(top))
        messages = [
            {"role": "system", "content": (
                "You are a clinical evidence extraction assistant for a doctor-review tool. "
                "Using ONLY the provided note excerpts, state the most critical findings, "
                "risks, and recommended follow-up in 1-3 sentences. Cite excerpt numbers like "
                "[1]. If the excerpts do not support a finding, say so. Do not invent facts. "
                "This is decision support for clinician review, not a diagnosis.")},
            {"role": "user", "content": f"NOTE EXCERPTS:\n{context}\n\nQUESTION: {query}"},
        ]
        
        try:
            critical = azure_client.chat(messages, temperature=0.1, max_tokens=300).strip()
        except Exception as e:
            print(f"AzureSearchRAG synthesis failed, using excerpt fallback: {e}")
            critical = top[0]["text"][:300] if top else "No critical findings extracted."

        return {
            "source": f"asclepius_notes.json ({self.name})",
            "raw_text_snippet": full_text[:500] + "...",
            "critical_findings": critical,
            "citations": top,
            "backend": self.name,
        }
