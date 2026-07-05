"""
RAG backend selector.

Selection order is controlled by the RAG_BACKEND env var:
    auto     (default) -> try GDX, then Azure, then keyword
    gdx      -> force EY GDX (falls back if it can't initialize)
    azure    -> force Azure RAG (falls back to keyword if not configured)
    keyword  -> force the offline keyword fallback

The selected instance is cached so we don't rebuild the index on every call.
"""

import os

_cached = None


def _try(build, label):
    try:
        inst = build()
        print(f"[RAG] Using backend: {inst.name}")
        return inst
    except Exception as e:
        print(f"[RAG] {label} backend unavailable ({e}).")
        return None


def get_rag_system():
    global _cached
    if _cached is not None:
        return _cached

    backend = os.getenv("RAG_BACKEND", "auto").lower()

    inst = None
    if backend in ("auto", "gdx"):
        from rag.gdx_rag import GDXRagSystem
        inst = _try(GDXRagSystem, "GDX")

    if inst is None and backend in ("auto", "azure"):
        from llm import azure_client
        if azure_client.is_configured():
            from rag.azure_rag import AzureRAGSystem
            inst = _try(AzureRAGSystem, "Azure")
        elif backend == "azure":
            print("[RAG] Azure requested but AZURE_OPENAI_* not set; falling back.")

    if inst is None:
        from rag.keyword_rag import KeywordRAGSystem
        inst = KeywordRAGSystem()
        print(f"[RAG] Using backend: {inst.name}")

    _cached = inst
    return _cached
