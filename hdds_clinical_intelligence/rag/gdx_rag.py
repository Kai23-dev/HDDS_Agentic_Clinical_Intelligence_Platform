"""
GDX RAG backend -- adapter slot for EY's company-built GDX RAG system.

>>> THIS IS A TEMPLATE / PLUG-IN POINT. <<<

When you receive the EY GDX RAG system:
  1. Add its package to requirements.txt (or vendor it under a folder here).
  2. Fill in the TODOs below so GDXRagSystem wraps the real client and returns the
     BaseRAGSystem contract shape.
  3. Set RAG_BACKEND=gdx in .env  (or leave RAG_BACKEND=auto and it will be tried
     first automatically).

Until then, __init__ raises so the factory transparently falls back to the Azure
RAG backup (or keyword fallback). You do NOT need this to be working to ship.
"""

from typing import List, Dict, Any

from rag.base import BaseRAGSystem


class GDXRagSystem(BaseRAGSystem):
    name = "ey-gdx-rag"

    def __init__(self):
        # TODO(EY GDX): import and initialize the real GDX client here, e.g.
        #     from gdx_rag_sdk import GDXClient
        #     self._client = GDXClient(endpoint=os.environ["GDX_ENDPOINT"], ...)
        raise NotImplementedError(
            "EY GDX RAG system not wired up yet. Falling back to the Azure/keyword "
            "backend. See rag/gdx_rag.py to plug it in when available."
        )

    def retrieve(self, patient_id: str, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        # TODO(EY GDX): call the GDX retrieval API and map results to
        #     [{"text": ..., "score": ..., "source": ...}, ...]
        raise NotImplementedError

    def extract_information(self, patient_id: str, query_type: str = "all") -> Any:
        # TODO(EY GDX): call GDX and return either a string (no notes) or a dict:
        #     {"source", "raw_text_snippet", "critical_findings", "citations", "backend"}
        raise NotImplementedError
