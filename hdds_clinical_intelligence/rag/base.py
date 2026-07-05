"""
Common interface every RAG backend must implement.

Keeping this contract stable is what makes the backends swappable. When the EY
GDX RAG system arrives, wrap it in a class that subclasses BaseRAGSystem and the
rest of the platform will pick it up automatically via the factory.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseRAGSystem(ABC):
    """Abstract base for all unstructured-notes retrieval backends."""

    #: Human-readable name of the backend, shown in outputs for traceability.
    name: str = "base"

    @abstractmethod
    def retrieve(self, patient_id: str, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Return the most relevant note chunks for a patient + query.

        Each item is a dict: {"text": str, "score": float, "source": str}.
        Return [] when nothing is available.
        """
        raise NotImplementedError

    @abstractmethod
    def extract_information(self, patient_id: str, query_type: str = "all") -> Any:
        """
        Backward-compatible entry point used by the orchestrator and chat agent.

        MUST return either:
          - a string (when no notes exist), or
          - a dict with keys: source, raw_text_snippet, critical_findings
            (and optionally "citations": [{"text", "score", "source"}, ...]).

        Keeping this shape stable is required -- downstream code checks for the
        "critical_findings" key and reads "raw_text_snippet".
        """
        raise NotImplementedError
