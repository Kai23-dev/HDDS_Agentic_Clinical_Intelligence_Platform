"""
Backward-compatible facade for the RAG system.

Historically the orchestrator/API/chat imported `GTXRagSystem` from here. That
still works, but it now delegates to the pluggable backend chosen by
`rag.factory.get_rag_system()` (EY GDX -> Azure RAG -> keyword fallback).

New code should prefer:  from rag import get_rag_system
"""

from rag.factory import get_rag_system


class GTXRagSystem:
    """Thin adapter that forwards to the configured RAG backend."""

    def __init__(self):
        self._backend = get_rag_system()

    def extract_information(self, patient_id, query_type="all"):
        return self._backend.extract_information(patient_id, query_type)

    def retrieve(self, patient_id, query, top_k=4):
        return self._backend.retrieve(patient_id, query, top_k)
