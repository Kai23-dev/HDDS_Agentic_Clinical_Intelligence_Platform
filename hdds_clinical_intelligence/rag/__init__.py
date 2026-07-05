"""
Pluggable RAG (Retrieval-Augmented Generation) package.

The rest of the app only ever talks to `get_rag_system()` from `rag.factory`,
which returns a concrete backend implementing `BaseRAGSystem`:

    EY GDX RAG   (rag/gdx_rag.py)     -- preferred, if EY provides the module
    Azure RAG    (rag/azure_rag.py)   -- our own real embeddings-based backup
    Keyword RAG  (rag/keyword_rag.py) -- offline fallback, no API keys needed

This lets us drop in the company's GDX RAG system when it arrives without
touching the orchestrator, chat agent, or API.
"""

from rag.base import BaseRAGSystem
from rag.factory import get_rag_system

__all__ = ["BaseRAGSystem", "get_rag_system"]
